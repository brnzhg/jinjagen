from __future__ import annotations
from _typeshed import NoneType
from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast

from dataclasses import dataclass

TSelf = TypeVar('TSelf')
TVal = TypeVar('TVal', covariant=True)


class HasStrChildrenProtocol(Protocol[TVal]):
 
    @property
    def children(self) -> Mapping[str, StrNodeProtocol[TVal]]:
        ...

   


class StrNodeProtocol(Protocol[TVal]):
    key: str
    parent: StrNodeProtocol

    #@property
    #def children(self: TSelf) -> Mapping[str, TSelf]:
    #    ...

    @property
    def children(self) -> Mapping[str, StrNodeProtocol[TVal]]:
        ...

    def is_leaf(self) -> bool:
        return not self.children

    def add_child(self: TSelf, child: TSelf) -> bool:
        ...

    def remove_child(self, child_key: str) -> bool:
        ...

    
    
    

class StrKeyNode(StrNodeProtocol[TVal]):
    key: str
    children: Dict[str, StrKeyNode]

    def __init__(self, key: str, children: Dict[str, StrKeyNode[TVal]]):
        self.key = key
        self.children = children
    
def stupid_func(bob: StrNodeProtocol[TVal]) -> None:
    return

# bobby: StrKeyNode[str] = StrKeyNode('bob', { 'cheese': StrKeyNode('cheese', {}) })
# stupid_func(bobby)
    

# class GStrNode(Generic[TVal]):
#    key: str
#    children: Dict[str, GStrNode[TVal]]



