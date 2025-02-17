import logging

def setup_logging(debug: bool = False):
    """Configure logging with appropriate level and format."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
