# -*- coding: utf-8 -*-
import logging


def setup():
    logger = logging.getLogger('jtes')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('debug.txt', 'w', delay=True)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    # ch.setLevel(logging.INFO)
    ch.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.addHandler(ch)
