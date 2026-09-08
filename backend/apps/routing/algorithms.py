import heapq


def dijkstra(adjacency, source):
    distances = {source: 0}
    queue = [(0, source)]

    while queue:
        dist, node = heapq.heappop(queue)
        if dist > distances.get(node, float("inf")):
            continue

        for neighbor, weight in adjacency.get(node, []):
            candidate = dist + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))

    return distances


def shortest_path(adjacency, source, target):
    if source == target:
        return [source], 0

    distances = {source: 0}
    came_from = {}
    queue = [(0, source)]

    while queue:
        dist, node = heapq.heappop(queue)
        if dist > distances.get(node, float("inf")):
            continue
        if node == target:
            break

        for neighbor, weight in adjacency.get(node, []):
            candidate = dist + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                came_from[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    if target not in distances:
        return None, None

    path = [target]
    while path[-1] != source:
        path.append(came_from[path[-1]])
    path.reverse()

    return path, distances[target]
