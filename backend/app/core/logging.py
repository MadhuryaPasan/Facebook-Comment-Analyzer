import logging


def setup_logging(log_file: str = "backend-server.log", level: int = logging.INFO) -> None:
    """Configure application-wide logging once at startup."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
