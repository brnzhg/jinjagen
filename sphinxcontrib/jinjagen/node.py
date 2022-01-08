from __future__ import annotations
from _typeshed import NoneType
from typing import NewType, Protocol, Callable, TypeVar, Generic, Mapping, Any, List, Dict, Tuple, Optional, Iterable, Sequence, Generator, Iterator
from typing import ForwardRef
from typing import cast, Type

from abc import ABC, abstractmethod

from dataclasses import dataclass


TNode = TypeVar('TNode', bound='StrKeyNodeBase')
TNodeP = TypeVar('TNodeP', bound='StrKeyNodeBaseP')

class NodeFactory(Protocol[TNode]):
    def __call__(self, key:str, parent: Optional[TNode]) -> TNode: ...


class NodeFactoryReqP(Protocol[TNode]):
    def __call__(self, key:str, parent: TNode) -> TNode: ...


class LookupElseCreateNode(ABC, Generic[TNode]):

    @abstractmethod
    @property
    def lookup_nodes(self) -> Dict[str, TNode]:...

    @abstractmethod 
    def lookup_else_create_node(self, 
        node_key: str, 
        node_factory: NodeFactory[TNode]) -> TNode:...


#ABC dataclass
class StrKeyNodeBase(LookupElseCreateNode[TNode], ABC):

    @abstractmethod
    @property
    def key(self) -> str:...
    
    @abstractmethod
    @property
    def children(self: TNode) -> Dict[str, TNode]: ...

    @property
    def lookup_nodes(self: TNode) -> Dict[str, TNode]: return self.children

    def add_child(self: TNode, child_node: TNode) -> None:
        self.children[child_node.key] = child_node

    def lookup_else_create_child(self: TNode,
                                 child_key: str,
                                 child_factory: NodeFactoryReqP[TNode]) -> TNode:
        if child_key in self.children:
            return self.children[child_key]
        new_child: TNode =  child_factory(child_key, self)
        # self.children[child_key] = new_child
        self.add_child(new_child)
        return new_child

    def lookup_else_create_node(self: TNode,
        node_key: str,
        node_factory: NodeFactory[TNode]) -> TNode:
        return self.lookup_else_create_child(node_key, node_factory)


class StrKeyNodeBaseP(StrKeyNodeBase, ABC):

    @abstractmethod
    @property
    def parent(self: TNodeP) -> Optional[TNodeP]: ...
    
    def to_root_path(self: TNodeP, include_self: bool) -> Generator[TNodeP, None, None]:
        if include_self:
            yield self
        if self.parent:
            yield from self.parent.to_root_path(True)

    def from_root_path(self: TNodeP, include_self: bool) -> Iterator[TNodeP]:
        return reversed(list(self.to_root_path(include_self)))

    def from_root_keypath(self: TNodeP, include_self: bool) -> Iterator[str]:
        return reversed(list(map(lambda x: x.key, self.to_root_path(include_self))))

   
@dataclass
class StrKeyRootNodes(LookupElseCreateNode[TNode]):
    roots: Dict[str, TNode]

    @property
    def lookup_nodes(self) -> Dict[str, TNode]: return self.roots

    @classmethod
    def from_roots_iter(self, roots: Iterable[TNode]) -> StrKeyRootNodes:
        return StrKeyRootNodes({r.key: r for r in roots })

    def add_node(self, new_node: TNode) -> None:
        self.roots[new_node.key] = new_node

    def lookup_else_create_node(self, 
        node_key: str,
        node_factory: NodeFactory[TNode]) -> TNode:
        if node_key in self.roots:
            return self.roots[node_key]
        new_root: TNode = node_factory(node_key, None) 
        self.add_node(new_root)
        return new_root

    def lookup_keypath_else_create(self,
        gen_keypath: List[str], 
        node_factory: NodeFactory[TNode]) -> TNode:
        curr_node: TNode = self.lookup_else_create_node(
            gen_keypath[0], node_factory)
        for gen_key in gen_keypath[1:]:
            curr_node = curr_node.lookup_else_create_child(
                gen_key, node_factory)
        return curr_node

@dataclass
class StrKeyRootNodesP(StrKeyRootNodes[TNodeP]):
    pass
   

# TSelf = TypeVar('TSelf')
# TVal = TypeVar('TVal', covariant=True)


# class HasStrChildrenProtocol(Protocol[TVal]):

#    @property
#    def children(self) -> Mapping[str, StrNodeProtocol[TVal]]:

# class StrNodeProtocol(Protocol[TVal]):

    # @property
    # def children(self: TSelf) -> Mapping[str, TSelf]:

    # @property
    # def children(self) -> Mapping[str, StrNodeProtocol[TVal]]:

    # def is_leaf(self) -> bool:

    # def add_child(self: TSelf, child: TSelf) -> bool:
