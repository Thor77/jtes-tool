# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import pprint
from datetime import date
from os.path import join

import jtes.logger
from jtes import config, downloader, episodes, utils
from jtes.utils import play

jtes.logger.setup()
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
    storage_path = configuration.get('General', 'storage')
    episodes_path = join(storage_path, 'episodes')
    meta_path = join(storage_path, 'meta.json')
    # make sure required directories exist
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(episodes_path, exist_ok=True)
    # read metadata
    try:
        with open(meta_path, 'r') as f:
            meta = json.load(f)
    except FileNotFoundError:
        meta = {}
    logger.debug(
        'read metadata from %s: %s', meta_path, pprint.pformat(meta))
    downloaded_episodes = sorted(
        utils.parse_downloads(meta.get('downloads', [])),
        key=lambda e: e.published
    )
    # find unplayed files
    unplayed = list(filter(
        lambda episode: episode in meta.get('history', []),
        downloaded_episodes
    ))
    if unplayed:
        logger.debug('there are unplayed episodes: %s', unplayed)
        for unplayed_episode in sorted(unplayed, reverse=True):
            # play episode
            play(unplayed_episode)
            # add episode to history
            meta.setdefault('history', []).append(unplayed_episode)
    logger.debug('no unplayed episodes left, fetching new ones')
    available_episodes = episodes.available()
    logger.debug('there are episodes available for download: %s',
                 available_episodes)
    # find published date of latest downloaded file
    latest_downloaded_published = downloaded_episodes[-1].published \
        if downloaded_episodes else date.min
    logger.debug('latest downloaded episode is from %s',
                 latest_downloaded_published)
    # only download episodes newer than latest_download
    episodes_to_downloaded = list(filter(
        lambda episode: episode.published > latest_downloaded_published,
        available_episodes
    ))[:configuration.getint('General', 'max')]
    logger.debug('will downloaded these episodes: %s', episodes_to_downloaded)
    downloads = list(downloader.download_episodes(
        episodes_to_downloaded, episodes_path))
    meta.setdefault('downloads', []).extend(downloads)
    # write metadata
    with open(meta_path, 'w+') as f:
        json.dump(meta, f)
    logger.debug(
        'wrote metadata to %s: %s', meta_path, pprint.pformat(meta))


if __name__ == '__main__':
    cli()
