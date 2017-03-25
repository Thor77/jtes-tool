# -*- coding: utf-8 -*-
import argparse
import logging
import os
import pickle
import pprint
from datetime import date
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
    logger.info('No unplayed episodes left, fetching new ones')
    available_episodes = episodes.available()
    logger.debug('there are episodes available for download: %s',
                 available_episodes)
    # find published date of latest downloaded file
    latest_downloaded_published = downloaded_episodes[-1].published \
        if downloaded_episodes else date.min
    logger.debug('latest downloaded episode is from %s',
                 latest_downloaded_published)
    # only download episodes newer than latest_download
    # and not already downloaded
    episodes_to_downloaded = list(filter(
        lambda episode:
            episode.published > latest_downloaded_published and
            episode not in meta.get('downloads', []),
        available_episodes
    ))[:configuration.getint('General', 'max')]
    logger.debug('will downloaded these episodes: %s', episodes_to_downloaded)
    downloads = downloader.download_episodes(
        episodes_to_downloaded, episodes_path)
    meta.setdefault('downloads', []).extend(downloads)
    # write metadata
    with open(meta_path, 'wb+') as f:
        pickle.dump(meta, f)
    logger.debug(
        'wrote metadata to %s: %s', meta_path, pprint.pformat(meta))


if __name__ == '__main__':
    cli()
