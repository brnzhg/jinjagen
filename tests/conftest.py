"""
    pytest config for sphinxcontrib/jinjagen/tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by Brian Zhang <brnzhg@gmail.com>
    :license: BSD, see LICENSE for details.
"""
import os
import shutil

import docutils
import pytest
# from pathlib import Path
import sphinx
from sphinx.testing.path import path

pytest_plugins = 'sphinx.testing.fixtures'

#TODO use pathlib
@pytest.fixture(scope='session')
def rootdir():
    return path(__file__).parent.abspath() / 'roots'



def pytest_report_header(config):
    header = "libraries: Sphinx-%s, docutils-%s" % (
        sphinx.__display_version__,
        docutils.__version__,
    )
    if hasattr(config, "_tmp_path_factory"):
        header += "\nbase tempdir: %s" % config._tmp_path_factory.getbasetemp()

    return header


def _initialize_test_directory(session):
    if "SPHINX_TEST_TEMPDIR" in os.environ:
        tempdir = os.path.abspath(os.getenv("SPHINX_TEST_TEMPDIR"))
        print("Temporary files will be placed in %s." % tempdir)

        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)

        os.makedirs(tempdir)


def pytest_sessionstart(session):
    _initialize_test_directory(session)