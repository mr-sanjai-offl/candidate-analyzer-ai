'use client'

import * as React from 'react'
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  NodeProps,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

type SkillNodeProps = NodeProps<Node<{ label: string; category: string }>>
type EvidenceNodeProps = NodeProps<Node<{ label: string; confidence: number }>>

// Custom Skill Node component inside react flow
function SkillNode({ data }: SkillNodeProps) {
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border-2 border-primary text-card-foreground">
      <div className="flex items-center">
        <div className="ml-2">
          <div className="text-sm font-bold">{data.label}</div>
          <div className="text-xs text-muted-foreground">Skill • {data.category}</div>
        </div>
      </div>
    </div>
  )
}

// Custom Evidence Node component inside react flow
function EvidenceNode({ data }: EvidenceNodeProps) {
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border border-muted-foreground/30 text-card-foreground">
      <div className="text-sm font-semibold">{data.label}</div>
      <div className="text-xs text-muted-foreground">Confidence: {data.confidence}%</div>
    </div>
  )
}

const nodeTypes = {
  skillNode: SkillNode,
  evidenceNode: EvidenceNode,
}

interface KnowledgeGraphProps {
  nodes: Node[]
  edges: Edge[]
}

export function KnowledgeGraph({ nodes: initialNodes, edges: initialEdges }: KnowledgeGraphProps) {
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  return (
    <div className="w-full h-[400px] border rounded-lg overflow-hidden bg-muted/10 relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background gap={12} size={1} />
      </ReactFlow>
      
      {/* Legend overlay */}
      <div className="absolute bottom-4 right-4 bg-background/90 backdrop-blur border p-3 rounded shadow-md text-xs space-y-1.5 z-10">
        <p className="font-semibold text-muted-foreground">Graph Legend</p>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-sm border-2 border-primary bg-card" />
          <span>Capability Skill Node</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-sm border border-muted-foreground/30 bg-card" />
          <span>Evaluation Evidence Statement</span>
        </div>
      </div>
    </div>
  )
}
