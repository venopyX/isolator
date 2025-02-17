import os
import logging
from typing import List
from ..enums import DisplayServer

class DisplayManager:
    """Handles display server detection and configuration."""

    def __init__(self):
        self.display_server = self._detect_display_server()
        self.logger = logging.getLogger(__name__)

    def _detect_display_server(self) -> DisplayServer:
        """Detect the current display server."""
        if os.environ.get("WAYLAND_DISPLAY"):
            return DisplayServer.WAYLAND
        elif os.environ.get("DISPLAY"):
            return DisplayServer.X11
        return DisplayServer.UNKNOWN

    def get_display_args(self) -> List[str]:
        """Get bubblewrap arguments for display server access."""
        args = []

        if self.display_server == DisplayServer.X11:
            self.logger.info("Configuring X11 display server")
            x11_socket = "/tmp/.X11-unix"
            if os.path.exists(x11_socket):
                args.extend([
                    "--bind", x11_socket, x11_socket,
                    "--setenv", "DISPLAY", os.environ["DISPLAY"]
                ])

                xauth_path = os.path.expanduser("~/.Xauthority")
                if os.path.exists(xauth_path):
                    args.extend(["--ro-bind", xauth_path, xauth_path])

        elif self.display_server == DisplayServer.WAYLAND:
            self.logger.info("Configuring Wayland display server")
            wayland_socket = os.path.join(
                os.environ.get("XDG_RUNTIME_DIR", ""),
                os.environ.get("WAYLAND_DISPLAY", "")
            )
            if os.path.exists(wayland_socket):
                args.extend([
                    "--bind", wayland_socket, wayland_socket,
                    "--setenv", "WAYLAND_DISPLAY", os.environ["WAYLAND_DISPLAY"],
                    "--setenv", "XDG_RUNTIME_DIR", os.environ["XDG_RUNTIME_DIR"]
                ])

        return args
