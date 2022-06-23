import networkx as nx
from collections import defaultdict
import math, copy, os


class BasicAtts(object):
    def __init__(self, name, weight):
        self.customer = defaultdict(set)
        self.provider = defaultdict(set)
        self.peer = defaultdict(set)
        self.weight = weight
        self.adjacency_list = defaultdict(set)

        self.graph = nx.Graph()
        self.short_graph = nx.DiGraph()
        self.edges = defaultdict()
        self.distance = dict()
        self.pr = None
        self.rel_name = name

        self.getGraph()
        self.getDistance()
        self.ASHierarchy()

    def getGraph(self):
        with open(self.rel_name) as f:
            for line in f:
                if not line.startswith('#'):
                    [asn1, asn2, rel] = line.strip().split('|')
                    self.graph.add_edge(asn1, asn2)
                    if rel == '-1':
                        self.short_graph.add_node(asn1)
                        self.short_graph.add_node(asn2)
                        self.short_graph.add_weighted_edges_from([(asn1, asn2, self.weight)])
                        self.short_graph.add_weighted_edges_from([(asn2, asn1, 2 - self.weight)])
                        self.edges[asn1 + "-" + asn2] = 0.5
                        self.edges[asn2 + "-" + asn1] = 1.5

                        self.customer[asn1].add(asn2)
                        self.provider[asn2].add(asn1)
                        self.adjacency_list[int(asn1)].add((int(asn2), self.weight))
                        self.adjacency_list[int(asn2)].add((int(asn1), 2 - self.weight))

                    elif rel == '0':
                        self.short_graph.add_node(asn1)
                        self.short_graph.add_node(asn2)
                        self.short_graph.add_weighted_edges_from([(asn2, asn1, 1)])
                        self.short_graph.add_weighted_edges_from([(asn1, asn2, 1)])
                        self.edges[asn1 + "-" + asn2] = 1
                        self.edges[asn2 + "-" + asn1] = 1

                        self.peer[asn1].add(asn2)
                        self.peer[asn2].add(asn1)
                        self.adjacency_list[int(asn1)].add((int(asn2), 1))
                        self.adjacency_list[int(asn2)].add((int(asn1), 1))

    def getDistance(self):
        shortestDistanceList = defaultdict(list)
        self.clique = set(['174', '209', '286', '701', '1239', '1299', '2828', '2914', '3257', '3320',
                           '3356', '3491', '5511', '6453', '6461', '6762', '6830', '7018', '12956'])
        for c in self.clique:
            p = nx.shortest_path_length(self.graph, source=c)
            for k, v in p.items():
                shortestDistanceList[k].append(v)

        for node in self.graph.nodes():
            self.distance[node] = int(sum(shortestDistanceList[node]) / len(shortestDistanceList[node]))

    def getRel(self, asn1, asn2):
        if asn1 in self.customer[asn2]:
            return 0
        if asn1 in self.peer[asn2]:
            return 1
        if asn1 in self.provider[asn2]:
            return 2
        return 1

    def ASHierarchy(self):
        self.tier2 = set()
        self.direct = set()
        self.stubdirect = set()
        self.common = set()
        self.stub = set()

        allNodes = copy.deepcopy(self.clique)

        for node in self.clique:
            for cus in self.graph.neighbors(node):
                if cus in allNodes:
                    continue
                if self.graph.degree(cus) > 1000:
                    self.tier2.add(cus)
                elif self.graph.degree(cus) > 100:
                    self.direct.add(cus)
                else:
                    self.stubdirect.add(cus)
                allNodes.add(cus)
            allNodes.add(node)
        for node in self.graph.nodes():
            if not self.customer[node]:
                self.stub.add(node)
                allNodes.add(node)
        for node in self.graph.nodes():
            if node in allNodes:
                continue
            self.common.add(node)
            allNodes.add(node)

    def getHierarchy(self, asn):
        if asn in self.clique:
            return 1
        if asn in self.tier2:
            return 2
        if asn in self.direct:
            return 3
        if asn in self.stubdirect:
            return 4
        if asn in self.common:
            return 5
        if asn in self.stub:
            return 6
        return 0

    def getDegree(self, asn):
        if asn not in self.graph.nodes():
            return 0
        d = self.graph.degree(asn)
        if d < 20:
            return 7
        if d < 50:
            return 6
        if d < 100:
            return 5
        if d < 200:
            return 4
        if d < 500:
            return 3
        if d < 1000:
            return 2
        return 1

    def getEdgeRelationship(self, asn1, asn2):
        if asn1 in self.customer[asn2]:
            return 1
        if asn1 in self.peer[asn2]:
            return 2
        if asn1 in self.provider[asn2]:
            return 3
        return 0

    def calPr(self):
        self.pr = nx.pagerank(self.graph)

    def is_effictive(self, path):
        is_path = True
        weight = 2
        for i in range(len(path) - 1):
            if self.edges[path[i] + "-" + path[i+1]] < weight:
                weight = self.edges[path[i] + "-" + path[i+1]]
            if self.edges[path[i] + "-" + path[i+1]] > weight:
                is_path = False
                break
        return is_path
