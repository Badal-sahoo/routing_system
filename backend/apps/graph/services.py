from collections import defaultdict

from .models import Edge


def build_adjacency():
    adjacency = defaultdict(list)
    rows = Edge.objects.values_list(
        "from_node_fk_id", "to_node_fk_id", "weight", "is_bidirectional"
    )
    for from_id, to_id, weight, is_bidirectional in rows:
        adjacency[from_id].append((to_id, weight))
        if is_bidirectional:
            adjacency[to_id].append((from_id, weight))
    return adjacency


def reverse_adjacency(adjacency):
    reversed_adjacency = defaultdict(list)
    for node, neighbours in adjacency.items():
        for neighbour, weight in neighbours:
            reversed_adjacency[neighbour].append((node, weight))
    return reversed_adjacency
