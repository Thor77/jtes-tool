# -*- coding: utf-8 -*-
from subprocess import run

from jtes.episodes import Episode


def play(path):
    run(['mpv', path])


def parse_downloads(downloads):
    print(downloads)
    return downloads
