import { useEffect, useMemo } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
} from 'reactflow';
import { layoutKnowledgeGraph } from '../utils/dagreLayout';

function KnowledgeNode({ data }) {
  return (
    <Paper
      elevation={3}
      sx={{
        minWidth: 220,
        maxWidth: 260,
        px: 2,
        py: 1.5,
        border: '1px solid rgba(18, 50, 79, 0.12)',
        borderRadius: 3,
        background: 'linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%)',
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: '#12324f' }} />
      <Typography variant="subtitle2" fontWeight={700} gutterBottom>
        {data.label}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {data.description || 'Concept from the generated knowledge graph.'}
      </Typography>
      <Handle type="source" position={Position.Right} style={{ background: '#12324f' }} />
    </Paper>
  );
}

const nodeTypes = {
  knowledgeNode: KnowledgeNode,
};

export function LessonMindMap({ knowledgeGraph }) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!knowledgeGraph) {
      return { nodes: [], edges: [] };
    }

    return layoutKnowledgeGraph(knowledgeGraph);
  }, [knowledgeGraph]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialEdges, initialNodes, setEdges, setNodes]);

  if (!knowledgeGraph) {
    return (
      <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Generate a mind map to visualize the lesson concepts.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box
      sx={{
        height: 560,
        borderRadius: 3,
        overflow: 'hidden',
        border: '1px solid rgba(18, 50, 79, 0.12)',
        background: 'linear-gradient(180deg, #ffffff 0%, #f4f7fc 100%)',
      }}
    >
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          nodesDraggable
          elementsSelectable
          defaultEdgeOptions={{
            type: 'smoothstep',
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          }}
        >
          <Background gap={20} size={1} color="#dbe6f4" />
          <Controls />
          <MiniMap zoomable pannable />
        </ReactFlow>
      </ReactFlowProvider>
    </Box>
  );
}
