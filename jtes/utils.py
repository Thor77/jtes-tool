# -*- coding: utf-8 -*-
from subprocess import Popen

from jtes.episodes import Episode


def play(path):
    Popen(['mpv', path])


def parse_downloads(downloads):
    print(downloads)
    return downloads
