from functools import partial
from functools import wraps
import logging


class UtilsMonitoring:  # noqa: R0205
    """Some Utilities."""

    # pylint: disable:invalid_name
    @staticmethod
    def io_display(
        func=None, input=True, output=True, level=15
    ):  # pylint: disable=W0622
        """Monitor the input/output of a function.
        NB : Do not use this monitoring method on an __init__ if the class
        implements __repr__ with attributes
        Parameters
        ----------
        func: func
            function to monitor (default: {None})
        input: bool
            True when the function must monitor the input (default: {True})
        output: bool
            True when the function must monitor the output (default: {True})
        level: int
            Level from which the function must log
        Returns
        -------
        object : the result of the function
        """
        if func is None:
            return partial(
                UtilsMonitoring.io_display,
                input=input,
                output=output,
                level=level,
            )

        @wraps(func)
        def wrapped(*args, **kwargs):
            name = func.__qualname__
            logger = logging.getLogger(__name__ + "." + name)

            if input and logger.getEffectiveLevel() <= level:
                msg = f"Entering '{name}' (args={args[1:len(args)]}, kwargs={kwargs})"
                logger.log(level, msg)

            result = func(*args, **kwargs)

            if output and logger.getEffectiveLevel() <= level:
                msg = f"Exiting '{name}' (result={result})"
                logger.log(level, msg)

            return result

        return wrapped