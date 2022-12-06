import sys
import logging
from src.main import main
from src.utils.log_utils import init_loggers


logger = logging.getLogger(__name__)
console = logging.getLogger('console')


if __name__ == '__main__':
    try:
        init_loggers()
        main(sys.argv)
    except Exception as err:  # pylint: disable=broad-except
        logger.exception('An unexpected exception occurred, %s', err)
        console.exception('An unexpected exception occurred, %s', err)
