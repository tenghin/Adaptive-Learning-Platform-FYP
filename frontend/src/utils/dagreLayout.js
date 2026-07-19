import dagre from 'dagre';

const NODE_WIDTH = 260;
const NODE_HEIGHT = 110;

const relationColors = {
  prerequisite: '#d1495b',
  related_to: '#2a9d8f',
  part_of: '#4361ee',
  causes: '#f4a261',
};

export function layoutKnowledgeGraph(knowledgeGraph) {
  const concepts = Array.isArray(knowledgeGraph?.concepts)
    ? knowledgeGraph.concepts
    : [];
  const relationships = Array.isArray(knowledgeGraph?.relationships)
    ? knowledgeGraph.relationships
    : [];

  const graph = new dagre.graphlib.Graph();
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({
    rankdir: 'LR',
    nodesep: 48,
    ranksep: 96,
    marginx: 24,
    marginy: 24,
  });

  const nodes = concepts.map((concept) => ({
    id: concept.id,
    type: 'knowledgeNode',
    data: {
      label: concept.label,
      description: concept.description,
    },
    position: { x: 0, y: 0 },
  }));

  nodes.forEach((node) => {
    graph.setNode(node.id, {
      width: NODE_WIDTH,
      height: NODE_HEIGHT,
    });
  });

  relationships.forEach((relationship) => {
    graph.setEdge(relationship.source, relationship.target);
  });

  dagre.layout(graph);

  const positionedNodes = nodes.map((node) => {
    const graphNode = graph.node(node.id);

    return {
      ...node,
      position: {
        x: graphNode.x - NODE_WIDTH / 2,
        y: graphNode.y - NODE_HEIGHT / 2,
      },
    };
  });

  const edges = relationships.map((relationship) => ({
    id: `${relationship.source}-${relationship.target}-${relationship.type}`,
    source: relationship.source,
    target: relationship.target,
    type: 'smoothstep',
    animated: relationship.type === 'prerequisite',
    label: relationship.type.replaceAll('_', ' '),
    style: {
      stroke: relationColors[relationship.type] || relationColors.related_to,
      strokeWidth: 2,
    },
    labelStyle: {
      fill: '#12324f',
      fontWeight: 600,
    },
  }));

  return {
    nodes: positionedNodes,
    edges,
  };
}
