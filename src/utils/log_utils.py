"""
Logging utility functions.
"""

import logging

console = logging.getLogger('console')


def init_loggers():
    """
    Initialize the logger that will log messages to a rotating log file.
    """
    # Set the global logging level to DEBUG
    logging.getLogger().setLevel(logging.DEBUG)

    # Handler for console
    c_handler = logging.StreamHandler()

    # Set formatter to print only the message in console
    formatter = logging.Formatter('%(message)s')
    c_handler.setFormatter(formatter)

    # Set level to DEBUG
    c_handler.setLevel(logging.DEBUG)

    # Add the console handler to the root logger
    console.addHandler(c_handler)

    # Set the file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler = logging.FileHandler('./app.log', encoding='utf-8')
    f_handler.setFormatter(formatter)

    # Set the log level to DEBUG so that everything will be written to the log file
    f_handler.setLevel(logging.DEBUG)

    # Add the file handler to the root logger
    logging.getLogger().addHandler(f_handler)
