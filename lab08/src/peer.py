import logging
from receiver import Receiver
from sender import Sender


def _make_logger(name, filename):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            handler = logging.FileHandler(filename, encoding="utf-8")
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)

            logger.addHandler(handler)

        return logger


class Peer(Receiver, Sender):
    def __init__(self, name, port, drop_rate, timeout):
        Receiver.__init__(self, _make_logger(name, f'{name}.log'), port, drop_rate)
        Sender.__init__(self, _make_logger(name, f'{name}.log'), timeout, drop_rate)
