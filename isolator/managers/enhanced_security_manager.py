"""Enhanced security management for Isolator."""
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict
from ..config.profiles import ProfileConfig
from ..enums import IsolationLevel

class SecurityError(Exception):
    """Base class for security-related errors."""
    pass

class EnhancedSecurityManager:
    """Enhanced security manager with improved isolation and monitoring."""
    
    def __init__(self, isolation_level: IsolationLevel, profile: Optional[ProfileConfig] = None):
        self.isolation_level = isolation_level
        self.profile = profile
        self.logger = logging.getLogger(__name__)
        self.seccomp_dir = Path("/etc/isolator/seccomp")
        self._setup_seccomp_dir()

    def _setup_seccomp_dir(self):
        """Ensure seccomp directory exists with default profiles."""
        if not self.seccomp_dir.exists():
            try:
                self.seccomp_dir.mkdir(parents=True, exist_ok=True)
                # TODO: Install default seccomp profiles
            except Exception as e:
                self.logger.warning(f"Failed to create seccomp directory: {e}")

    def get_security_args(self) -> List[str]:
        """Get comprehensive security arguments for bubblewrap."""
        args = []
        
        # Base security settings
        args.extend(self._get_base_security_args())
        
        # Profile-specific security
        if self.profile:
            args.extend(self._get_profile_security_args())
        
        # Isolation level specific settings
        args.extend(self._get_isolation_level_args())
        
        # Seccomp filtering
        seccomp_args = self._get_seccomp_args()
        if seccomp_args:
            args.extend(seccomp_args)
            
        return args

    def _get_base_security_args(self) -> List[str]:
        """Get base security arguments applied to all configurations."""
        return [
            "--unshare-pid",      # Process namespace isolation
            "--unshare-ipc",      # IPC namespace isolation
            "--unshare-uts",      # UTS namespace isolation
            "--proc", "/proc",    # Secure /proc mount
            "--dev", "/dev",      # Secure /dev mount
            "--new-session",      # New session
            "--die-with-parent"   # Clean exit
        ]

    def _get_profile_security_args(self) -> List[str]:
        """Get security arguments based on the profile configuration."""
        if not self.profile:
            return []
            
        args = []
        
        # Add capabilities
        for cap in self.profile.capabilities:
            args.extend(["--cap-add", cap])
            
        # Add network ports if specified
        if self.profile.network_ports:
            for port in self.profile.network_ports:
                args.extend(["--add-port", str(port)])
                
        return args

    def _get_isolation_level_args(self) -> List[str]:
        """Get security arguments based on isolation level."""
        args = []
        
        if self.isolation_level == IsolationLevel.STRICT:
            args.extend([
                "--unshare-net",         # Network isolation
                "--unshare-cgroup-try",  # cgroup isolation
                "--cap-drop", "ALL"      # Drop all capabilities
            ])
            
            # Additional strict mode settings
            if not self.profile or "CAP_SYS_ADMIN" not in self.profile.capabilities:
                args.extend([
                    "--unshare-user-try",    # User namespace isolation
                    "--hostname", "isolated"  # Set hostname
                ])
                
        elif self.isolation_level == IsolationLevel.STANDARD:
            # Standard isolation allows some network access but still maintains security
            args.extend([
                "--share-net",           # Allow network
                "--unshare-user-try",    # Try user namespace isolation
                "--hostname", "isolated"  # Set hostname
            ])
            
        return args

    def _get_seccomp_args(self) -> List[str]:
        """Get seccomp filtering arguments."""
        if self.profile and self.profile.seccomp_profile:
            profile_path = self.seccomp_dir / self.profile.seccomp_profile
            if profile_path.exists():
                return ["--seccomp", "9", str(profile_path)]
                
        # Fall back to default seccomp profile if available
        default_profile = self.seccomp_dir / "default.bpf"
        if default_profile.exists():
            return ["--seccomp", "9", str(default_profile)]
            
        return []

    def validate_security_config(self) -> bool:
        """Validate the security configuration."""
        try:
            if self.profile:
                # Validate capabilities
                for cap in self.profile.capabilities:
                    if not cap.startswith("CAP_"):
                        raise SecurityError(f"Invalid capability format: {cap}")
                
                # Validate network ports
                if self.profile.network_ports:
                    for port in self.profile.network_ports:
                        if not (0 <= port <= 65535):
                            raise SecurityError(f"Invalid port number: {port}")
                            
            return True
        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            return False
