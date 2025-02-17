from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Set
from .enums import IsolationLevel, ApplicationProfile

@dataclass
class IsolationConfig:
    """Configuration for application isolation with comprehensive options."""
    app_command: List[str]
    persist_dir: Optional[Path] = None
    network_enabled: bool = True
    gui_enabled: bool = True
    isolation_level: IsolationLevel = IsolationLevel.STANDARD
    tmp_dir: Optional[Path] = None
    overlay_enabled: bool = True
    debug: bool = False
    profile: Optional[ApplicationProfile] = None

    def __post_init__(self):
        """Validate and process configuration after initialization."""
        if not self.app_command:
            raise ValueError("Application command cannot be empty")

        if isinstance(self.persist_dir, str):
            self.persist_dir = Path(self.persist_dir)
        if isinstance(self.tmp_dir, str):
            self.tmp_dir = Path(self.tmp_dir)
