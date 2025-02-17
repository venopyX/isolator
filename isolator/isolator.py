import logging
import subprocess
import sys
from typing import List
from .config import IsolationConfig
from .managers.display_manager import DisplayManager
from .managers.filesystem_manager import FilesystemManager
from .managers.security_manager import SecurityManager

class ApplicationIsolator:
    """Main class for handling application isolation."""

    def __init__(self, config: IsolationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.display_manager = DisplayManager()
        self.filesystem_manager = FilesystemManager(config)
        self.security_manager = SecurityManager(config.isolation_level)

    def run(self) -> int:
        """Run the isolated application."""
        try:
            resolved_command = self.filesystem_manager.resolve_command(self.config.app_command)
            self.config.app_command = resolved_command

            self.logger.debug(f"Resolved command: {resolved_command}")
            bwrap_args = self._prepare_bwrap_args()

            return self._execute_bwrap(bwrap_args)
        except Exception as e:
            self.logger.error(f"Failed to run isolated application: {e}")
            return 1
        finally:
            self.cleanup()

    def _prepare_bwrap_args(self) -> List[str]:
        """Prepare complete bubblewrap command arguments."""
        args = ["bwrap"]

        if self.config.gui_enabled:
            args.extend(self.display_manager.get_display_args())

        args.extend(self.filesystem_manager.setup())
        args.extend(self.security_manager.get_security_args())
        args.extend(self.config.app_command)

        return args

    def _execute_bwrap(self, bwrap_args: List[str]) -> int:
        """Execute bubblewrap with prepared arguments."""
        self.logger.debug(f"Executing: {' '.join(bwrap_args)}")

        try:
            process = subprocess.Popen(bwrap_args)
            return process.wait()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, cleaning up...")
            return 130

    def cleanup(self):
        """Clean up resources."""
        self.filesystem_manager.cleanup()
