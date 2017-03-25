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

    downloaded_episodes = []
    with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
        for episode in episodes:
            logger.info('Downloading %s', episode.name)
            logger.debug('downloading %s', episode)
            # first extract mix-url from JedenTagEinSet
            jtes_info = ytdl.extract_info(episode.path, process=False)
            if len(jtes_info['entries']) <= 0:
                logger.warning('No download found for %s', episode.path)
                continue
            mix_url = jtes_info['entries'][0]['url']  # only download first

            # download mix
            def save_episode(progress):
                if progress['status'] != 'finished':
                    return
                downloaded_episodes.append(
                    episode._replace(path=progress['filename'])
                )
            ytdl.add_progress_hook(save_episode)
            ytdl.extract_info(mix_url)
            ytdl._progress_hooks.remove(save_episode)
    return downloaded_episodes
