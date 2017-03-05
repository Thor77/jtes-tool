# -*- coding: utf-8 -*-
from subprocess import Popen

from jtes.episodes import Episode


def play(path):
    Popen([path], executable='mpv')


def parse_downloads(downloads):
    print(downloads)
    return downloads
