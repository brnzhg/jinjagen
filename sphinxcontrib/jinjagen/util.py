from __future__ import annotations
from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast

from dataclasses import dataclass

from jinja2 import Template
from jinja2.sandbox import SandboxedEnvironment
from sphinx.application import Sphinx
# from sphinx.util.osutil import ensuredir
from sphinx.util.logging import getLogger
from sphinx.jinja2glue import BuiltinTemplateLoader


class JinjaEnvFactory(Protocol):

    def build_env(self, app: Sphinx) -> SandboxedEnvironment:
        ...

# TODO see autoapi for adding other directory to loader
class BuiltinTemplateLoaderEnvFactory(JinjaEnvFactory):

    #TODO can take in 
    
    def build_env(self, app: Sphinx) -> SandboxedEnvironment:
        template_loader = BuiltinTemplateLoader()
        template_loader.init(app.builder) #type: ignore
        return SandboxedEnvironment(loader=template_loader)
        # env.filters.update(conf.jinja_filters)
        # env.tests.update(conf.jinja_tests)
        # env.globals.update(conf.jinja_globals)
        # env.policies.update(conf.jinja_policies)


    
