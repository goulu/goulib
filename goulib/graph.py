"""
efficient Euclidian Graphs for :mod:`networkx` and related algorithms

:requires:

* `networkx <http://networkx.github.io/>`_
* `matplotlib <http://pypi.python.org/pypi/matplotlib/>`_

:optional:

* `scipy <http://www.scipy.org/>`_ for delauney triangulation
* `rtree <http://toblerity.org/rtree/>`_ for faster GeoGraph algorithms
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2014, Philippe Guglielmetti"
__credits__ = []
__license__ = "LGPL"

import logging
import math
import json

import networkx as nx  # http://networkx.github.io/
import numpy
import scipy

from . import plot  # set matplotlib backend
import matplotlib.pyplot as plt  # after import .plot

from . import math2, itertools2

"""
finding the nearest neighbor in a large GeoGraph is much faster with the
RTree package, but it's not generally available, so a pure python fallback
is provided
"""

try:
    from rtree import index  # http://toblerity.org/rtree/
    RTREE = True
except ImportError:  # fallback, especially because I couldn't manage to install rtree on travis-ci
    RTREE = False
    # logging.warning('rtree not available')

    class index:    # pylint: disable=function-redefined
        # mimics rtree.index module

        class Property:
            def set_dimension(self, n):
                self.n = n

        class Index(dict):
            """fallback for rtree.index"""

            def __init__(self, properties):
                self.prop = properties
                self.bounds = [None]*properties.n*2  # minx,miny,maxx,maxy, ...

            def count(self, ignored):
                return len(self)

            def insert(self, k, p, _):
                self[k] = p
                for i, c in enumerate(p):
                    v = self.bounds[i]
                    self.bounds[i] = min(c if v is None else v, c)
                    v = self.bounds[self.prop.n+i]
                    self.bounds[self.prop.n+i] = max(c if v is None else v, c)

            def delete(self, k, _):
                del self[k]

            def nearest(self, p, num_results, objects='raw'):
                """ very inefficient, but remember it's a fallback..."""
                return itertools2.best(list(self.values()), key=lambda q: math2.dist(p, q), n=num_results)

_nk = 0  # node key

def to_networkx_graph(data, create_using=None, multigraph_input=False):
    """Make a NetworkX graph from a known data structure.
    enhances `networkx.convert.to_networkx_graph`
    :param data: any type handled by `convert.to_networkx_graph`, plus:
    * :class:`scipy.spatial.qhull.Delaunay` to enable building a graph from a delauney triangulation

    If create_using is a :class:`GeoGraph`and data is a Graph where nodes have a 'pos' attribute,
    then this attribute will be used to rename nodes as (x,y,...) tuples suitable for GeoGraph.

    """
    if isinstance(data, scipy.spatial.Delaunay):
        create_using.delauney = data
        triangles = data.points[data.simplices]
        for point in triangles:
            p = list(map(tuple, point))  # convert from numpy to regular list
            create_using.add_edge(p[0], p[1])
            create_using.add_edge(p[1], p[2])
            create_using.add_edge(p[2], p[0])

    elif isinstance(create_using, _Geo):
        tol = create_using.tol
        create_using.tol = 0  # zero tolerance when copying

        if isinstance(data, nx.Graph):
            create_using.clear()
            create_using.add_nodes_from(data.nodes(data=True))
            create_using.add_edges_from(data.edges(data=True))
        else:
            create_using = nx.convert.to_networkx_graph(
                data, create_using, multigraph_input)
        create_using.tol = tol  # revert tolerance

    else:
        create_using = nx.convert.to_networkx_graph(
            data, create_using, multigraph_input)

    return create_using


# pylint: disable=no-member, unsupported-membership-test, unsubscriptable-object
class _Geo(plot.Plot):
    """base class for graph with nodes at specified positions.
    if edges have a "length" attribute, it is used to compute distances,
    otherwise euclidian distance between nodes is used by default
    """

    def __init__(self, parent, data=None, nodes=None, **kwargs):
        """
        :param parent: type of the graph. nx.Graph, nx.DiGraph or nx.MultiGraph
        :param data: see :meth:`to_networkx_graph` for valid types
        """
        self.parent = parent
        self.idx = None  # index is created at first call to add_node

        self._map = {}  # map from original node name to position for pygraphviz.AGraph and other graphs were 'pos' is a node attribute

        if data:
            if isinstance(data, str):  # suppose data is a filename
                ext = data.split('.')[-1].lower()
                if ext == 'dot':
                    import pydot
                    dot = pydot.graph_from_dot_file(data)
                    data = nx.drawing.nx_pydot.from_pydot(dot[0])
                elif ext == 'json':
                    data = read_json(
                        data, directed=self.is_directed(), multigraph=self.multi)
                else:
                    raise (Exception('unknown file format'))

            to_networkx_graph(data, self)
        elif nodes:
            for node in nodes:
                self.add_node(node)

        self.render_args = {}

    def copy(self):
        """
        :return: copy of self graph
        """
        # does not use deepcopy because the rtree index must be rebuilt
        return self.__class__(self, **self.graph)

    def __eq__(self, other):
        """
        :return: True if self and other are equal
        """
        def eq(a, b):
            return a == b
        return nx.is_isomorphic(self, other, node_match=eq, edge_match=eq)

    def __nonzero__(self):
        """
        :return: True if graph has at least one node
        """
        return self.number_of_nodes() > 0

    __bool__ = __nonzero__

    def clear(self):
        # saves some graph attributes cleared by convert._prep_create_using
        t, m = self.tol, self.multi
        self.parent.clear(self)
        self.multi = m
        self.graph['tol'] = t

    @property
    def tol(self):
        return self.graph['tol']

    @tol.setter
    def tol(self, tol):
        self.graph['tol'] = tol

    @property
    def multi(self):
        return self.graph.get('multi', True)

    @multi.setter
    def multi(self, s):
        self.graph['multi'] = s

    def is_multigraph(self):
        """used internally in constructor"""
        try:
            return self.multi
        except AttributeError:
            return self.parent.is_multigraph(self)

    def pos(self, nodes=None):
        """
        :param nodes: a single node, an iterator of all nodes if None
        :return: the position of node(s)
        """
        try:
            return self.nodes[nodes]['pos']
        except KeyError:
            pass
        if isinstance(nodes, tuple):
            return nodes
        if nodes is None:
            nodes = self
        return (self.pos(n) for n in nodes)

    def dist(self, u, v):
        """
        :return: float distance between nodes u and v
        """

        try:
            edge = self[u][v]
            return edge['length']
        except KeyError:
            return math2.dist(self.pos(u), self.pos(v))

    def length(self, edges=None):
        """
        :param edges: iterator over edges either as (u,v,data) or (u,v,key,data). If None, all edges are taken
        :returns: sum of 'length' attributes of edges
        """

        if edges is None:  # take all edges
            return self.size(weight="length")

        res = 0
        for edge in edges:
            data = edge[-1]
            (u, v) = edge[:2]
            try:
                l = data['length']
            except:
                l = self.dist(u, v)
                data['length'] = l
            res += l
        return res

    def box(self):
        """:return: nodes bounding box as (xmin,ymin,...),(xmax,ymax,...)"""
        if self.idx is None:  # empty graph
            return (0, 0)
        minmax = self.idx.bounds
        n = len(minmax)//2
        return tuple(minmax[:n]), tuple(minmax[n:])

    def box_size(self):
        """:return: (x,y) size"""
        a, b = self.box()
        try:
            a[0], b[0]  # at least one dimension ?
            return tuple(math2.vecsub(b, a))
        except:
            return (0, 0)

    def contiguity(self, pts):
        """
        :return: int number of points from pts already in graph
        """
        res = 0
        for pt in pts:
            if pt in self:
                res += 1
        return res

    def closest_nodes(self, p, n=1, skip=False):
        """
        nodes closest to a given position
        :param p: (x,y) position tuple
        :param skip: optional bool to skip n itself
        :return: list of nodes, minimal distance
        """
        if skip:
            n += 1
        if n == 1:
            if p in self:
                return [p], 0

        res, d = [], None
        for p2 in self.idx.nearest(p, num_results=n, objects='raw'):
            d = self.dist(p, p2)
            if skip and d <= self.tol:
                continue
            res.append(p2)
        return res, d

    def closest_edges(self, p, data=False):
        """:return: container of edges close to p and distance"""
        edges = []
        n = 0
        while not edges and n < 10:
            n += 1  # handle more and more nodes until we find one with edges
            nbunch, d = self.closest_nodes(p, n)
            edges = self.edges(nbunch=nbunch, data=data)

        return edges, d

    def add_node(self, p, **attr):
        """add a node or return one already very close
        :return (x,y,...) node id
        """
        if p in self:  # point already exists
            return p

        id = p  # save the node id as the position might differ

        if type(p) is not tuple:
            # try to find a position tuple somewhere
            if p in self._map:
                return self._map[p]

            p = attr.get('pos', id)
            if isinstance(p, str):
                p = p.split(',')
            try:
                p = tuple(float(x) for x in p)
            except ValueError:  # assign a random position, but keep node id
                from random import random
                attr['pos'] = p = tuple((random(), random()))

        if self.idx is None:  # now we know the dimension, so we can create the index
            n = len(p)
            prop = index.Property()
            prop.set_dimension(n)
            self.idx = index.Index(properties=prop)

        if self.tol > 0:
            # search for those within tolerance
            close, d = self.closest_nodes(p)
            if close and d <= self.tol:
                return close[0]

        # point doesn't exist yet : create it

        global _nk  # unique int node identifier for RTREE
        _nk += 1
        self.idx.insert(_nk, p, p)
        # use RTREE key for networkX
        attr['key'] = _nk
        self.parent.add_node(self, id, **attr)
        # ._map links both id
        self._map[id] = p
        return id

    def add_nodes_from(self, nodes, **attr):
        # must override here because Graph.add_nodes_from doesn't call add_node
        # so attributes and self.idx wouldn't be handled correctly

        for n in nodes:
            attr.update(n[1])
            self.add_node(n[0], **attr)

    def remove_node(self, n):
        """
        :param n: node tuple
        remove node from graph and rtree
        """
        n1 = self.number_of_nodes()
        n2 = self.idx.count(self.idx.bounds)
        if n1 != n2:
            logging.error('GeoGraph has %d!=%d' % (n1, n2))
            raise RuntimeError('Nodes/Rtree mismatch')
        nk = self.nodes[n]['key']
        self.parent.remove_node(self, n)
        self.idx.delete(nk, n)  # in fact n is ignored, the nk key is used here

    def _last(self, u, v):
        """since multigraphs can have several edges from u to v,
        :return: dict of the edge added last
        """
        try:
            edges = self.adj[u][v]
        except:  # no edge between u and v yet
            return None  # not {}, to make a diff with existing empty dict
        if len(edges) == 1:  # quick
            return edges[0]
        else:
            return edges[max(edges.keys())]

    def _add_edge(self, u, v, key=None, **attr):
        """add an edge to graph

        :return: edge key
        """
        u = self.add_node(u)  # create or find nearest in tol
        v = self.add_node(v)  # create or find nearest in tol

        if 'length' not in attr:
            attr['length'] = self.dist(u, v)

        if not self.is_multigraph():  # update already existing edge
            try:
                self[u][v]
            except KeyError:  # no edge
                pass
            else:
                k = key or 0
                self[u][v][k].update(attr)
                return k

        key = self.parent.add_edge(self, u, v, key=key)
        # note : NetworkX 1.x doesn't return the key ...
        if self.parent.is_multigraph(self):
            if key is None:  # ... so we have to retrieve it now
                key = len(self[u][v])-1
            self[u][v][key].update(attr)
        else:
            self[u][v].update(attr)
            key = None
        return key

    if nx.__version__ < '2':  # backward compatibility for now
        def add_edge(self, u, v, key=None, attr_dict=None, **attr):
            # set up attribute dict # code copied from nx 1,11
            if attr_dict is None:
                attr_dict = attr
            else:
                attr_dict.update(attr)
            return self._add_edge(u, v, key=key, **attr_dict)
    else:
        add_edge = _add_edge

    def add_edge2(self, u, v, key=None, **attrs):
        """add an edge to graph
        :return: edge data from created or existing edge
        """
        key = self._add_edge(u, v, key, **attrs)

        try:
            return self[u][v][key or 0]
        except KeyError:
            return self[u][v]

    def remove_edge(self, u, v=None, key=None, clean=False):
        """
        :param u: Node or Edge (Nodes tuple)
        :param v: Node if u is a single Node
        :param clean: bool removes disconnected nodes. must be False for certain nx algos to work
        :result: return attributes of removed edge
        remove edge from graph. NetworkX graphs do not remove unused nodes
        """

        if v is None:
            u, v = u[0], u[1]

        if self.is_multigraph():
            if key is None:
                key = self.adj[u][v]
                key = itertools2.first(key)
            data = self.adj[u][v][key]
        else:
            data = self.adj[u][v]
        self.parent.remove_edge(self, u, v, key)

        if clean:
            if self.degree(u) == 0:
                self.remove_node(u)
            if self.degree(v) == 0:
                self.remove_node(v)
        return data

    def number_of_nodes(self, doublecheck=False):
        # check that both structures are coherent at the same time
        n1 = self.parent.number_of_nodes(self)
        if doublecheck:
            n2 = self.idx.count(self.idx.bounds) if n1 else 0
            if n1 != n2:
                raise KeyError('%s %s number of nodes %d!=%d' %
                               (self.__class__.__name__, self.name, n1, n2))
        return n1

    def shortest_path(self, source=None, target=None):
        # TODO : add distance weights
        return nx.shortest_path(self, source, target)

    def stats(self):
        """:return: dict of graph data to use in __repr__ or usable otherwise"""
        res = {}
        res['name'] = self.name
        res['bbox'] = self.box()
        res['size'] = self.box_size()
        res['nodes'] = self.number_of_nodes()
        res['edges'] = self.number_of_edges()
        if not self.is_directed:  # not implemented for directed type
            res['components'] = nx.number_connected_components(self)
        res['length'] = self.length()
        return res

    def __str__(self):
        """:returns: string representation, used mainly for logging and debugging"""
        return str(self.stats())

    def draw(self, **kwargs):
        """ draw graph with default params"""
        kwargs.setdefault('with_labels', False)
        kwargs.setdefault('node_size', 0)

        return draw_networkx(self, **kwargs)

        """ for debug and compatibility check:
        kwargs.pop('edge_color',None)
        return nx.draw_networkx(self, **kwargs)
        """

    def render(self, fmt='svg', **kwargs):
        """ render graph to bitmap stream
        :param fmt: string defining the format. 'svg' by default for INotepads
        :return: matplotlib figure as a byte stream in specified format
        """

        self.render_args.update(kwargs)
        fig = self.draw(**self.render_args)

        from io import BytesIO
        output = BytesIO()
        fig.savefig(output, format=fmt,
                    transparent=kwargs.get('transparent', True))
        res = output.getvalue()
        plt.close(fig)
        return res

    def save(self, filename, **kwargs):
        """ save graph in various formats"""
        ext = filename.split('.')[-1].lower()
        if ext == 'dxf':
            write_dxf(self, filename)
        elif ext == 'dot':
            write_dot(self, filename)
        elif ext == 'json':
            write_json(self, filename, **kwargs)
        else:
            open(filename, 'wb').write(self.render(ext, **kwargs))
        return self


class GeoGraph(_Geo, nx.MultiGraph):
    """ Undirected graph with nodes positions
    can be set to non multiedges anytime with attribute multi=False
    """

    def __init__(self, data=None, nodes=None, **kwargs):
        """
        :param data: see :meth:`to_networkx_graph` for valid types
        :param kwargs: other parameters will be copied as attributes, especially:

        """
        properties = kwargs
        try:
            properties.update(data.graph)
        except:
            pass
        # default tolerance on node positions
        properties.setdefault('tol', 0.010)

        nx.MultiGraph.__init__(self, None, **properties)
        _Geo.__init__(self, nx.MultiGraph, data, nodes)


class DiGraph(_Geo, nx.MultiDiGraph):
    """ directed graph with nodes positions
    can be set to non multiedges anytime with attribute multi=False
    """

    def __init__(self, data=None, nodes=None, **kwargs):
        """
        :param data: see :meth:`to_networkx_graph` for valid types
        :param kwargs: other parameters will be copied as attributes, especially:

        """
        properties = kwargs
        try:
            properties.update(data.graph)
        except AttributeError:
            pass
        # default tolerance on node positions
        properties.setdefault('tol', 0.010)

        nx.MultiDiGraph.__init__(self, None, **properties)
        _Geo.__init__(self, nx.MultiDiGraph, data, nodes, directed=True)


def figure(g, box=None, **kwargs):
    """
    :param g: _Geo derived Graph
    :param box: optional interval.Box if g has no box
    :return: matplotlib axis suitable for drawing graph g
    """
    fig = plt.figure(**kwargs)
    try:
        box = g.box()
    except:
        pass  # use 2nd parameter

    # draw a transparent diagonal to size everything
    plt.plot(box[0], box[1], alpha=0)
    plt.axis('equal')
    import pylab
    pylab.axis('off')  # turn off axis

    return fig


def draw_networkx(g, pos=None, **kwargs):
    """ improves nx.draw_networkx
    :param g: NetworkX Graph
    :param pos: can be either :

    - optional dictionary of (x,y) node positions
    - function of the form lambda node:(x,y) that maps node positions.
    - None. in this case, nodes are directly used as positions if graph is a GeoGraph, otherwise nx.draw_shell is used

    :param **kwargs: passed to nx.draw method as described in http://networkx.lanl.gov/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html with one tweak:

    - if edge_color is a function of the form lambda data:color string, it is mapped over all edges

    """

    # build node positions

    if itertools2.iscallable(pos):  # mapping function
        pos = dict(((node, pos(node)) for node in g))

    if pos is None:
        try:
            pos = dict((node, data['pos'][:2])
                       for node, data in g.nodes(data=True))
        except KeyError:
            pass

    if pos is None:
        try:
            pos = dict(((node, node[:2]) for node in g))
        except TypeError:
            pass

    if pos is None:
        pos = nx.spring_layout(g)  # default to spring layout

    try:  # convert ndarray to python lists
        for k in pos:
            pos[k] = pos[k].tolist()
    except AttributeError:
        pass

    edgelist = list(kwargs.pop('edgelist', g.edges(data=True)))

    edge_color = kwargs.get('edge_color', None)
    if edge_color is None:
        # build edge_colors
        default = None
        try:  # get default edge color
            default = g.color
        except AttributeError:
            pass
        if default is None:
            default = 'k'  # black

        def f(data):  # function to color edges, applied below
            c = data.get('color', default)
            return c if c else default
        edge_color = f

    if itertools2.iscallable(edge_color):  # mapping function ?
        edge_color = list(map(edge_color, (data for u, v, data in edgelist)))

    if edge_color:  # not empty
        kwargs['edge_color'] = edge_color

    fig = kwargs.pop('fig', None)

    if not fig:
        try:  # we need a bounding box
            box = g.box()
        except:
            box = (math2.minimum(pos.values()), math2.maximum(pos.values()))
        fig = figure(g, box=box, figsize=kwargs.get('figsize', None))

    if kwargs.get('node_size', 300) > 0:
        nx.draw_networkx_nodes(g, pos, **itertools2.subdict(kwargs, (
            'nodelist', 'node_size', 'node_color', 'node_shape', 'alpha', 'cmap', 'vmin', 'vmax', 'ax', 'linewidths', 'edgecolor', 'label'
        )))

    nx.draw_networkx_edges(g, pos, edgelist, **itertools2.subdict(kwargs, (
        'width', 'edge_color', 'style', 'alpha', 'arrowstyle', 'arrowsize', 'edge_cmap', 'edge_vmin', 'edge_vmax', 'ax', 'arrows', 'label', 'node_size', 'nodelist', 'node_shape', 'connectionstyle', 'min_source_margin', 'min_target_margin'
    )))

    labels = kwargs.pop('labels', False)
    if labels:
        if labels is True:
            labels = None  # will be set automatically
        if itertools2.iscallable(labels):  # mapping function ?
            labels = list(labels(u) for u in g.nodes(data=True))
        if isinstance(labels, list):  # a dict is expected:
            labels = dict(zip(g.nodes(), labels))
        nx.draw_networkx_labels(g, pos, labels,  **itertools2.subdict(kwargs, (
            'font_size', 'font_color', 'font_family', 'font_weight', 'alpha', 'bbox', 'horizontalalignment', 'verticalalignment', 'ax'
        )))

    return fig


def to_drawing(g, d=None, edges=[]):
    """
    draws Graph to a `Drawing`
    :param g: :class:`Graph`
    :param d: existing :class:`Drawing` to draw onto, or None to create a new Drawing
    :param edges: iterable of edges (with data) that will be added, in the same order. By default all edges are drawn
    :return: :class:`Drawing`

    Graph edges with an 'entity' property
    """
    from . import drawing, geom
    if d is None:
        d = drawing.Drawing()
    if not edges:
        edges = g.edges(data=True)
    for edge in edges:
        u, v, data = edge[0], edge[1], edge[-1]
        try:
            e = data['entity']
        except KeyError:
            u = g.pos(u)
            v = g.pos(v)
            e = geom.Segment2(u, v)
        d.append(e)
    return d


def write_dxf(g, filename):
    """writes :class:`networkx.Graph` in .dxf format"""
    to_drawing(g).save(filename)


def write_dot(g, filename):
    import pydot

    if isinstance(g, _Geo) or any(map(lambda n: hasattr(n, 'pos'), g.nodes())):
        g = g.copy()

    for n in g.nodes(data=True):
        try:
            pos = g.pos(n[0])
        except AttributeError:
            pos = n[1].get('pos', None)
        if pos is not None:  # format pos as neato wants it : "x,y"
            n[1]['pos'] = '"%s,%s"' % pos

    nx.drawing.nx_pydot.write_dot(g, filename)


def to_json(g, **kwargs):
    """
    :return: string JSON representation of a graph
    """
    from datetime import datetime, date, time, timedelta

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        try:
            return str(obj)
        except Exception:
            pass
        raise TypeError("Type %s not serializable" % (type(obj)))
    from networkx.readwrite import json_graph
    g = json_graph.node_link_data(g)
    for node in g['nodes']:
        pos = node.pop('pos', None)
        if pos:
            node['x'] = pos[0]
            node['y'] = pos[1]
            # node['fixed']=True
    kwargs.setdefault('default', json_serial)
    return json.dumps(g, **kwargs)


def write_json(g, filename, **kwargs):
    """write a JSON file, suitable for D*.js representation
    """
    with open(filename, 'w') as file:
        file.write(to_json(g, **kwargs))


def read_json(filename, directed=False, multigraph=True, attrs=None):
    with open(filename) as f:
        js_graph = json.load(f)
    return nx.node_link_graph(js_graph, directed, multigraph, attrs)


def delauney_triangulation(nodes, qhull_options='', incremental=False, **kwargs):
    """
    https://en.wikipedia.org/wiki/Delaunay_triangulation
    :param nodes: _Geo graph or list of (x,y) or (x,y,z) node positions
    :param qhull_options: string passed to :meth:`scipy.spatial.Delaunay`,
    which passes it to Qhull ( http://www.qhull.org/ )
    *'Qt' ensures all points are connected
    *'Qz' required when nodes lie on a sphere
    *'QJ' solves some singularity situations

    :param kwargs: passed to the :class:`GeoGraph` constructor
    :return: :class:`GeoGraph` with delauney triangulation between nodes
    """
    if isinstance(nodes, _Geo):
        nodes = list(nodes.pos())
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html
    points = numpy.array(nodes)
    tri = scipy.spatial.Delaunay(
        points, qhull_options=qhull_options, incremental=incremental)
    kwargs['multi'] = False  # to avoid duplicating triangle edges below
    g = GeoGraph(tri, dimension=tri.ndim, **kwargs)
    return g


def euclidean_minimum_spanning_tree(nodes, **kwargs):
    """
    :param nodes: list of (x,y) nodes positions
    :return: :class:`GeoGraph` with minimum spanning tree between nodes

    see https://en.wikipedia.org/wiki/Euclidean_minimum_spanning_tree
    """
    g = GeoGraph(None, **kwargs)
    d = delauney_triangulation(nodes, **kwargs)
    g.add_edges_from(nx.minimum_spanning_edges(d, weight='length'))
    return g

# Function to distribute N points on the surface of a sphere
# (source: http://www.softimageblog.com/archives/115)


def points_on_sphere(N):
    pts = []
    inc = math.pi * (3 - math.sqrt(5))
    off = 2 / float(N)
    for k in range(0, int(N)):
        y = k * off - 1 + (off / 2)
        r = math.sqrt(1 - y*y)
        phi = k * inc
        pts.append((math.cos(phi)*r, y, math.sin(phi)*r))
    return pts
