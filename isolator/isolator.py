import os
import logging
import subprocess
import sys
from typing import List, Optional
from .config import IsolationConfig
from .managers.display_manager import DisplayManager
from .managers.filesystem_manager import FilesystemManager
from .managers.security_manager import SecurityManager
from .enums import ApplicationProfile

class ApplicationIsolator:
    """Main class for handling application isolation."""

    def __init__(self, config: IsolationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.display_manager = DisplayManager()
        self.filesystem_manager = FilesystemManager(config)
        self.security_manager = SecurityManager(
            config.isolation_level,
            config.profile
        )

    def run(self) -> int:
        """Run the isolated application."""
        try:
            resolved_command = self.filesystem_manager.resolve_command(self.config.app_command)
            self.config.app_command = resolved_command

            self.logger.debug(f"Resolved command: {resolved_command}")
            bwrap_args = self._prepare_bwrap_args()
            
            # Add browser-specific environment variables if needed
            if self.config.profile == ApplicationProfile.BROWSER:
                bwrap_args.extend([
                    "--setenv", "CHROME_SANDBOX", "1",
                    "--setenv", "CHROME_WRAPPER", "1",
                    "--setenv", "CHROME_DISABLE_SETUID_SANDBOX", "1"
                ])

            return self._execute_bwrap(bwrap_args)
        except Exception as e:
            self.logger.error(f"Failed to run isolated application: {e}")
            return 1
        finally:
            self.cleanup()

    def _prepare_bwrap_args(self) -> List[str]:
        """Prepare complete bubblewrap command arguments."""
        args = ["bwrap"]

        # Add filesystem setup first
        args.extend(self.filesystem_manager.setup())

        # Add display configuration if GUI is enabled
        if self.config.gui_enabled:
            args.extend(self.display_manager.get_display_args())

        # Add security arguments
        args.extend(self.security_manager.get_security_args())

        # Add the actual command to run
        args.extend(self.config.app_command)

        return args

    def _execute_bwrap(self, bwrap_args: List[str]) -> int:
        """Execute bubblewrap with prepared arguments."""
        self.logger.debug(f"Executing: {' '.join(bwrap_args)}")

        try:
            # Use shell=False for better security
            process = subprocess.Popen(
                bwrap_args,
                env=os.environ.copy(),  # Pass current environment
                shell=False
            )
            return process.wait()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, cleaning up...")
            return 130
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to execute bwrap: {e}")
            return e.returncode
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1

    def cleanup(self):
        """Clean up resources."""
        self.filesystem_manager.cleanup()