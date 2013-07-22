import logging


def setupLog():
    """
    Sets up the main logger for the daemon
    """
    level = logging.WARNING
    if debug:
            level = logging.DEBUG

    formatter = logging.Formatter("""%(asctime)s - %(name)s - %(levelname)s
    %(message)s""")

    logger = logging.getLogger("irc")
    logger.setLevel(level)

    fh = logging.FileHandler("logz.log")
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Log to the console if we're in debug mode
    if debug:
        try:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        except:
            pass

    return logger
