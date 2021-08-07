from __future__ import annotations
from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast

from collections import deque, defaultdict
from pathlib import Path
from traceback import format_exception

from dataclasses import dataclass

from jinja2 import Template
from jinja2.sandbox import SandboxedEnvironment
from sphinx.application import Sphinx, Builder
# from sphinx.util.osutil import ensuredir
from sphinx.util.logging import getLogger
from sphinx.jinja2glue import BuiltinTemplateLoader

logger = getLogger(__name__)

#TODO make generic tree, lookup keys in one in other
@dataclass
class GenKeyNode:
    key: str
    children: List[GenKeyNode]

@dataclass
class FileGenRunDef:
    gen_key_roots: List[GenKeyNode]
    name: str
    template_filepath: str
    # output_dir: str
    suffix: str

@dataclass
class FileGenRunData:
    run_def: FileGenRunDef
    template: Template

@dataclass
class FileGenNode:
    gen_key: str
    parent: Optional[FileGenNode]
    children_by_gen_key: Dict[str, FileGenNode]
    run_entry_by_name: Dict[str, FileGenRunEntry]

    def lookup_else_create_child(self, child_gen_key: str) -> FileGenNode:
        if child_gen_key in self.children_by_gen_key:
            return self.children_by_gen_key[child_gen_key]
        new_child: FileGenNode = FileGenNode(child_gen_key, self, {}, {})
        self.children_by_gen_key[child_gen_key] = new_child
        return new_child

    def to_root_path(self, include_self: bool) -> Generator[FileGenNode, None, None]:
        if include_self:
            yield self
        if self.parent:
            yield from self.parent.to_root_path(True)

    def from_root_path(self, include_self: bool) -> Iterator[FileGenNode]:
        return reversed(list(self.to_root_path(include_self)))

    def from_root_keys(self, include_self: bool):
        return reversed(list(map(lambda x: x.gen_key, self.to_root_path(include_self))))


@dataclass
class FileGenRoots:
    nodes_by_gen_key: Dict[str, FileGenNode]

    def lookup_else_create_node(self, gen_key:str) -> FileGenNode:
        if gen_key in self.nodes_by_gen_key:
            return self.nodes_by_gen_key[gen_key]
        new_node: FileGenNode = FileGenNode(gen_key, None, {}, {})
        self.nodes_by_gen_key[gen_key] = new_node
        return new_node

    def lookup_key_path_else_create(self, gen_key_path: List[str]) -> FileGenNode:
        curr_node: FileGenNode = self.lookup_else_create_node(gen_key_path[0])
        for gen_key in gen_key_path[1:]:
            curr_node = curr_node.lookup_else_create_child(gen_key)
        return curr_node






# take out of tree, just needed for context, should be generated by Node and Run, for each key
@dataclass
class FileGenRunEntry:
    # name: str
    gen_key: str
    run_data: FileGenRunData # same for all entries under same name
    filepath: Path # can be calculated, run output_dir + parent parent parent to root, combine gen_keys


def get_file_gen_run_entry_path(src_dir: str, run: FileGenRunDef, from_root_keys: List[str]) -> Path:
    return Path(src_dir, *from_root_keys, f'{run.name}.{run.suffix}')

def get_run_data(run_def: FileGenRunDef, template_env: SandboxedEnvironment) -> FileGenRunData:
    return FileGenRunData(run_def, template_env.get_template(run_def.template_filepath))


# def create_file_gen_run_entry(src_dir: str,
#                               run: FileGenRunDef, 
#                               from_root_keys: List[str]) -> FileGenRunEntry:
#    run_entry_path: Path = Path(src_dir, *from_root_keys, f'{run.name}.{run.suffix}')
#    return FileGenRunEntry(run, run_entry_path)


@dataclass
class FileContext:
    gen_node: FileGenNode
    gen_roots: FileGenRoots
    gen_run_entry: FileGenRunEntry # dont need name, on FileGenEntry

    def get_render_kwargs(self) -> Dict[str, Any]:
        return {
            'gen_node': self.gen_node
            , 'gen_roots': self.gen_roots
            , 'gen_run_entry': self.gen_run_entry
        }

    def render(self) -> str:
        return self.gen_run_entry.run_data.template.render(self.get_render_kwargs)


# copied from autoapi - https://github.com/carlos-jenkins/autoapi/blob/master/lib/autoapi/sphinx.py
def get_template_env(app: Sphinx) -> SandboxedEnvironment:
    """
    Get the template environment.
    .. note::
       Template should be loaded as a package_data using
       :py:function:`pkgutil.get_data`, but because we want the user to
       override the default template we need to hook it to the Sphinx loader,
       and thus a file system approach is required as it is implemented like
       that.
    """
    #template_dir = [join(dirname(abspath(__file__)), 'templates')]
    template_loader = BuiltinTemplateLoader()
    template_loader.init(cast(Builder, app.builder)) # dirs = template_dir
    template_env = SandboxedEnvironment(loader=template_loader)
    # template_env.filters['summary'] = filter_summary
    return template_env


# TODO get filepath from context instead??
def update_gen_tree(gen_roots: FileGenRoots, run_data: FileGenRunData) -> None:

    q: deque[Tuple[FileGenNode, GenKeyNode]] = deque()

    for gen_key_root in run_data.run_def.gen_key_roots:
        root_node = gen_roots.lookup_else_create_node(gen_key_root.key)
        if gen_key_root.children:
            for child_key_node in gen_key_root.children:
                q.appendleft((root_node, child_key_node))
        else:
            root_node.run_entry_by_name[run_data.run_def.name] = FileGenRunEntry(
                gen_key=gen_key_root.key
                , run_data=run_data
                , filepath=get_file_gen_run_entry_path(None, run_data.run_def, None))

    while q:
        e_file_node: FileGenNode
        e_key_node: GenKeyNode
        e_file_node, e_key_node = q.pop()

        lookup_file_node = e_file_node.lookup_else_create_child(e_key_node.key)
        if e_key_node.children:
            for child_key_node in e_key_node.children:
                q.appendleft((lookup_file_node, child_key_node))
        else:
            lookup_file_node.run_entry_by_name[run_data.run_def.name] = FileGenRunEntry(
                gen_key=e_key_node.key
                , run_data=run_data
                , filepath=None)






def gen_tree_from_runs(file_gen_runs: List[FileGenRunDef]) -> FileGenRoots:
    pass

def render_and_write_gen_node(
    gen_roots: FileGenRoots,
    gen_node: FileGenNode) -> None:
    for name, run_entry in gen_node.run_entry_by_name.items():

        gen_node.children_by_gen_key

        # try:
        name_ctxt = FileContext(gen_node, gen_roots, run_entry)

        run_entry.filepath.parent.mkdir(exist_ok=True, parents=True)
        run_entry.filepath.write_text(name_ctxt.render())
        # except Exception as ex:
        #   logger.error( 'Error %s'.format(format_exception(Exception, ex)))


def render_and_write_gen_tree(root_dir: str, gen_roots: FileGenRoots, template: Template) -> None:
    q: deque[FileGenNode] = deque(gen_roots.nodes_by_gen_key.values())

    # bfs
    while q:
        elmt = q.pop()
        render_and_write_gen_node(gen_roots, elmt)

        for elmt_child in elmt.children_by_gen_key.values():
            q.appendleft(elmt_child)

    