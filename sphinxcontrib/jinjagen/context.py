from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast

from jinja2 import Template, Environment, FileSystemLoader
from sphinxcontrib.jinjagen.util import JinjaEnvFactory


class JinjagenContextBase:

    ctxt: Dict[str, Any]
    env_factory: JinjaEnvFactory

    #TODO where to get template dir?? just let it be the templates directory..., directive gives relative filepath
    # def build_file_loader(self, template_filepath: str) -> FileSystemLoader:
    #    return 


