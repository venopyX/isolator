from enum import Enum, auto

class DisplayServer(Enum):
    X11 = auto()
    WAYLAND = auto()
    UNKNOWN = auto()

class IsolationLevel(Enum):
    MINIMAL = auto()
    STANDARD = auto()
    STRICT = auto()

class ApplicationProfile(Enum):
    BASIC = auto()
    BROWSER = auto()
    MULTIMEDIA = auto()
    DEVELOPMENT = auto()
    GRAPHICS = auto()
