# -*- coding: utf-8 -*-
import logging
import os
from os.path import join

import youtube_dl

from jtes.episodes import Episode

logger = logging.getLogger('jtes')

YTDL_OPTIONS = {
    'logger': logger
}


def download_episodes(episodes, target_path):
    '''
    Download an Episode and move it to the right location

    :param episode: Episode to download
    :type episode: jtes.episodes.Episode
    '''
    def move_episode(progress_data):
        if progress_data['status'] != 'finished':
            return
        filename = progress_data['filename']
        path = join(target_path, filename)
        os.rename(filename, path)
        yield Episode(
            published=None,
            name=filename,
            path=path
        )
    YTDL_OPTIONS.setdefault('progress_hooks', []).append(move_episode)
    with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
        for episode in episodes:
            ytdl.extract_info(episode.path, extra_info={
                'episode': episode
            })
