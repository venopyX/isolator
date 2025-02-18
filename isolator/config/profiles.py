"""Profile configuration management for Isolator."""
from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import yaml
from pathlib import Path

@dataclass
class ProfileConfig:
    """Configuration for an application profile."""
    name: str
    mounts: List[str]
    devices: List[str]
    capabilities: List[str]
    env_vars: Dict[str, str]
    seccomp_profile: Optional[str] = None
    network_ports: Optional[List[int]] = None
    resource_limits: Optional[Dict[str, str]] = None

class ProfileManager:
    """Manages application profiles and their configurations."""
    
    def __init__(self):
        self.profiles: Dict[str, ProfileConfig] = {}
        self.config_paths = [
            Path("/etc/isolator/profiles"),
            Path.home() / ".config" / "isolator" / "profiles",
        ]
        self._load_profiles()

    def _load_profiles(self):
        """Load profiles from configuration files."""
        for config_path in self.config_paths:
            if not config_path.exists():
                continue
                
            for profile_file in config_path.glob("*.yaml"):
                try:
                    with open(profile_file) as f:
                        data = yaml.safe_load(f)
                        profile = ProfileConfig(**data)
                        self.profiles[profile.name] = profile
                except Exception as e:
                    logging.error(f"Failed to load profile {profile_file}: {e}")

    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get a profile configuration by name."""
        return self.profiles.get(name)

    def create_profile(self, config: ProfileConfig) -> bool:
        """Create a new profile configuration."""
        if config.name in self.profiles:
            return False
            
        # Save to user config directory
        config_dir = Path.home() / ".config" / "isolator" / "profiles"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        profile_path = config_dir / f"{config.name}.yaml"
        with open(profile_path, "w") as f:
            yaml.dump(dataclasses.asdict(config), f)
            
        self.profiles[config.name] = config
        return True

    def update_profile(self, config: ProfileConfig) -> bool:
        """Update an existing profile configuration."""
        if config.name not in self.profiles:
            return False
            
        # Update in user config directory
        config_dir = Path.home() / ".config" / "isolator" / "profiles"
        profile_path = config_dir / f"{config.name}.yaml"
        
        with open(profile_path, "w") as f:
            yaml.dump(dataclasses.asdict(config), f)
            
        self.profiles[config.name] = config
        return True
