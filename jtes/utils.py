# -*- coding: utf-8 -*-
from subprocess import run


def play(path):
    run(['mpv', path])
