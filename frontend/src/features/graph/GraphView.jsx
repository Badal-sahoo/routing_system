import { useMemo } from "react";
import { GraphCanvas } from "reagraph";

import { AGENT_STATUS_COLOR, useAgents } from "../agents/agents.hooks";
import { useEdges, useNodes } from "./graph.hooks";

const NODE_COLOR = "#3b82f6";

const MAP_SIZE = 900;

function createProjection(nodes) {
  if (nodes.length === 0) return null;

  const lats = nodes.map((node) => Number(node.lat));
  const lngs = nodes.map((node) => Number(node.lng));
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);

  const centerLat = (minLat + maxLat) / 2;
  const centerLng = (minLng + maxLng) / 2;

  const lngSquash = Math.cos((centerLat * Math.PI) / 180);
  const spanLat = maxLat - minLat || 1;
  const spanLng = (maxLng - minLng) * lngSquash || 1;
  const scale = MAP_SIZE / Math.max(spanLat, spanLng);

  return (lat, lng) => ({
    x: (Number(lng) - centerLng) * lngSquash * scale,
    y: (Number(lat) - centerLat) * scale,
    z: 0,
  });
}

export default function GraphView() {
  const nodes = useNodes();
  const edges = useEdges();
  const agents = useAgents();

  const project = useMemo(() => createProjection(nodes), [nodes]);

  const cityNodes = useMemo(() => {
    return nodes.map((node) => {
      const agentsHere = agents.filter(
        (agent) => agent.current_node_fk === node.id
      );
      const label =
        agentsHere.length > 0
          ? `${node.label} (${agentsHere.map((agent) => agent.name).join(", ")})`
          : node.label;
      const fill =
        agentsHere.length > 0
          ? AGENT_STATUS_COLOR[agentsHere[0].status] ?? AGENT_STATUS_COLOR.offline
          : NODE_COLOR;

      return { id: String(node.id), label, fill };
    });
  }, [nodes, agents]);

  const riderMarkers = useMemo(() => {
    if (project === null) return [];

    return agents
      .filter((agent) => agent.live_location)
      .map((agent) => ({
        id: `rider-${agent.id}`,
        label: `${agent.name} (live)`,
        fill: AGENT_STATUS_COLOR[agent.status] ?? AGENT_STATUS_COLOR.offline,
      }));
  }, [agents, project]);

  const graphNodes = useMemo(
    () => [...cityNodes, ...riderMarkers],
    [cityNodes, riderMarkers]
  );

  const positions = useMemo(() => {
    if (!project) return {};

    const placed = {};
    nodes.forEach((node) => {
      placed[String(node.id)] = project(node.lat, node.lng);
    });
    agents
      .filter((agent) => agent.live_location)
      .forEach((agent) => {
        placed[`rider-${agent.id}`] = project(
          agent.live_location.lat,
          agent.live_location.lng
        );
      });
    return placed;
  }, [nodes, agents, project]);

  const graphEdges = useMemo(() => {
    return edges.map((edge) => ({
      id: `edge-${edge.id}`,
      source: String(edge.from_node_fk),
      target: String(edge.to_node_fk),
      label: `${edge.weight} min`,
    }));
  }, [edges]);

  const layoutOverrides = useMemo(
    () => ({
      getNodePosition: (id) => positions[id] ?? { x: 0, y: 0, z: 0 },
    }),
    [positions]
  );

  return (
    <div style={{ height: "100%", width: "100%", position: "relative" }}>
      {cityNodes.length === 0 ? (
        <p style={{ padding: "1rem", opacity: 0.6 }}>
          No places loaded. Everything that shows a place name falls back to a
          raw id until the graph arrives — press Reload in the header, or seed
          the city with <code>manage.py seed_city --reset</code>.
        </p>
      ) : (
        <GraphCanvas
          nodes={graphNodes}
          edges={graphEdges}
          layoutType="custom"
          layoutOverrides={layoutOverrides}
          animated={false}
          edgeArrowPosition="none"
        />
      )}
    </div>
  );
}
