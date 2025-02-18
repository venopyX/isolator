import argparse
import sys
from pathlib import Path
from .config import IsolationConfig, ResourceLimits
from .enums import IsolationLevel, ApplicationProfile
from .isolator import ApplicationIsolator
from .logging_config import setup_logging

def parse_args() -> argparse.Namespace:
    """Parse command line arguments with comprehensive options."""
    parser = argparse.ArgumentParser(
        description="Run GUI applications in isolated environments with advanced containerization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "command",
        nargs="+",
        help="Command to run in isolation"
    )

    parser.add_argument(
        "--profile",
        choices=[p.name for p in ApplicationProfile],
        help="Force specific application profile"
    )

    parser.add_argument(
        "--persist",
        type=Path,
        help="Directory to persist data to"
    )

    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Disable network access"
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Disable GUI support"
    )

    parser.add_argument(
        "--isolation-level",
        type=str,
        choices=[level.name.lower() for level in IsolationLevel],
        default=IsolationLevel.STANDARD.name.lower(),
        help="Set isolation level"
    )

    # Resource limit arguments
    parser.add_argument(
        "--memory",
        type=str,
        help="Memory limit (e.g., '2G', '500M')"
    )

    parser.add_argument(
        "--cpu",
        type=int,
        help="CPU limit percentage (1-100)"
    )

    parser.add_argument(
        "--io-weight",
        type=int,
        choices=range(10, 1001),
        help="I/O weight (10-1000)"
    )

    parser.add_argument(
        "--max-processes",
        type=int,
        help="Maximum number of processes"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    setup_logging(args.debug)

    # Create resource limits if any are specified
    resource_limits = None
    if any([args.memory, args.cpu, args.io_weight, args.max_processes]):
        resource_limits = ResourceLimits(
            memory_limit=args.memory,
            cpu_limit=args.cpu,
            io_weight=args.io_weight,
            max_processes=args.max_processes
        )

    config = IsolationConfig(
        app_command=args.command,
        persist_dir=args.persist,
        network_enabled=not args.no_network,
        gui_enabled=not args.no_gui,
        isolation_level=IsolationLevel[args.isolation_level.upper()],
        debug=args.debug,
        profile=ApplicationProfile[args.profile.upper()] if args.profile else None,
        resource_limits=resource_limits
    )

    isolator = ApplicationIsolator(config)
    sys.exit(isolator.run())

if __name__ == "__main__":
    main()
