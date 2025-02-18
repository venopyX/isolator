# security_manager.py
import logging
import os
from typing import List, Optional
from ..enums import IsolationLevel, ApplicationProfile

class SecurityManager:
    """Handles security-related configurations and policies."""

    def __init__(self, isolation_level: IsolationLevel, profile: Optional[ApplicationProfile] = None):
        self.isolation_level = isolation_level
        self.profile = profile
        self.logger = logging.getLogger(__name__)

    def get_security_args(self) -> List[str]:
        """Get security-related bubblewrap arguments based on profile and isolation level."""
        args = []

        # Base security options for all profiles
        args.extend([
            "--unshare-pid",      # Isolate process namespace
            "--unshare-ipc",      # Isolate IPC namespace
            "--unshare-uts",      # Isolate UTS namespace
            "--new-session",      # New session
            "--die-with-parent"   # Clean exit
        ])

        # Profile-specific security settings
        if self.profile == ApplicationProfile.BROWSER:
            args.extend(self._get_browser_security_args())
        else:
            args.extend(self._get_default_security_args())

        # Environment setup (must be after namespace setup)
        env_vars = {
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "HOME": os.path.expanduser("~"),
            "USER": os.getenv("USER", ""),
            "LANG": os.getenv("LANG", "C.UTF-8"),
            "TERM": os.getenv("TERM", "xterm-256color")
        }

        for key, value in env_vars.items():
            if value:  # Only set if value is not empty
                args.extend(["--setenv", key, value])

        return args

    def _get_browser_security_args(self) -> List[str]:
        """Get security arguments optimized for browser applications."""
        browser_args = [
            "--share-net",       # Enable network access
            "--unshare-user-try",  # Try user namespace isolation
            "--new-session",      # New session
            "--cap-add", "ALL",   # Chrome needs full capabilities for its sandbox
            "--dev-bind", "/dev/shm", "/dev/shm",  # Shared memory
            "--bind", "/tmp", "/tmp",  # Temporary files
            "--bind", "/run", "/run"  # Runtime files
        ]

        # Add seccomp filtering for browsers if available
        if os.path.exists("/usr/share/chromium/seccomp-filter.bpf"):
            browser_args.extend([
                "--seccomp", "9",
                "/usr/share/chromium/seccomp-filter.bpf"
            ])

        return browser_args

    def _get_default_security_args(self) -> List[str]:
        """Get default security arguments for non-browser applications."""
        default_args = [
            "--hostname", "isolated"  # Set hostname
        ]
        
        if self.isolation_level == IsolationLevel.STRICT:
            default_args.extend([
                "--unshare-net",         # Network isolation
                "--unshare-cgroup-try",  # Try cgroup isolation
                "--unshare-user-try",    # Try user namespace isolation
                "--cap-drop", "ALL"      # Drop all capabilities
            ])

        return default_args

    def validate_security_config(self) -> bool:
        """Validate the security configuration."""
        try:
            # Validate isolation level
            if not isinstance(self.isolation_level, IsolationLevel):
                self.logger.error(f"Invalid isolation level: {self.isolation_level}")
                return False

            # Validate profile if set
            if self.profile is not None and not isinstance(self.profile, ApplicationProfile):
                self.logger.error(f"Invalid profile: {self.profile}")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            return False
