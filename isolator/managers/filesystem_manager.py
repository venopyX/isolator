import os
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import List, Dict
from ..config import IsolationConfig
from .requirements_manager import RequirementsManager

class FilesystemManager:
    """Enhanced filesystem manager with profile-based isolation."""

    def __init__(self, config: IsolationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_dirs: List[Path] = []
        self.user_runtime_dir = os.path.join('/run/user', str(os.getuid()))
        self.requirements_manager = RequirementsManager()

    def _create_temp_dirs(self) -> List[Path]:
        """Create temporary directories for isolation."""
        temp_dirs = []
        if self.config.tmp_dir:
            temp_dirs.append(Path(self.config.tmp_dir))
        else:
            temp_dir = Path(tempfile.mkdtemp())
            temp_dirs.append(temp_dir)
            self.logger.debug(f"Created temporary directory: {temp_dir}")
        return temp_dirs

    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
                self.logger.debug(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")

    def resolve_command(self, command: List[str]) -> List[str]:
        """Resolve command path and return full command with arguments."""
        if not command:
            raise ValueError("Empty command provided")

        # Try to find the binary in common locations
        binary_name = command[0]
        if not os.path.isabs(binary_name):
            # First try which command
            try:
                full_path = subprocess.check_output(["which", binary_name]).decode().strip()
                self.logger.debug(f"Found binary using which: {full_path}")
                return [full_path] + command[1:]
            except subprocess.CalledProcessError:
                self.logger.debug(f"Binary not found using which: {binary_name}")

            # Search in common locations
            search_paths = [
                "/usr/bin",
                "/usr/local/bin",
                "/opt",
                "/usr/lib",
                "/usr/lib64",
                "/usr/share",
                "/usr/local/lib",
            ]

            # Try both direct path and subdirectories
            for path in search_paths:
                # Try direct path
                full_path = os.path.join(path, binary_name)
                if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                    self.logger.debug(f"Found binary in {path}: {full_path}")
                    return [full_path] + command[1:]

                # Search in subdirectories
                if os.path.exists(path):
                    for root, _, files in os.walk(path, followlinks=True):
                        if binary_name in files:
                            full_path = os.path.join(root, binary_name)
                            if os.access(full_path, os.X_OK):
                                self.logger.debug(f"Found binary in subdirectory: {full_path}")
                                return [full_path] + command[1:]

            self.logger.warning(f"Binary not found in common locations: {binary_name}")

        # If we reach here, use the command as is
        return command

    def setup(self) -> List[str]:
        """Set up filesystem isolation and return bubblewrap arguments."""
        args = []
        
        # Create temporary directories
        self.temp_dirs = self._create_temp_dirs()
        
        # Essential system paths for binary execution (order matters)
        essential_paths = [
            # First mount the core system directories
            ("/proc", "/proc"),  # Must be first for /proc/self/fd
            ("/sys", "/sys"),   # Hardware and device information
            
            # Then mount system binaries and libraries
            ("/usr", "/usr"),
            ("/bin", "/bin"),
            ("/sbin", "/sbin"),
            ("/lib", "/lib"),
            ("/lib64", "/lib64"),
            
            # Additional system directories
            ("/etc", "/etc"),    # Configuration files
            ("/opt", "/opt"),    # Optional packages
            ("/var", "/var"),    # Variable data
            
            # Home directory for user data
            (os.path.expanduser("~"), os.path.expanduser("~")),  # User's home
        ]

        # Mount essential paths
        for src, dest in essential_paths:
            if os.path.exists(src):
                args.extend(["--ro-bind", src, dest])
                self.logger.debug(f"Mounted {src} to {dest}")
            else:
                self.logger.debug(f"Path not found: {src}")

        # Set up /dev with necessary permissions
        args.extend([
            "--dev-bind", "/dev", "/dev",  # Full device access with original permissions
        ])

        # Ensure specific device nodes are accessible
        for dev in ["/dev/null", "/dev/zero", "/dev/random", "/dev/urandom"]:
            if os.path.exists(dev):
                args.extend(["--dev-bind", dev, dev])

        # Add common binary locations and application-specific paths
        extra_paths = [
            # Common binary and library locations
            "/usr/local/bin",
            "/usr/local/sbin",
            "/usr/local/lib",
            "/usr/local/lib64",
            "/usr/local/share",
            "/usr/lib/mozilla",
            "/usr/lib/firefox",
            "/usr/lib/chromium",
            
            # Runtime and configuration
            "/run",
            "/run/dbus",
            "/run/user",
            
            # Font configuration
            "/usr/share/fonts",
            "/usr/share/icons",
            "/usr/share/themes",
            "/var/cache/fontconfig",
            
            # Application data
            "/usr/share/applications",
            "/usr/share/mime",
            "/usr/share/X11",
            "/usr/share/glib-2.0",
        ]
        
        for path in extra_paths:
            if os.path.exists(path):
                args.extend(["--ro-bind", path, path])
                self.logger.debug(f"Mounted extra path: {path}")

        # User configuration with writable overlay
        user_config_paths = [
            "~/.config",
            "~/.local/share",
            "~/.cache",
            "~/.mozilla",
            "~/.pki",
            "~/.chrome",
            "~/.config/google-chrome"
        ]

        for path in user_config_paths:
            full_path = os.path.expanduser(path)
            if os.path.exists(full_path):
                # Create temporary overlay for writable access
                temp_path = os.path.join(self.temp_dirs[0], os.path.basename(path))
                os.makedirs(temp_path, exist_ok=True)
                args.extend(["--bind", temp_path, full_path])
                self.logger.debug(f"Mounted writable overlay for {full_path}")
        
        # Set up D-Bus and runtime directories
        args.extend(self._setup_dbus())
        args.extend(self._setup_xdg_runtime())
        
        # Set up overlay filesystem if enabled
        if self.config.overlay_enabled:
            args.extend(self._setup_overlay())
        
        # Handle temporary directory
        if self.config.tmp_dir:
            args.extend(["--bind", str(self.config.tmp_dir), "/tmp"])
        else:
            args.extend(["--tmpfs", "/tmp"])

        # Add PATH environment
        args.extend([
            "--setenv", "PATH",
            "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ])
            
        return args

    def _setup_dbus(self) -> List[str]:
        """Configure D-Bus with enhanced socket handling."""
        args = []

        if os.path.exists("/run/dbus"):
            args.extend(["--bind", "/run/dbus", "/run/dbus"])

        user_dirs = [
            "/run/user/1000/bus",
            "/run/user/1000/at-spi",
            "/run/user/1000/pulse"
        ]

        for dir_path in user_dirs:
            parent_dir = os.path.dirname(dir_path)
            if os.path.exists(parent_dir):
                args.extend(["--bind", parent_dir, parent_dir])

        return args

    def _setup_environment(self, profile_env: Dict[str, str]) -> List[str]:
        """Set up environment variables with profile-specific settings."""
        env_vars = {
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "XDG_RUNTIME_DIR": self.user_runtime_dir,
            "DBUS_SESSION_BUS_ADDRESS": f"unix:path={self.user_runtime_dir}/bus"
        }

        env_vars.update(profile_env)

        args = []
        for key, value in env_vars.items():
            args.extend(["--setenv", key, value])

        return args

    def _setup_overlay(self) -> List[str]:
        """Set up overlay filesystem for writable layers."""
        args = []

        if self.config.persist_dir:
            lower_dir = self.config.persist_dir
            upper_dir = Path(tempfile.mkdtemp(dir=self.user_runtime_dir))
            work_dir = Path(tempfile.mkdtemp(dir=self.user_runtime_dir))

            self.logger.debug(f"Using overlay: lower={lower_dir}, upper={upper_dir}, work={work_dir}")

            args.extend([
                "--bind", str(upper_dir), "/overlay-upper",
                "--bind", str(work_dir), "/overlay-work",
                "--overlay", f"{lower_dir}:{str(upper_dir)}", "/overlay"
            ])
        else:
            self.logger.warning("Overlay enabled but no persist_dir specified; skipping overlay setup.")

        return args

    def _setup_xdg_runtime(self) -> List[str]:
        """Configure XDG_RUNTIME_DIR and related directories."""
        args = []

        # Set up XDG_RUNTIME_DIR
        if os.path.exists(self.user_runtime_dir):
            args.extend(["--bind", self.user_runtime_dir, self.user_runtime_dir])
        else:
            self.logger.warning(f"XDG_RUNTIME_DIR {self.user_runtime_dir} does not exist")

        # Set up common runtime directories
        runtime_dirs = [
            "/run/user/1000/pulse",  # PulseAudio
            "/run/user/1000/bus",    # D-Bus
            "/run/user/1000/gnupg",  # GnuPG
        ]

        for dir_path in runtime_dirs:
            if os.path.exists(dir_path):
                args.extend(["--bind", dir_path, dir_path])

        # Handle /dev/fd specially - it's typically a symlink to /proc/self/fd
        args.extend(["--symlink", "/proc/self/fd", "/dev/fd"])
        args.extend(["--symlink", "/proc/self/fd/0", "/dev/stdin"])
        args.extend(["--symlink", "/proc/self/fd/1", "/dev/stdout"])
        args.extend(["--symlink", "/proc/self/fd/2", "/dev/stderr"])

        return args
