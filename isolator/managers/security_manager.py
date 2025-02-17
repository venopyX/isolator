import logging
from typing import List
from ..enums import IsolationLevel

class SecurityManager:
    """Handles security-related configurations and policies."""

    def __init__(self, isolation_level: IsolationLevel):
        self.isolation_level = isolation_level
        self.logger = logging.getLogger(__name__)

    def get_security_args(self) -> List[str]:
        """Get security-related bubblewrap arguments."""
        args = [
            "--unshare-pid",
            "--unshare-uts",
            "--unshare-ipc"
        ]

        if self.isolation_level == IsolationLevel.STRICT:
            args.extend([
                "--unshare-net",
                "--unshare-user",
                "--hostname", "isolated"
            ])

        return args
