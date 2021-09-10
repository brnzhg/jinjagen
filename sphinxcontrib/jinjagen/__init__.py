"""
    sphinxcontrib.jinjagen
    ~~~~~~~~~~~~~~~~~~~~~~

    generate multiple rst files from each jinja template

    :copyright: Copyright 2017 by Brian Zhang <brnzhg@gmail.com>
    :license: BSD, see LICENSE for details.
"""

import pbr.version

# For type annotations
from typing import Any, Dict, List, Optional
from sphinx.application import Sphinx
from .filegen import FileGenRunDef, gen_from_run_defs

__version__ = '1.2.3' #pbr.version.VersionInfo('sphinxcontrib-jinjagen').version_string()

def builder_inited(app: Sphinx) -> None:
    run_defs: Optional[List[FileGenRunDef]] = app.config.jinjagen_runs
    if not run_defs or not app.env:
        return

    gen_from_run_defs(app, run_defs)


# unicode?
def setup(app: Sphinx) -> Dict[str, Any]:
    # app.add_config_value("jinjagen_templates_subdir", "jinjagen", "env") #env?
    # jinjagen_run1 = filegen.FileGenRunDef(gen_keys=[['stew', 'meatball']],
    #                                      name='recipe',
    #                                      template_filepath='jinjagen/recipe_template.jinja',
    #                                      suffix='rst')

    # test_runs = [jinjagen_run1]
    app.add_config_value("jinjagen_runs", [], "env")
    app.add_config_value("jinjagen_contexts", {})
    app.connect('builder-inited', builder_inited)

    return {'version': __version__, 'parallel_read_safe': True}
