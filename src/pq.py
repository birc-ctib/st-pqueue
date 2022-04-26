"""A priority queue based on a search tree."""

from __future__ import annotations
from typing import (
    Generic, TypeVar, Protocol,
    Iterable, Iterator, Optional,
    Any,
)
from dataclasses import dataclass
from itertools import chain

# Defining what it means to be ordered and set up T
# so we can use it to mean an ordered type


class Ordered(Protocol):
    """Protocol for ordered types."""

    def __lt__(self, other: Any) -> bool:
        """Is self less than other."""
        ...


T = TypeVar('T', bound=Ordered)


# Define nodes so we can define trees
@dataclass
class Node(Generic[T]):
    """Inner node in a search tree."""

    value: T
    left: Tree[T] = None
    right: Tree[T] = None


Tree = Optional[Node[T]]

# Operations on nodes. Later wrapped for a SearchTree


def contains(tree: Tree[T], val: T) -> bool:
    """Insert val into this tree."""
    if tree is None:
        return False
    if val < tree.value:
        return contains(tree.left, val)
    if val > tree.value:
        return contains(tree.right, val)
    return True


def insert(tree: Tree[T], val: T) -> Node[T]:
    """Insert val into this tree."""
    if tree is None:
        return Node(val)
    if val < tree.value:
        return Node(tree.value, insert(tree.left, val), tree.right)
    if val > tree.value:
        return Node(tree.value, tree.left, insert(tree.right, val))
    return tree


def rightmost(tree: Node[T]) -> T:
    """Get the rightmost value in a non-empty tree."""
    while tree.right:
        tree = tree.right
    return tree.value


def remove(tree: Tree[T], val: T) -> Tree[T]:
    """Remove val from tree."""
    if tree is None:
        return None

    if val < tree.value:
        return Node(tree.value, remove(tree.left, val), tree.right)
    if val > tree.value:
        return Node(tree.value, tree.left, remove(tree.right, val))

    # tree.value == val
    if tree.left is None:
        return tree.right
    if tree.right is None:
        return tree.left

    rm_val = rightmost(tree.left)
    return Node(rm_val, remove(tree.left, rm_val), tree.right)


def iterate(tree: Tree[T]) -> Iterator[T]:
    """Iterate over all the tree's values."""
    if tree is not None:
        yield from iterate(tree.left)
        yield tree.value
        yield from iterate(tree.right)

# Interface to a search tree


@dataclass(init=False)
class SearchTree(Generic[T]):
    """A search tree."""

    root: Tree[T]

    def __init__(self, data: Iterable[T] = (), tree: Tree[T] = None):
        """
        Build a search tree from data.

        We build it by inserting nodes one at a time,
        so the construction time is O(n log n) if data has n elements.

        If you provide a tree to the `tree` argument, it is used
        as the initial tree. This gives you a way of constructing
        a SearchTree object from a Tree object.
        """
        self.root = tree
        for x in data:
            self.insert(x)

    def __contains__(self, val: T) -> bool:
        """Test if val is in this tree."""
        return contains(self.root, val)

    def insert(self, val: T) -> None:
        """Insert val into this tree."""
        self.root = insert(self.root, val)

    def remove(self, val: T) -> None:
        """Remove val from this tree."""
        self.root = remove(self.root, val)

    def __iter__(self) -> Iterator[T]:
        """Iterate over all the tree's values."""
        yield from iterate(self.root)

    def __bool__(self) -> bool:
        """Test for emptiness as a bool."""
        return self.root is not None


def st_sort(x: Iterable[T]) -> Iterator[T]:
    """
    Sort the elements in x using a search tree.

    We can do this by simply inserting all the elements
    into a search tree and then run through it in-order.
    """
    return iter(SearchTree(x))

# And now for the priority queue


class PriorityQueue(SearchTree[T]):
    """Priority queue implemented using a search tree."""

    @property
    def min_val(self) -> T:
        """Return the smallest value."""
        # FIXME
        tree = self.root
        assert tree is not None, "Tree can't be empty for min_val"
        while tree.left is not None:
            tree = tree.left
        return tree.value

    def delete_min(self) -> T:
        # FIXME
        """Delete the smallest value (and return it)."""
        min_val = self.min_val
        self.remove(min_val)
        return min_val


def pq_sort(x: Iterable[T]) -> Iterator[T]:
    """Sort x using a priority queue."""
    # FIXME
    # You can do by iteratively extract `delete_min`.
    # With this implementation, of course, you can just
    # call st_sort(), since your priority queue is also
    # a search tree, but I want you to implement a sort
    # that uses `delete_min``. Such a solution would work
    # with *any* data structure that provides `delete_min`
    # and not just this search tree based one.
    t = PriorityQueue(x)
    y = []
    while t:
        y.append(t.delete_min())
    return iter(y)


# Merging
def general_merge(
    x: PriorityQueue[T], y: PriorityQueue[T]
) -> PriorityQueue[T]:
    """
    Merge x and y into a new priority queue.

    You don't have to do this persistently, leaving x and y
    unchanged, but the implementation above does allow for it
    in the same running time.
    """
    # FIXME
    # In the general case, I can't do much better than building a completely
    # new priority queue. A little better, but not much. Here's a complete
    # rebuild. The running time is (len(x)+len(y)) log(len(x)+len(y))
    return PriorityQueue(chain(iter(x), iter(y)))


def general_merge2(
    x: PriorityQueue[T], y: PriorityQueue[T]
) -> PriorityQueue[T]:
    """
    Merge x and y into a new priority queue.

    You don't have to do this persistently, leaving x and y
    unchanged, but the implementation above does allow for it
    in the same running time.
    """
    # With a complete rebuild we are inserting the elements from x and y into
    # an increasingly larger tree, but after inserting all the elements in
    # x we are just back to the original x structure. If we started from there
    # we would only spend O(len(y) log(len(x)+len(y))) on inserting y's
    # elements into x. If we knew the sizes of x and y in constant time--we
    # could keep track of it in the insertion and deletion operations, we
    # should always insert the smaller into the larger.
    tree = x.root
    for z in iter(y):
        tree = insert(tree, z)
    return PriorityQueue(tree=tree)


def special_merge(
    x: PriorityQueue[T], y: PriorityQueue[T]
) -> PriorityQueue[T]:
    """
    Merge x and y into a new priority queue.

    You can assume that the largest value in x is smaller than
    the smallest value in y.

    You don't have to do this persistently, leaving x and y
    unchanged, but the implementation above does allow for it
    in the same running time.
    """
    largest_x = rightmost(x.root)
    smallest_y = y.min_val
    assert largest_x < smallest_y
    # FIXME
    # We can pull up the largest value in x (and remove it)
    # from that tree, then put the largest value in the root
    # of a new tree with x minus largest on the left and
    # y on the right. This takes time O(log n) for getting
    # and removing x's largest value.
    tree = Node(
        largest_x,
        remove(x.root, largest_x),
        y.root
    )
    return PriorityQueue(tree=tree)
