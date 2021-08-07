"""
    sphinxcontrib.jinjagen
    ~~~~~~~~~~~~~~~~~~~~~~

    generate multiple rst files from each jinja template

    :copyright: Copyright 2017 by Brian Zhang <brnzhg@gmail.com>
    :license: BSD, see LICENSE for details.
"""

import pbr.version

# For type annotations
from typing import Any, Dict  # noqa
from sphinx.application import Sphinx  # noqa
import filegen

__version__ = pbr.version.VersionInfo(
    'jinjagen').version_string()


# unicode?
def setup(app: Sphinx) -> Dict[str, Any]:
    # app.add_config_value("jinjagen_templates_subdir", "jinjagen", "env") #env?
    jinjagen_run1 = filegen.FileGenRunDef(gen_keys=[['stew', 'meatball']],
                                       name='recipe', 
                                       template_filepath='jinjagen/recipe_template.jinja', 
                                       suffix='rst')

    test_runs = [jinjagen_run1]
    app.add_config_value("jinjagen_runs", test_runs, "env")

    return {'version': __version__, 'parallel_read_safe': True}
