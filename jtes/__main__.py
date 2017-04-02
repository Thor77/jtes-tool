# -*- coding: utf-8 -*-
import argparse
import logging
import os
import pickle
import pprint
from os.path import join

from jtes import config, downloader, episodes, utils
from jtes.logger import file_handler, stream_handler

logger = logging.getLogger('jtes')


def cli():
    parser = argparse.ArgumentParser(
        description='Play the latest (unplayed) episode from JedenTagEinSet',
        argument_default=argparse.SUPPRESS
    )
    parser.add_argument(
        '-c', '--config',
        type=str, help='path to config'
    )
    parser.add_argument(
        '-d', '--debug',
        help='debug mode', action='store_true'
    )
    parser.add_argument(
        '-s', '--storage',
        type=str, help='path to a storage-directory for episodes'
    )
    parser.add_argument(
        '-m', '--max',
        type=int, help='max episodes to download'
    )
    parser.add_argument(
        '-nd', '--nodownload',
        help='dont download new episodes', action='store_true'
    )
    options = parser.parse_args()
    if 'config' in options:
        configuration = config.load(options.config)
    else:
        configuration = config.load()
    for option, value in vars(options).items():
        configuration.set('General', option, str(value))
    main(configuration)


def main(configuration):
    if configuration.getboolean('General', 'debug'):
        logger.setLevel(logging.DEBUG)
    # add logging handler
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    storage_path = configuration.get('General', 'storage')
    episodes_path = join(storage_path, 'episodes')
    meta_path = join(storage_path, 'meta.pickle')
    # make sure required directories exist
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(episodes_path, exist_ok=True)
    # read metadata
    try:
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
    except FileNotFoundError:
        meta = {}
    logger.debug(
        'read metadata from %s: %s', meta_path, pprint.pformat(meta))
    downloaded_episodes = sorted(
        meta.get('downloads', []),
        key=lambda e: e.published
    )
    # find unplayed files
    unplayed = list(filter(
        lambda episode: episode not in meta.get('history', []),
        downloaded_episodes
    ))
    if unplayed:
        logger.info('There are unplayed episodes: %s', unplayed)
        for unplayed_episode in unplayed:
            # play episode
            utils.play(unplayed_episode.path)
            # add episode to history
            meta.setdefault('history', []).append(unplayed_episode)
    if configuration.getboolean('General', 'nodownload'):
        logger.info('downloading new episodes forbidden (nodownload) -> exit')
        return
    logger.info('No unplayed episodes left, fetching new ones')
    available_episodes = episodes.available()
    logger.debug('there are episodes available for download: %s',
                 available_episodes)
    # strip path from episodes
    # maybe add an url-attr in the future
    old_downloads = list(
        map(lambda e: e._replace(path=None), meta.get('downloads', []))
    )
    # only download not downloaded episodes
    episodes_to_downloaded = list(filter(
        lambda episode: episode._replace(path=None) not in old_downloads,
        available_episodes
    ))[:configuration.getint('General', 'max')]
    logger.debug('will downloaded these episodes: %s', episodes_to_downloaded)
    downloads = downloader.download_episodes(
        episodes_to_downloaded, episodes_path)
    # play downloaded episodes
    for download in downloads:
        # play episode
        utils.play(download.path)
        # add episode to history
        meta.setdefault('history', []).append(download)
    meta.setdefault('downloads', []).extend(downloads)
    # write metadata
    with open(meta_path, 'wb+') as f:
        pickle.dump(meta, f)
    logger.debug(
        'wrote metadata to %s: %s', meta_path, pprint.pformat(meta))


if __name__ == '__main__':
    cli()
