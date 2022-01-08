"""
    sphinxcontrib.jinjagen
    ~~~~~~~~~~~~~~~~~~~~~~

    generate multiple rst files from each jinja template

    :copyright: Copyright 2017 by Brian Zhang <brnzhg@gmail.com>
    :license: BSD, see LICENSE for details.
"""

from jinja2.sandbox import SandboxedEnvironment
import pbr.version

# For type annotations
from typing import Any, Dict, List, Optional
from sphinx.application import Sphinx
from sphinxcontrib.jinjagen.util import BuiltinTemplateLoaderEnvFactory, JinjaEnvFactory
from .filegen2 import FileGenRunDef, gen_from_run_defs

__version__ = '1.2.3' #pbr.version.VersionInfo('sphinxcontrib-jinjagen').version_string()

def builder_inited(app: Sphinx) -> None:
    run_defs: Optional[List[FileGenRunDef]] = app.config.jinjagen_runs
    run_env_factory: Optional[JinjaEnvFactory] = app.config.jinjagen_run_env_factory
    if not run_defs or not run_env_factory or not app.env:
        return

    template_env: SandboxedEnvironment = run_env_factory.build_env(app)

    gen_from_run_defs(template_env, run_defs, app.env.srcdir)


# unicode?
def setup(app: Sphinx) -> Dict[str, Any]:
    # app.add_config_value("jinjagen_templates_subdir", "jinjagen", "env") #env?
    # jinjagen_run1 = filegen.FileGenRunDef(gen_keys=[['stew', 'meatball']],
    #                                      name='recipe',
    #                                      template_filepath='jinjagen/recipe_template.jinja',
    #                                      suffix='rst')

    # test_runs = [jinjagen_run1]
    app.add_config_value('jinjagen_runs', [], 'env')
    app.add_config_value('jinjagen_run_env_factory', BuiltinTemplateLoaderEnvFactory(), 'env') #TODO check env
    app.add_config_value('jinjagen_contexts', {}, 'env') #TODO check env
    app.connect('builder-inited', builder_inited)

    return {'version': __version__, 'parallel_read_safe': True}
