import os
import pwd
from typing import Dict, Set
from dataclasses import dataclass, field
from ..enums import ApplicationProfile

@dataclass
class SystemRequirement:
    """System requirements for application isolation."""
    paths: Set[str] = field(default_factory=set)
    devices: Set[str] = field(default_factory=set)
    env_vars: Dict[str, str] = field(default_factory=dict)
    capabilities: Set[str] = field(default_factory=set)

class RequirementsManager:
    """Manages system requirements for different application types."""

    def __init__(self):
        self.profiles: Dict[ApplicationProfile, SystemRequirement] = self._initialize_profiles()

    def _initialize_profiles(self) -> Dict[ApplicationProfile, SystemRequirement]:
        profiles = {}

        profiles[ApplicationProfile.BASIC] = SystemRequirement(
            paths={"/usr", "/etc", "/opt", "/bin", "/lib", "/lib64"},
            devices={"/dev/dri"},
            env_vars={"NO_AT_BRIDGE": "1"}
        )

        browser_req = SystemRequirement(
            paths={
                # Base system paths
                "/usr", "/etc", "/opt", "/bin", "/lib", "/lib64",
                "/usr/lib", "/usr/lib64", "/usr/local/lib", "/usr/local/lib64",
                "/usr/share", "/usr/local/share",
                
                # System devices and runtime
                "/sys/dev", "/sys/devices", "/run/dbus", "/run/user",
                "/var/run/dbus", "/var/lib/dbus",
                
                # Font configuration
                "/etc/fonts", "/usr/share/fonts", "/var/cache/fontconfig",
                "/usr/share/fontconfig", "/usr/share/icons", "/usr/share/themes",
                
                # Application specific
                "/usr/share/applications", "/usr/share/mime",
                "/usr/share/mozilla", "/usr/lib/mozilla", "/usr/lib/firefox",
                "/usr/share/glib-2.0", "/usr/share/gtk-3.0",
                
                # User configuration
                f"/home/{pwd.getpwuid(os.getuid()).pw_name}/.mozilla",
                f"/home/{pwd.getpwuid(os.getuid()).pw_name}/.config",
                f"/home/{pwd.getpwuid(os.getuid()).pw_name}/.cache",
                f"/home/{pwd.getpwuid(os.getuid()).pw_name}/.local/share"
            },
            devices={"/dev/dri", "/dev/shm"},
            env_vars={
                "NO_AT_BRIDGE": "1",
                "FONTCONFIG_PATH": "/etc/fonts",
                "CHROME_WRAPPER": "1"
            },
            capabilities={"net_admin"}
        )
        profiles[ApplicationProfile.BROWSER] = browser_req

        profiles[ApplicationProfile.MULTIMEDIA] = SystemRequirement(
            paths={
                "/usr", "/etc", "/opt", "/bin", "/lib", "/lib64",
                "/run/dbus", "/run/user", "/etc/machine-id"
            },
            devices={"/dev/dri", "/dev/snd"},
            env_vars={"PULSE_SERVER": "unix:/run/user/1000/pulse/native"}
        )

        return profiles

    def detect_profile(self, command: str) -> ApplicationProfile:
        """Automatically detect appropriate profile for an application."""
        browsers = {"chrome", "firefox", "chromium", "opera", "brave"}
        multimedia = {"vlc", "mpv", "audacity", "obs"}
        development = {"code", "idea", "pycharm", "eclipse"}
        graphics = {"gimp", "inkscape", "krita", "blender"}

        cmd_base = os.path.basename(command).lower()

        if any(browser in cmd_base for browser in browsers):
            return ApplicationProfile.BROWSER
        elif any(app in cmd_base for app in multimedia):
            return ApplicationProfile.MULTIMEDIA
        elif any(app in cmd_base for app in development):
            return ApplicationProfile.DEVELOPMENT
        elif any(app in cmd_base for app in graphics):
            return ApplicationProfile.GRAPHICS

        return ApplicationProfile.BASIC
