from goulib.tests import *
from goulib.graph import *

import logging
import os
import time

path = os.path.dirname(os.path.abspath(__file__))
results = os.path.join(path, 'results', 'graph')  # path for results


class TestGeoGraph:
    @classmethod
    def setup_class(self):
        self.empty = GeoGraph()
        self.cube = GeoGraph(nx.hypercube_graph(3), multi=False)
        self.geo = GeoGraph(nx.random_geometric_graph(50, .25))

        nodes = points_on_sphere(120)
        # test if we can construct from nodes only
        self.sphere = GeoGraph(nodes=nodes)
        self.sphere = delauney_triangulation(
            nodes, 'Qz', tol=0)  # 'Qz' required for spheres

        self.dot = GeoGraph(os.path.join(path, 'data', 'cluster.dot'))

    def test_save(self):
        self.dot.save(os.path.join(results, 'cluster.png'), transparent=False)

        # 3D graph
        self.sphere.save(os.path.join(
            results, 'graph.sphere.png'), transparent=False)

    def test_to_drawing(self):
        d = to_drawing(self.geo)  # 2D
        d.save(os.path.join(results, 'graph.geo.drawing.svg'))
        d = to_drawing(self.sphere)  # 3D
        d.save(os.path.join(results, 'graph.sphere.drawing.svg'))

    def test_render(self):
        # define a function that maps edge data to a color
        m = plt.get_cmap('Blues')

        def edge_color(data):  # make longer links darker
            try:
                return m(data['length']/.25)
            except:
                pass
        self.geo.render(
            edge_color=edge_color,
            node_size=50,
            labels=lambda x: x[1]['key'],  # key of dict of node attributes
        )  # this sets geo.render_args ...
        self.geo.save(os.path.join(results, 'graph.graph.png'),
                      transparent=False)

    def test_is_multigraph(self):
        assert not self.cube.is_multigraph()

    def test___init__(self):
        assert self.cube.number_of_nodes() == 8
        assert self.cube.number_of_edges() == 12

    def test___nonzero__(self):
        assert bool(self.cube)
        assert not bool(self.empty)

    def test_length(self):
        assert self.cube.length() == 12

    def test_multi(self):
        pass  # tested below

    def test_add_node(self):
        g = GeoGraph()
        # tests the various ways, checking the second attempt returns the same node
        assert g.add_node((1.2, 3)) == g.add_node((1.2, 3))
        assert g.add_node('(-1.2,-5)') == g.add_node('(-1.2,-5)')
        assert g.add_node("label") == g.add_node("label")

    def test_add_edge(self):
        g = self.cube.copy()
        assert g.length() == 12
        g.add_edge((0, 0, 0), (1, 1, 1), length=3)
        assert g.number_of_edges() == 13
        assert g.length() == 15
        # try recreating the same edge when multi is False
        g.multi = False
        assert g.number_of_edges() == 13
        # it should only change the attribute
        g.add_edge((0, 0, 0), (1, 1, 1), length=2)

        assert g.number_of_edges() == 13
        assert g.length() == 14
        # try recreating the same edge when multi is False
        g.multi = True
        # now this one should be added
        edge = g.add_edge2((0, 0, 0), (1, 1, 1), length=3)
        assert edge['length'] == 3
        assert g.number_of_edges() == 14
        assert g.length() == 17

    def test_remove_edge(self):
        g = self.cube.copy()
        assert g.number_of_nodes() == 8
        assert g.number_of_edges() == 12

        for edge in list(g.edges((0, 0, 0))):
            g.remove_edge(edge, clean=True)

        assert g.number_of_nodes() == 7
        assert g.number_of_edges() == 9

    def test_closest_nodes(self):
        close, d = self.cube.closest_nodes((0, 0, 0))
        assert d == 0
        assert close == [(0, 0, 0)]
        close, d = self.cube.closest_nodes((0, 0, 0), skip=True)
        assert d == 1
        assert len(close) == 3
        close, d = self.cube.closest_nodes((0.5, 0.5, 0))
        assert len(close) == 4

    def test_remove_node(self):
        g = self.cube.copy()
        assert g.number_of_nodes() == 8
        assert g.number_of_edges() == 12

        g.remove_node((0, 0, 0))

        assert g.number_of_nodes() == 7
        assert g.number_of_edges() == 9

    def test_closest_edges(self):
        g = self.cube.copy()
        close, d = g.closest_edges((0, 0, 0))
        assert d == 0
        assert len(list(close)) == 3

        g.remove_node((0, 0, 0))  # tested above
        close, d = g.closest_edges((0, 0, 0))
        assert d == 1
        assert len(list(close)) == 6

    def test_box(self):
        assert self.cube.box() == ((0, 0, 0), (1, 1, 1))

    def test_box_size(self):
        assert self.cube.box_size() == (1, 1, 1)

    def test_stats(self):
        stats = self.cube.stats()
        assert stats['nodes'] == 8
        assert stats['edges'] == 12

    def test_str(self):
        s = str(self.empty)
        assert "'nodes': 8" in str(self.cube)

    def test_dist(self):
        import math
        assert self.cube.dist((0, 0, 0), (1, 1, 1)) == math.sqrt(3)

    def test_contiguity(self):
        c = self.cube.contiguity([(0, 0, 0), (1, 0, 0)])
        assert c is not None

    def test_tol(self):
        assert self.cube.tol is not None

    def test___str__(self):
        assert str(self.cube) is not None

    def test_add_nodes_from(self):
        g = GeoGraph()
        g.add_nodes_from([((0, 0), {}), ((1, 1), {})])
        assert len(g) == 2

    def test_copy(self):
        g = self.geo.copy()
        assert not g is self.geo
        # assert_true(g == self.geo) #TODO find why it doens't work anymore

    def test_number_of_nodes(self):
        assert self.cube.number_of_nodes() == 8

    def test_draw(self):
        fig, ax = plt.subplots()
        self.cube.draw(ax=ax)
        plt.close(fig)

    def test_clear(self):
        g = GeoGraph(nx.random_geometric_graph(50, .25))
        g.clear()
        assert g.multi == True

    def test___bool__(self):
        assert bool(self.cube)
        assert not bool(GeoGraph())


class TestRender:
    def test_render(self):
        pass  # tested in test_save


class TestDelauneyEMST(TestCase):
    '''groups 2 tests coherently'''

    def setUp(self):
        self.n = 1000 if RTREE else 100
        from random import random
        self.nodes = [(random(), random()) for _ in range(self.n)]

    def test_delauney_triangulation(self):
        start = time.perf_counter()
        graph = delauney_triangulation(self.nodes, tol=0)
        logging.info('Delauney %d : %f' % (self.n, time.perf_counter()-start))
        assert graph.number_of_nodes() == self.n
        assert nx.is_connected(graph)
        assert graph.is_directed() == False
        graph.save(os.path.join(results, 'graph.delauney.png'))

    def test_emst(self):
        start = time.perf_counter()
        graph = euclidean_minimum_spanning_tree(self.nodes)
        logging.info('Spanning tree %d : %f' %
                     (self.n, time.perf_counter()-start))
        graph.save(os.path.join(results, 'graph.emst.png'))
        graph = to_networkx_graph(graph, create_using=nx.Graph())  # issue #12


class TestFigure:
    def test_figure(self):
        pass  # tested above


class TestDraw:
    def test_draw(self):
        pass  # tested above


class TestDrawNetworkx:
    def test_draw_networkx(self):
        g = nx.gn_graph(10)  # generate a DiGraph
        draw_networkx(g)


class TestPointsOnSphere:
    def test_points_on_sphere(self):
        pass


class TestWriteDxf:
    def test_write_dxf(self):
        g = GeoGraph()
        g.add_edge((0, 0), (1, 1))
        out = os.path.join(path, 'results', 'graph.test.dxf')
        write_dxf(g, out)
        assert os.path.exists(out)


class TestToNetworkxGraph:
    def test_to_networkx_graph(self):
        g = GeoGraph()
        g.add_edge((0, 0), (1, 1))
        nx_g = nx.Graph(g)
        assert len(nx_g) == 2


class TestDiGraph:
    def test___init__(self):
        dg = DiGraph()
        dg.add_edge('A', 'B')
        assert dg.has_edge('A', 'B')
        assert not dg.has_edge('B', 'A')


class TestToDrawing:
    def test_to_drawing(self):
        g = GeoGraph()
        g.add_edge((0, 0), (1, 1))
        d = to_drawing(g)
        assert len(d) == 1


class TestWriteDot:
    def test_write_dot(self):
        try:
            import pydot
            g = nx.Graph()
            g.add_edge('A', 'B')
            out = os.path.join(path, 'results', 'graph.test.dot')
            write_dot(g, out)
            assert os.path.exists(out)
        except (ImportError, FileNotFoundError):
            pass


class TestToJson:
    def test_to_json(self):
        g = GeoGraph()
        g.add_edge((0, 0), (1, 1))
        j = to_json(g)
        assert 'nodes' in j and ('edges' in j or 'links' in j)


class TestWriteJson:
    def test_write_json(self):
        g = GeoGraph()
        g.add_edge((0, 0), (1, 1))
        out = os.path.join(path, 'results', 'graph.test.json')
        write_json(g, out)
        assert os.path.exists(out)

