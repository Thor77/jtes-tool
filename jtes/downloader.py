# -*- coding: utf-8 -*-
import logging
from os.path import join

import youtube_dl


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
    outtmpl = join(target_path, '%(title)s.%(ext)s')
    YTDL_OPTIONS['outtmpl'] = outtmpl
    with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
        for episode in episodes:
            ytdl.extract_info(episode.path, extra_info={
                'episode': episode
            })
            yield episode
