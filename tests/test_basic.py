import os
from pathlib import Path
import tempfile
import shutil

import pytest

from filemgr import human_readable, get_total_size, move_to_trash, remove_recursive


def test_human_readable():
    assert human_readable(1023).endswith('B')
    assert human_readable(1024).endswith('K' + 'B')


def test_get_total_size_and_delete(tmp_path):
    # create files
    p = tmp_path / "data"
    p.mkdir()
    f = p / "a.txt"
    f.write_bytes(b"hello")
    f2 = p / "b.txt"
    f2.write_bytes(b"world")

    total = get_total_size(str(p))
    assert total >= 10

    # move to trash via function (should create .filemgr_trash on disk root)
    dest = move_to_trash(str(p))
    assert Path(dest).exists()

    # cleanup
    shutil.rmtree(str(dest))
