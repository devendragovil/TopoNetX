"""Module with views.

Such as:
HyperEdgeView, CellView, SimplexView, NodeView.
"""
from collections.abc import Collection, Hashable, Iterable, Iterator, Sequence
from itertools import chain
from typing import Any, Literal

from toponetx.classes.cell import Cell
from toponetx.classes.hyperedge import HyperEdge
from toponetx.classes.path import Path
from toponetx.classes.simplex import Simplex

__all__ = [
    "HyperEdgeView",
    "ColoredHyperEdgeView",
    "CellView",
    "SimplexView",
    "NodeView",
]


class CellView:
    """A CellView class for cells of a CellComplex.

    Parameters
    ----------
    name : str, optional
        The name of the cell view.
    """

    def __init__(self, name: str = "") -> None:
        """Initialize an object for the CellView class for cells of a CellComplex.

        Parameters
        ----------
        name : str, optional
            The name of the cell view.
        """
        self.name = name

        # Initialize a dictionary to hold cells, with keys being the tuple
        # that defines the cell, and values being dictionaries of cell objects
        # with different attributes
        self._cells: dict[tuple[Hashable, ...], dict[int, Cell]] = {}

    def __getitem__(self, cell):
        """Return the attributes of a given cell.

        Parameters
        ----------
        cell : tuple list or cell
            The cell of interest.

        Returns
        -------
        dict or list of dicts
            The attributes associated with the cell.

        Raises
        ------
        KeyError
            If the cell is not in the cell dictionary.
        """
        if isinstance(cell, Cell):
            if cell.elements not in self._cells:
                raise KeyError(
                    f"cell {cell.__repr__()} is not in the cell dictionary",
                )

            # If there is only one cell with these elements, return its attributes
            elif len(self._cells[cell.elements]) == 1:
                k = next(iter(self._cells[cell.elements].keys()))
                return self._cells[cell.elements][k]._attributes

            # If there are multiple cells with these elements, return the attributes of all cells
            else:
                return [
                    self._cells[cell.elements][c]._attributes
                    for c in self._cells[cell.elements]
                ]

        # If a tuple or list is passed in, assume it represents a cell
        elif isinstance(cell, (tuple, list)):
            cell = tuple(cell)
            if cell in self._cells:
                if len(self._cells[cell]) == 1:
                    k = next(iter(self._cells[cell].keys()))
                    return self._cells[cell][k]._attributes
                else:
                    return [self._cells[cell][c]._attributes for c in self._cells[cell]]
            else:
                raise KeyError(f"cell {cell} is not in the cell dictionary")

        else:
            raise TypeError("Input must be a tuple, list or a cell.")

    def raw(self, cell: tuple | list | Cell) -> Cell | list[Cell]:
        """Index the raw cell objects analogous to the overall index of CellView.

        Parameters
        ----------
        cell : tuple, list, or cell
            The cell of interest.

        Returns
        -------
        Cell or list of Cells
            The raw Cell objects.
            If more than one cell with the same boundary exists, returns a list;
            otherwise a single cell.

        Raises
        ------
        KeyError
            If the cell is not in the cell dictionary.
        """
        if isinstance(cell, Cell):
            if cell.elements not in self._cells:
                raise KeyError(f"cell {cell.__repr__()} is not in the cell dictionary")

            # If there is only one cell with these elements, return its attributes
            elif len(self._cells[cell.elements]) == 1:
                k = next(iter(self._cells[cell.elements].keys()))
                return self._cells[cell.elements][k]

            # If there are multiple cells with these elements, return the attributes of all cells
            else:
                return [
                    self._cells[cell.elements][c] for c in self._cells[cell.elements]
                ]

        # If a tuple or list is passed in, assume it represents a cell
        elif isinstance(cell, (tuple, list)):
            cell = tuple(cell)
            if cell in self._cells:
                if len(self._cells[cell]) == 1:
                    k = next(iter(self._cells[cell].keys()))
                    return self._cells[cell][k]
                else:
                    return [self._cells[cell][c] for c in self._cells[cell]]
            else:
                raise KeyError(f"cell {cell} is not in the cell dictionary")

        else:
            raise TypeError("Input must be a tuple, list or a cell.")

    def __len__(self) -> int:
        """Return the number of cells in the cell view.

        Returns
        -------
        int
            The number of cells in the cell view.
        """
        return sum(len(self._cells[cell]) for cell in self._cells)

    def __iter__(self) -> Iterator:
        """Iterate over all cells in the cell view.

        Returns
        -------
        Iterator
            Iterator to iterate over all cells in the cell view.
        """
        return iter(
            [
                self._cells[cell][key]
                for cell in self._cells
                for key in self._cells[cell]
            ]
        )

    def __contains__(self, e: tuple | list | Cell) -> bool:
        """Check if a given element is in the cell view.

        Parameters
        ----------
        e : tuple, list, or cell
            The element to check.

        Returns
        -------
        bool
            Whether or not the element is in the cell view.
        """
        while True:
            if isinstance(e, (Cell, tuple, list)):
                break
            raise TypeError("Input must be of type: tuple, list or a cell.")

        e = Cell(e)
        e_homotopic_to = [e.is_homotopic_to(x) for x in self._cells]
        return any(e_homotopic_to)

    def __repr__(self) -> str:
        """Return a string representation of the cell view.

        Returns
        -------
        str
            The __repr__ representation of the cell view.
        """
        return f"CellView({[self._cells[cell][key] for cell in self._cells for key in  self._cells[cell]] })"

    def __str__(self) -> str:
        """Return a string representation of the cell view.

        Returns
        -------
        str
            The __str__ representation of the cell view.
        """
        return f"CellView({[self._cells[cell][key] for cell in self._cells for key in  self._cells[cell]] })"


class ColoredHyperEdgeView:
    """A class for viewing the cells/hyperedges of a colored hypergraph.

    Provides methods for accessing, and retrieving
    information about the cells/hyperedges of a complex.

    Parameters
    ----------
    name : str, optional
        The name of the view.

    Examples
    --------
    >>> hev = ColoredHyperEdgeView()
    """

    def __init__(self, name: str = "") -> None:
        """Initialize a new instance of the ColoredHyperEdgeView class.

        Parameters
        ----------
        name : str, optional
            The name of the view.

        Examples
        --------
        >>> hev = ColoredHyperEdgeView()
        """
        self.name = name
        self.hyperedge_dict = {}

    def __getitem__(self, hyperedge):
        """Get item.

        Parameters
        ----------
        hyperedge : Hashable or ColoredHyperEdge
            DESCRIPTION.

        Returns
        -------
        dict or list or dicts
            Return dict of attributes associated with that hyperedges.
        """
        if isinstance(hyperedge, Iterable):
            if len(hyperedge) == 2:
                if isinstance(hyperedge[0], Iterable) and isinstance(hyperedge[1], int):
                    hyperedge_elements, key = hyperedge
                else:
                    raise KeyError(
                        "Input hyperedge must of the form (Iterable representing elements of hyperedge, key)"
                    )
        hyperedge = HyperEdgeView()._to_frozen_set(hyperedge_elements)
        hyperedge_elements = hyperedge
        rank = self.get_rank(hyperedge_elements)
        return self.hyperedge_dict[rank][hyperedge_elements][key]

    @property
    def shape(self) -> tuple[int, ...]:
        """Compute shape.

        Returns
        -------
        tuple[int, ...]
            The shape of the ColoredHyperEdge.
        """
        shape = []
        for i in self.allranks:
            sm = sum([len(self.hyperedge_dict[i][k]) for k in self.hyperedge_dict[i]])
            shape.append(sm)
        return tuple(shape)

    def __len__(self) -> int:
        """Compute the number of nodes.

        Returns
        -------
        int
            The number of nodes in the ColoredHyperEdge.
        """
        return sum(self.shape[1:])

    def __iter__(self) -> Iterator:
        """Iterate over the hyperedges.

        Returns
        -------
        Iterator
            The iterator to iterate over the hyperedges.
        """
        lst = []
        for r in self.hyperedge_dict:
            if r == 0:
                continue
            else:
                for he in self.hyperedge_dict[r]:
                    for k in self.hyperedge_dict[r][he]:
                        lst.append((he, k))
        return iter(lst)

    def __contains__(self, hyperedge: Collection) -> bool:
        """Check if hyperedge is in the hyperedges.

        Parameters
        ----------
        hyperedge : Collection
            The hyperedge to check.

        Returns
        -------
        bool
            Return `True` if the hyperedge is contained within the hyperedges.

        Notes
        -----
        Assumption of input here hyperedge = ( elements of hyperedge, key of hyperedge)
        """
        if len(self.hyperedge_dict) == 0:
            return False
        if isinstance(hyperedge, Iterable):
            if len(hyperedge) == 0:
                return False
            if len(hyperedge) == 2:
                if isinstance(hyperedge, HyperEdge):
                    hyperedge_elements = hyperedge.elements
                    key = 0
                elif isinstance(hyperedge[0], Iterable) and isinstance(
                    hyperedge[1], int
                ):
                    hyperedge_elements_ = hyperedge[0]
                    if not isinstance(hyperedge_elements_, HyperEdge):
                        hyperedge_elements, key = hyperedge
                    else:
                        _, key = hyperedge
                        hyperedge_elements = hyperedge_elements_.elements
                else:
                    hyperedge_elements = hyperedge
                    key = 0
            else:
                hyperedge_elements = hyperedge
                key = 0
            all_ranks = self.allranks
        else:
            return False
        if isinstance(hyperedge_elements, Iterable) and not isinstance(
            hyperedge_elements, HyperEdge
        ):
            if len(hyperedge_elements) == 0:
                return False
            else:
                for i in all_ranks:
                    if frozenset(hyperedge_elements) in self.hyperedge_dict[i]:
                        if key in self.hyperedge_dict[i][frozenset(hyperedge_elements)]:
                            return True
                        else:
                            return False
                return False
        elif isinstance(hyperedge_elements, HyperEdge):
            if len(hyperedge_elements) == 0:
                return False
            else:
                for i in all_ranks:
                    if frozenset(hyperedge_elements.elements) in self.hyperedge_dict[i]:
                        return True
                return False

    def __repr__(self) -> str:
        """Return string representation of hyperedges.

        Returns
        -------
        str
            The __repr__ string representation of the hyperedges.
        """
        return f"ColoredHyperEdgeView({[(tuple(x[0]),x[1]) for x in self]})"

    def __str__(self) -> str:
        """Return string representation of hyperedges.

        Returns
        -------
        str
            The __str__ string representation of the hyperedges.
        """
        return f"ColoredHyperEdgeView({[(tuple(x[0]),x[1]) for x in self]})"

    def skeleton(self, rank: int, store_hyperedge_key: bool = True):
        """Skeleton of the complex.

        Parameters
        ----------
        rank : int
            Rank of the skeleton.
        store_hyperedge_key : bool, default=True
            Whether to return the hyperedge key or not.

        Returns
        -------
        list of frozensets
            The skeleton of rank `rank`.
        """
        if rank not in self.hyperedge_dict:
            return []
        if store_hyperedge_key:
            return sorted(
                [
                    (he, k)
                    for he in self.hyperedge_dict[rank]
                    for k in self.hyperedge_dict[rank][he]
                ]
            )
        else:
            return sorted(
                [
                    he
                    for he in self.hyperedge_dict[rank]
                    for k in self.hyperedge_dict[rank][he]
                ]
            )

    def get_rank(self, edge):
        """Get the rank of a given hyperedge.

        Parameters
        ----------
        edge : Iterable, Hashable or ColoredHyperEdge
            The edge for which to get the rank.

        Returns
        -------
        int
            The rank of the given colored hyperedge.
        """
        if isinstance(edge, HyperEdge):
            if len(edge) == 0:
                return 0
            else:
                for i in list(self.allranks):
                    if frozenset(edge.elements) in self.hyperedge_dict[i]:
                        return i
                raise KeyError(f"hyperedge {edge.elements} is not in the complex")
        elif isinstance(edge, str):
            if frozenset({edge}) in self.hyperedge_dict[0]:
                return 0
            else:
                raise KeyError(f"hyperedge {frozenset({edge})} is not in the complex")
        elif isinstance(edge, Iterable):
            if len(edge) == 0:
                return 0
            else:
                for i in list(self.allranks):
                    if frozenset(edge) in self.hyperedge_dict[i]:
                        return i
                raise KeyError(f"hyperedge {edge} is not in the complex")
        elif isinstance(edge, Hashable) and not isinstance(edge, Iterable):
            if frozenset({edge}) in self.hyperedge_dict[0]:
                return 0
            else:
                raise KeyError(f"hyperedge {frozenset({edge})} is not in the complex")

    @property
    def allranks(self) -> list[int]:
        """All ranks.

        Returns
        -------
        list[int]
            The sorted list of all ranks.
        """
        return sorted(self.hyperedge_dict.keys())


class HyperEdgeView:
    """A class for viewing the cells/hyperedges of a combinatorial complex.

    Provides methods for accessing, and retrieving
    information about the cells/hyperedges of a complex.

    Parameters
    ----------
    name : str, optional
        The name of the view.

    Examples
    --------
    >>> hev = HyperEdgeView()
    """

    def __init__(self, name: str = "") -> None:
        """Initialize an instance of the class for viewing the cells/hyperedges of a combinatorial complex.

        Provides methods for accessing, and retrieving
        information about the cells/hyperedges of a complex.

        Parameters
        ----------
        name : str, optional
            The name of the view.

        Examples
        --------
        >>> hev = HyperEdgeView()
        """
        self.name = name
        self.hyperedge_dict = {}

    @staticmethod
    def _to_frozen_set(hyperedge):
        """Convert a hyperedge into a frozen set.

        Parameters
        ----------
        hyperedge : HyperEdge | Iterable | Hashable
            The hyperedge that is to be converted to a frozen set.

        Returns
        -------
        frozenset
            Returns a frozenset of the elements contained in the hyperedge.
        """
        if isinstance(hyperedge, HyperEdge):
            hyperedge_ = hyperedge.elements
        elif isinstance(hyperedge, Iterable):
            hyperedge_ = frozenset(hyperedge)
        elif isinstance(hyperedge, Hashable) and not isinstance(hyperedge, Iterable):
            hyperedge_ = frozenset([hyperedge])
        return hyperedge_

    def __getitem__(self, hyperedge):
        """Get item.

        Parameters
        ----------
        hyperedge : Hashable or HyperEdge
            DESCRIPTION.

        Returns
        -------
        dict or list or dicts
            Return dict of attributes associated with that hyperedges.
        """
        hyperedge_ = HyperEdgeView._to_frozen_set(hyperedge)
        rank = self.get_rank(hyperedge_)
        return self.hyperedge_dict[rank][hyperedge_]

    @property
    def shape(self) -> tuple[int, ...]:
        """Compute shape.

        Returns
        -------
        tuple[int, ...]
            A tuple representing the shape of the hyperedge.
        """
        return tuple(len(self.hyperedge_dict[i]) for i in self.allranks)

    def __len__(self) -> int:
        """Compute the number of nodes.

        Returns
        -------
        int
            The number of nodes present in the HyperEdgeView.
        """
        return sum(self.shape)

    def __iter__(self) -> Iterator:
        """Iterate over the hyperedges.

        Returns
        -------
        Iterator
            Iterator object over the hyperedges.
        """
        return chain.from_iterable(self.hyperedge_dict.values())

    def __contains__(self, e: Collection) -> bool:
        """Check if e is in the hyperedges.

        Parameters
        ----------
        e : Collection
            The hyperedge that needs to be checked for containership
            in the HyperEdgeView.

        Returns
        -------
        bool
            Returns `True` if the hyperedge e is contained within the HyperEdgeView,
            else return `False`.
        """
        if len(self.hyperedge_dict) == 0:
            return False
        all_ranks = self.allranks
        if isinstance(e, HyperEdge):
            if len(e) == 0:
                return False
            else:
                for i in all_ranks:
                    if frozenset(e.elements) in self.hyperedge_dict[i]:
                        return True
                return False
        elif isinstance(e, Iterable):
            if len(e) == 0:
                return False
            else:
                for i in all_ranks:
                    if frozenset(e) in self.hyperedge_dict[i]:
                        return True
                return False
        elif isinstance(e, Hashable):
            return frozenset({e}) in self.hyperedge_dict[0]

    def __repr__(self) -> str:
        """Return string representation of hyperedges.

        Returns
        -------
        str
            The __repr__ string representation of HyperEdgeView.
        """
        return f"HyperEdgeView({[tuple(x) for x in self]})"

    def __str__(self) -> str:
        """Return string representation of hyperedges.

        Returns
        -------
        str
            The __str__ string representation of HyperEdgeView.
        """
        return f"HyperEdgeView({[tuple(x) for x in self]})"

    def skeleton(
        self,
        rank: int,
        level: Literal[
            "equal",
            "upper",
            "up",
            "lower",
            "down",
            "uppereq",
            "upeq",
            "lowereq",
            "downeq",
        ] = "equal",
    ):
        """Skeleton of the complex.

        Parameters
        ----------
        rank : int
            Rank of the skeleton.
        level : str, default="equal"
            Level of the skeleton.

        Returns
        -------
        list of frozensets
            The skeleton of rank `rank`.
        """
        if level == "equal":
            if rank in self.allranks:
                return sorted(self.hyperedge_dict[rank].keys())
            else:
                return []

        elif level in {"upper", "up"}:
            elements = []
            for rank_i in self.allranks:
                if rank_i > rank:
                    elements = elements + list(self.hyperedge_dict[rank_i].keys())
            return sorted(elements)

        elif level in {"lower", "down"}:
            elements = []
            for rank_i in self.allranks:
                if rank_i < rank:
                    elements = elements + list(self.hyperedge_dict[rank_i].keys())
            return sorted(elements)

        elif level in {"uppereq", "upeq"}:
            elements = []
            for rank_i in self.allranks:
                if rank_i >= rank:
                    elements = elements + list(self.hyperedge_dict[rank_i].keys())
            return sorted(elements)

        elif level in {"lowereq", "downeq"}:
            elements = []
            for rank_i in self.allranks:
                if rank_i <= rank:
                    elements = elements + list(self.hyperedge_dict[rank_i].keys())
            return sorted(elements)

        else:
            raise ValueError(
                "level must be 'equal', 'uppereq', 'lowereq', 'upeq', 'downeq', 'uppereq', 'lower', 'up', or 'down'  "
            )

    def get_rank(self, edge):
        """Get the rank of a hyperedge.

        Parameters
        ----------
        edge : Iterable, Hashable or HyperEdge
            The edge for which to get the rank.

        Returns
        -------
        int
            The rank of the given hyperedge.
        """
        if isinstance(edge, HyperEdge):
            if len(edge) == 0:
                return 0
            else:
                for i in list(self.allranks):
                    if frozenset(edge.elements) in self.hyperedge_dict[i]:
                        return i
                raise KeyError(f"hyperedge {edge.elements} is not in the complex")
        elif isinstance(edge, str):
            if frozenset({edge}) in self.hyperedge_dict[0]:
                return 0
            else:
                raise KeyError(f"hyperedge {frozenset({edge})} is not in the complex")
        elif isinstance(edge, Iterable):
            if len(edge) == 0:
                return 0
            else:
                for i in list(self.allranks):
                    if frozenset(edge) in self.hyperedge_dict[i]:
                        return i
                raise KeyError(f"hyperedge {edge} is not in the complex")
        elif isinstance(edge, Hashable) and not isinstance(edge, Iterable):
            if frozenset({edge}) in self.hyperedge_dict[0]:
                return 0
            else:
                raise KeyError(f"hyperedge {frozenset({edge})} is not in the complex")

    @property
    def allranks(self):
        """All ranks.

        Returns
        -------
        list[hashable]
            The sorted list of all ranks.
        """
        return sorted(self.hyperedge_dict.keys())

    def _get_lower_rank(self, rank):
        """Get a lower rank compared to given rank.

        Parameters
        ----------
        rank : int
            The rank to be used to get a lower rank.

        Returns
        -------
        int
            A rank below the current rank available in the HyperEdgeView.
        """
        if len(self.allranks) == 0:
            return -1

        ranks = sorted(self.allranks)
        if rank <= min(ranks) or rank >= max(ranks):
            return -1
        return ranks[ranks.index(rank) - 1]

    def _get_higher_rank(self, rank):
        """Get a higher rank compared to given rank.

        Parameters
        ----------
        rank : int
            The rank to be used to get a higher rank.

        Returns
        -------
        int
            A rank above the current rank available in the HyperEdgeView.
        """
        if len(self.allranks) == 0:
            return -1
        ranks = sorted(self.allranks)
        if rank <= min(ranks) or rank >= max(ranks):
            return -1
        return ranks[ranks.index(rank) + 1]


class SimplexView:
    """Simplex View class.

    The SimplexView class is used to provide a view/read only information
    into a subset of the nodes in a simplex.
    These classes are used in conjunction with the SimplicialComplex class
    for view/read only purposes for simplices in simplicial complexes.

    Parameters
    ----------
    name : str, optional
        Name of the SimplexView instance.

    Attributes
    ----------
    max_dim : int
        Maximum dimension of the simplices in the SimplexView instance.
    faces_dict : list of dict
        A list containing dictionaries of faces for each dimension.
    """

    def __init__(self, name: str = "") -> None:
        """Initialize an instance of the Simplex View class.

        The SimplexView class is used to provide a view/read only information
        into a subset of the nodes in a simplex.
        These classes are used in conjunction with the SimplicialComplex class
        for view/read only purposes for simplices in simplicial complexes.

        Parameters
        ----------
        name : str, optional
            Name of the SimplexView instance.
        """
        self.name = name

        self.max_dim = -1
        self.faces_dict = []

    def __getitem__(self, simplex):
        """Get the dictionary of attributes associated with the given simplex.

        Parameters
        ----------
        simplex : tuple, list or Simplex
            A tuple or list of nodes representing a simplex.

        Returns
        -------
        dict or list or dict
            A dictionary of attributes associated with the given simplex.
        """
        if isinstance(simplex, Simplex):
            if simplex.elements in self.faces_dict[len(simplex) - 1]:
                return self.faces_dict[len(simplex) - 1][simplex.elements]
        elif isinstance(simplex, Iterable):
            simplex = frozenset(simplex)
            if simplex in self.faces_dict[len(simplex) - 1]:
                return self.faces_dict[len(simplex) - 1][simplex]
            else:
                raise KeyError(f"input {simplex} is not in the simplex dictionary")

        elif isinstance(simplex, Hashable):
            if frozenset({simplex}) in self:
                return self.faces_dict[0][frozenset({simplex})]

    @property
    def shape(self) -> tuple[int, ...]:
        """Return the number of simplices in each dimension.

        Returns
        -------
        tuple of ints
            A tuple of integers representing the number of simplices in each dimension.
        """
        return tuple(len(self.faces_dict[i]) for i in range(len(self.faces_dict)))

    def __len__(self) -> int:
        """Return the number of simplices in the SimplexView instance.

        Returns
        -------
        int
            Returns the number of simplices in the SimplexView instance.
        """
        return sum(self.shape)

    def __iter__(self) -> Iterator:
        """Return an iterator over all simplices in the simplex view.

        Returns
        -------
        Iterator
            Returns an iterator over all simplices in the simplex view.
        """
        return chain.from_iterable(self.faces_dict)

    def __contains__(self, item) -> bool:
        """Check if a simplex is in the simplex view.

        Parameters
        ----------
        item : Any
            The simplex to be checked for membership in the simplex view.

        Returns
        -------
        bool
            True if the simplex is in the simplex view, False otherwise.

        Examples
        --------
        Check if a node is in the simplex view:

        >>> view = SimplexView()
        >>> view.faces_dict.append({frozenset({1}): {'weight': 1}})
        >>> view.max_dim = 0
        >>> 1 in view
        True
        >>> 2 in view
        False

        Check if a simplex is in the simplex view:

        >>> view.faces_dict.append({frozenset({1, 2}): {'weight': 1}})
        >>> view.max_dim = 1
        >>> {1, 2} in view
        True
        >>> {1, 3} in view
        False
        >>> {1, 2, 3} in view
        False
        """
        if isinstance(item, Iterable):
            item = frozenset(item)
            if not 0 < len(item) <= self.max_dim + 1:
                return False
            return item in self.faces_dict[len(item) - 1]
        elif isinstance(item, Hashable):
            return frozenset({item}) in self.faces_dict[0]
        return False

    def __repr__(self) -> str:
        """Return string representation that can be used to recreate it.

        Returns
        -------
        str
            Returns the __repr__ representation of the object.
        """
        all_simplices: list[tuple[int, ...]] = []
        for i in range(len(self.faces_dict)):
            all_simplices += [tuple(j) for j in self.faces_dict[i]]

        return f"SimplexView({all_simplices})"

    def __str__(self) -> str:
        """Return detailed string representation of the simplex view.

        Returns
        -------
        str
            Returns the __str__ representation of the object.
        """
        all_simplices: list[tuple[int, ...]] = []
        for i in range(len(self.faces_dict)):
            all_simplices += [tuple(j) for j in self.faces_dict[i]]

        return f"SimplexView({all_simplices})"


class NodeView:
    """Node view class.

    Parameters
    ----------
    objectdict : dict
        A dictionary of nodes with their attributes.
    cell_type : type
        The type of the cell.
    colored_nodes : bool, optional
        Whether or not the nodes are colored.
    name : str, optional
        Name of the NodeView instance.
    """

    def __init__(
        self, objectdict, cell_type, colored_nodes: bool = False, name: str = ""
    ) -> None:
        """Initialize an instance of the Node view class.

        Parameters
        ----------
        objectdict : dict
            A dictionary of nodes with their attributes.
        cell_type : type
            The type of the cell.
        colored_nodes : bool, optional, default = False
            Whether or not the nodes are colored.
        name : str, optional
            Name of the NodeView instance.
        """
        self.name = name
        if len(objectdict) != 0:
            self.nodes = objectdict[0]
        else:
            self.nodes = {}

        if cell_type is None:
            raise ValueError("cell_type cannot be None")

        self.cell_type = cell_type
        self.colored_nodes = colored_nodes

    def __repr__(self) -> str:
        """Return string representation of nodes.

        Returns
        -------
        str
            Returns the __repr__ representation of the object.
        """
        all_nodes = [tuple(j) for j in self.nodes.keys()]

        return f"NodeView({all_nodes})"

    def __iter__(self) -> Iterator:
        """Return an iterator over all nodes in the node view.

        Returns
        -------
        Iterator
            Returns an iterator over all nodes in the node view.
        """
        return iter(self.nodes)

    def __getitem__(self, cell):
        """Get item.

        Parameters
        ----------
        cell : tuple list or AbstractCell or Simplex
            A cell.

        Returns
        -------
        dict or list
            Dict of attributes associated with that cells.
        """
        if isinstance(cell, self.cell_type):
            if cell.elements in self.nodes:
                return self.nodes[cell.elements]
        elif isinstance(cell, Iterable):
            cell = frozenset(cell)
            if cell in self.nodes:
                if self.colored_nodes:
                    return self.nodes[cell][0]
                else:
                    return self.nodes[cell]
            else:
                raise KeyError(f"input {cell} is not in the node set of the complex")

        elif isinstance(cell, Hashable):
            if cell in self:
                if self.colored_nodes:
                    return self.nodes[frozenset({cell})][0]
                else:
                    return self.nodes[frozenset({cell})]

    def __len__(self) -> int:
        """Compute the number of nodes.

        Returns
        -------
        int
            Returns the number of nodes.
        """
        return len(self.nodes)

    def __contains__(self, e) -> bool:
        """Check if e is in the nodes.

        Parameters
        ----------
        e : Hashable | Iterable
            The node to check for.

        Returns
        -------
        bool
            Return `True` if e is contained in NodeView, else Return `False`.
        """
        if isinstance(e, Hashable) and not isinstance(e, self.cell_type):
            return frozenset({e}) in self.nodes

        elif isinstance(e, self.cell_type):
            return e.elements in self.nodes

        elif isinstance(e, Iterable):
            if len(e) == 1:
                return frozenset(e) in self.nodes
        else:
            return False


class PathView(SimplexView):
    """Path view class.

    Parameters
    ----------
    name : str, optional
        Name of the PathView instance.
    """

    def __init__(self, name: str = "") -> None:
        """Initialize an instance of the Path view class.

        Parameters
        ----------
        name : str, optional
            Name of the PathView instance.
        """
        super().__init__(name)

    def __getitem__(self, path: Hashable | Sequence[Hashable] | Path):
        """Get the dictionary of attributes associated with the given path.

        Parameters
        ----------
        path : int, str, tuple, list or Path
            A tuple or list of nodes representing a path.
            It can also be a Path object.
            It can also be a single node represented by int or str.

        Returns
        -------
        dict or list or dict
            A dictionary of attributes associated with the given path.
        """
        if isinstance(path, Path):
            if path.elements in self.faces_dict[len(path) - 1]:
                return self.faces_dict[len(path) - 1][path.elements]
            else:
                raise KeyError(f"input {path} is not in the path dictionary")
        elif isinstance(path, Sequence):
            path = tuple(path)
            if path in self.faces_dict[len(path) - 1]:
                return self.faces_dict[len(path) - 1][path]
            else:
                raise KeyError(f"input {path} is not in the path dictionary")
        elif isinstance(path, Hashable):
            if (path,) in self:
                return self.faces_dict[0][(path,)]
            else:
                raise KeyError(f"input {path} is not in the path dictionary")

    def __contains__(self, item: Sequence[Hashable] | Hashable | Path) -> bool:
        """Check if a path is in the path view.

        Parameters
        ----------
        item : Sequence[Hashable] or Hashable
            The path to be checked for membership in the path view.

        Returns
        -------
        bool
            True if the path is in the path view, False otherwise.
        """
        if isinstance(item, Sequence):
            item = tuple(item)
            if not 0 < len(item) <= self.max_dim + 1:
                return False
            return item in self.faces_dict[len(item) - 1]
        elif isinstance(item, Path):
            item = item.elements
            if not 0 < len(item) <= self.max_dim + 1:
                return False
            return item in self.faces_dict[len(item) - 1]
        elif isinstance(item, Hashable):
            return (item,) in self.faces_dict[0]
        return False

    def __repr__(self) -> str:
        """Return string representation that can be used to recreate it.

        Returns
        -------
        str
            Returns the __repr__ representation of the object.
        """
        all_paths: list[tuple[int | str, ...]] = []
        for i in range(len(self.faces_dict)):
            all_paths += [tuple(j) for j in self.faces_dict[i]]

        return f"PathView({all_paths})"

    def __str__(self) -> str:
        """Return detailed string representation of the path view.

        Returns
        -------
        str
            Returns the __str__ representation of the object.
        """
        all_paths: list[tuple[int | str, ...]] = []
        for i in range(len(self.faces_dict)):
            all_paths += [tuple(j) for j in self.faces_dict[i]]

        return f"PathView({all_paths})"
