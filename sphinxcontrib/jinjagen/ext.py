from __future__ import annotations
from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast

from collections import deque, defaultdict
# from pathlib import Path
from traceback import format_exception

from dataclasses import dataclass

from jinja2 import Template
from jinja2.sandbox import SandboxedEnvironment

from docutils.parsers.rst import directives
from docutils.nodes import Element, Node, TextElement, system_message


from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, Index
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.util import ws_re

from sphinx.application import Sphinx
# from sphinx.util.osutil import ensuredir
from sphinx.util.logging import getLogger
from sphinx.jinja2glue import BuiltinTemplateLoader



# Jinja directive, point to file by key?

# pointing to file:
# https://github.com/sphinx-doc/sphinx/blob/80b0a16e1c5f7266522a50284a003a0e17cf5ff7/sphinx/roles.py

class JinjagenGenDocRefRole(XRefRole):
    def process_link(self,
                    env: "BuildEnvironment", 
                    refnode: Element, 
                    has_explicit_title: bool,
                    title: str, 
                    target: str) -> Tuple[str, str]:
        """Called after parsing title and target text, and creating the
        reference node (given in *refnode*).  This method can alter the
        reference node and must return a new (or the same) ``(title, target)``
        tuple.
        """
        #self.env.gentree
        # target split on .
        # look up keys in gen tree
        # get absolute filepath of gentree
        # return title, ws_re.sub(' ', filepath)
        # ws_re is white space regex, replaces whitespace with ' '

        return title, ws_re.sub(' ', target)



# XRefRole child class which helps do Key1.Key2.

# how xrefrole and :doc: work 
# https://github.com/sphinx-doc/sphinx/blob/80b0a16e1c5f7266522a50284a003a0e17cf5ff7/sphinx/domains/std.py

class JinjagenDomain(Domain):

    name = 'jinja'
    label = 'jinjagen'
    roles = {
        'genref': XRefRole() # reference to generated document
    }



    

