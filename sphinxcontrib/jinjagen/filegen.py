from __future__ import annotations
from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast

from collections import deque
from pathlib import Path
from enum import Enum

from dataclasses import dataclass

from jinja2 import Template
from jinja2.sandbox import SandboxedEnvironment
from sphinx.application import Sphinx
# from sphinx.util.osutil import ensuredir
from sphinx.util.logging import getLogger
from sphinx.jinja2glue import BuiltinTemplateLoader

logger = getLogger(__name__)

#TODO make generic tree, lookup keys in one in other
@dataclass
class GenKeyNode:
    key: str
    children: List[GenKeyNode]


class FileGenRunNameOption(Enum):
    ALL_KEYS_DIRS = 1,
    ALWAYS_PREPEND_LAST_KEY = 2,
    PREPEND_LAST_KEY_FOR_SINGLE_ENTRY = 3


@dataclass
class FileGenRunDef:
    gen_key_roots: List[GenKeyNode]
    name: str
    template_filepath: str
    suffix: str
    name_option: FileGenRunNameOption
    base_dir: Optional[str]

    def entry_filepath_from_key_path(self, src_dir: str, from_root_keypath: List[str]) -> Path:
        # return Path(base_dir, *from_root_keypath, f'{self.name}.{self.suffix}')
        dirs_to_use: Iterable[str]
        filename_to_use: str
        if from_root_keypath and True:
            dirs_to_use = from_root_keypath[:-1]
            filename_to_use = f'{from_root_keypath[-1]}_{self.name}'
        else:
            dirs_to_use = from_root_keypath
            filename_to_use = self.name

        if self.base_dir:
            return Path(src_dir, self.base_dir, *dirs_to_use, filename_to_use)
        return Path(src_dir, *dirs_to_use, filename_to_use)


    def create_run_data(self, template_env: SandboxedEnvironment) -> FileGenRunData:
        return FileGenRunData(self, template_env.get_template(self.template_filepath))




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

    def from_root_keypath(self, include_self: bool):
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

    def lookup_keypath_else_create(self, gen_keypath: List[str]) -> FileGenNode:
        curr_node: FileGenNode = self.lookup_else_create_node(gen_keypath[0])
        for gen_key in gen_keypath[1:]:
            curr_node = curr_node.lookup_else_create_child(gen_key)
        return curr_node


# take out of tree, just needed for context, should be generated by Node and Run, for each key
@dataclass
class FileGenRunEntry:
    # name: str
    gen_key: str
    run_data: FileGenRunData # same for all entries under same name
    filepath: Path # can be calculated, run output_dir + parent parent parent to root, combine gen_keys


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
        return self.gen_run_entry.run_data.template.render(self.get_render_kwargs())


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
    template_loader.init(app.builder) # type: ignore
    template_env = SandboxedEnvironment(loader=template_loader)
    # template_env.filters['summary'] = filter_summary
    return template_env

#LookupElseCreateNode = Callable[[str], FileGenNode]

def update_gen_tree(src_dir: str, gen_roots: FileGenRoots, run_data: FileGenRunData) -> None:
    @dataclass
    class UpdateGenTreeElt:
        lookup_else_create_node: Callable[[str], FileGenNode]
        key_node: GenKeyNode

    run_def: FileGenRunDef = run_data.run_def
    q: deque[UpdateGenTreeElt] = deque(UpdateGenTreeElt(
        gen_roots.lookup_else_create_node, key_node) for key_node in run_def.gen_key_roots)

    while q:
        elt: UpdateGenTreeElt = q.pop()

        lookup_file_node: FileGenNode = elt.lookup_else_create_node(elt.key_node.key)
        if elt.key_node.children:
            for child_key_node in elt.key_node.children:
                q.appendleft(UpdateGenTreeElt(lookup_file_node.lookup_else_create_child,
                                              child_key_node))
        else:
            lookup_file_node.run_entry_by_name[run_def.name] = FileGenRunEntry(
                gen_key=elt.key_node.key,
                run_data=run_data,
                filepath=run_def.entry_filepath_from_key_path(src_dir,
                                                              lookup_file_node.from_root_keypath(include_self=True)))

# TODO generate tree in two steps, first step mark everything out, second one create run entries with filepaths
# maybe create the tree without any entries, just nodes. Then add entries after
def gen_tree_from_runs(src_dir: str, runs: List[FileGenRunData]) -> FileGenRoots:
    gen_roots: FileGenRoots = FileGenRoots({})

    for run_data in runs:
        update_gen_tree(src_dir, gen_roots, run_data)
    return gen_roots


def render_and_write_gen_node(
    gen_roots: FileGenRoots,
    gen_node: FileGenNode) -> None:
    for name, run_entry in gen_node.run_entry_by_name.items():

        # gen_node.children_by_gen_key

        # try:
        name_ctxt = FileContext(gen_node, gen_roots, run_entry)

        try:
            run_entry.filepath.parent.mkdir(exist_ok=True, parents=True)
            run_entry.filepath.write_text(name_ctxt.render())
        except Exception as ex:
            logger.error('wtf')
            raise ex
        # except Exception as ex:
        #   logger.error( 'Error %s'.format(format_exception(Exception, ex)))


def render_and_write_gen_tree(gen_roots: FileGenRoots) -> None:
    q: deque[FileGenNode] = deque(gen_roots.nodes_by_gen_key.values())

    # bfs
    while q:
        elmt = q.pop()
        render_and_write_gen_node(gen_roots, elmt)

        for elmt_child in elmt.children_by_gen_key.values():
            q.appendleft(elmt_child)


def gen_from_run_defs(app: Sphinx, run_defs: List[FileGenRunDef]) -> FileGenRoots:
    template_env: SandboxedEnvironment = get_template_env(app)

    # fetch run templates
    runs: List[FileGenRunData] = [run_def.create_run_data(template_env) for run_def in run_defs]

    # gen tree with output filepaths
    assert app.env is not None
    gen_roots: FileGenRoots = gen_tree_from_runs(str(app.env.srcdir), runs)

    # render and write
    render_and_write_gen_tree(gen_roots)
    return gen_roots

# TODO
# get version to work
# add back source directories for each run
# make generic tree, rename key to be special key
# create both context tree and run tree - runs easy lookup into context tree
#    run has override base keys
# so run can start at non base key, context never needs this i think, just purely needs keys, can have extra keys

# note any node can look up a context is how it will work, may be name, may be no name

# filepath options for name, key, etc
# if only thing for key, allow it not to create dir
# allow key to be appended to name
# allow force no create dir, and error if conflict

# environment holds object with contract
# contract can produce all the runs and stuff
#   so db can be accessed there on build-init

# TODO test toc

# option to run without build init... and mark files as "generated"
#   maybe just need command argument to not generate
#   add prefix of sorts, allows generating mingle with not generated
#   add parent template that displays generated time

    

    
