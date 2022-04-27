from .server import FakeServer, expect_that
import logging


class CustomColorFormatter(logging.Formatter):
    """Color formatter."""

    # Reset
    color_Off = "\033[0m"  # Text Reset

    log_colors = {
        logging.DEBUG: "\033[1;34m",  # blue
        logging.INFO: "\033[0;32m",  # green
        logging.WARNING: "\033[1;33m",  # yellow
        logging.ERROR: "\033[1;31m",  # red
        logging.CRITICAL: "\033[1;41m",  # red reverted
    }

    def format(self, record) -> str:
        """Format the log.
        Args:
            record: the log record
        Returns:
            str: the formatted log record
        """
        record.levelname = "{}{}{}".format(
            CustomColorFormatter.log_colors[record.levelno],
            record.levelname,
            CustomColorFormatter.color_Off,
        )
        record.msg = "{}{}{}".format(
            CustomColorFormatter.log_colors[record.levelno],
            record.msg,
            CustomColorFormatter.color_Off,
        )

        # Select the formatter according to the log if several handlers are
        # attached to the logger
        my_formatter = logging.Formatter
        my_handler = None
        handlers = logging.getLogger(__name__).handlers
        for handler in handlers:
            handler_level = handler.level
            if handler_level == logging.getLogger(__name__).getEffectiveLevel():
                if handler.formatter:
                    my_formatter._fmt = (  # pylint: disable=W0212
                        handler.formatter._fmt  # pylint: disable=W0212
                    )
                my_handler = handler
                break
        if my_handler is not None:
            for handler in handlers:
                if handler != my_handler:
                    logging.getLogger(__name__).removeHandler(handler)
        return my_formatter.format(self, record)  # type: ignore


class ShellColorFormatter(CustomColorFormatter):
    """Shell Color formatter."""

    def format(self, record) -> str:
        """Format the log.
        Args:
            record: the log record
        Returns:
            str: the formatted log record
        """
        record.msg = "{}{}{}".format(
            CustomColorFormatter.log_colors[logging.INFO],
            record.msg,
            CustomColorFormatter.color_Off,
        )
        return record.msg


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
ch.setFormatter(CustomColorFormatter())
# add the handlers to the logger
logger.addHandler(ch)

__version__ = "0.2.1"

logger.info(f"Fake server v{__version__}")
