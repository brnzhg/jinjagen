import pytest
from sphinx.application import Sphinx
from sphinx.testing.path import path

from sphinx.roles import XRefRole

@pytest.mark.sphinx(testroot='case1')
def test_test1(app: Sphinx, status, warning):

    assert app.builder is not None
    app.builder.build_all()
