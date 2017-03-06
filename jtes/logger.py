# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('jtes')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('debug.txt', 'w', delay=True)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
