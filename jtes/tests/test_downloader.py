from os import path as ospath
from shutil import rmtree

import pytest

from jtes.downloader import download_episodes
from jtes.episodes import Episode


@pytest.fixture
def storage(request):
    storage_directory = 'jtes/tests/storage'

    def cleanup():
        rmtree(storage_directory)
    request.addfinalizer(cleanup)
    return storage_directory


def test_dowload_episodes(storage):
    episode = Episode(
        path='https://www.jedentageinset.de/2017/03/21/1645-guzy-berlin-deep-'
        'selected-radioshow-017/',
        name='#1645 Guzy – Berlin Deep Selected Radioshow 017',
        published=None
    )
    download_episodes([episode], storage)
    assert ospath.isfile(
        ospath.join(storage, 'BDS Radioshow #017 - Mixed By Guzy.mp3')
    )
