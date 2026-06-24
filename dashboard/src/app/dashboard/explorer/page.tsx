"use client";

import { useMemo, useState, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Code2, Package } from "lucide-react";

function buildInitialGraphData() {
  const sourceNode: Node = {
    id: "source",
    position: { x: 400, y: 0 },
    data: {
      label: (
        <div className="text-center">
          <div className="flex justify-center mb-2"><Code2 className="text-[#1E1E1E]" size={20}/></div>
          <div className="font-bold text-[14px] font-mono text-[#1E1E1E]">validate_payment()</div>
          <div className="text-[10px] text-[#8B8D86] font-bold uppercase tracking-widest mt-2">Changed Symbol</div>
        </div>
      ),
    },
    style: {
      background: "#FAFAF8",
      color: "#1E1E1E",
      border: "1px solid #E5E5E2",
      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
      borderRadius: "8px",
      padding: "16px 20px",
      width: 200,
    },
    sourcePosition: Position.Bottom,
  };

  const repos = [
    { name: "checkout-service", tests: 45, isImpacted: true, impactedCount: 3 },
    { name: "billing-service", tests: 80, isImpacted: true, impactedCount: 2 },
    { name: "fraud-detection", tests: 35, isImpacted: true, impactedCount: 1 },
    { name: "payment-sdk-py", tests: 120, isImpacted: true, impactedCount: 2 },
    { name: "payment-sdk-node", tests: 85, isImpacted: true, impactedCount: 1 },
    { name: "compliance-svc", tests: 25, isImpacted: true, impactedCount: 1 },
    { name: "auth-service", tests: 60, isImpacted: true, impactedCount: 1 },
    { name: "reporting-dash", tests: 40, isImpacted: true, impactedCount: 1 },
    // Irrelevant repos
    { name: "user-profile", tests: 50, isImpacted: false, impactedCount: 0 },
    { name: "notification-svc", tests: 30, isImpacted: false, impactedCount: 0 },
    { name: "search-indexer", tests: 75, isImpacted: false, impactedCount: 0 },
  ];

  const initialNodes: Node[] = [sourceNode];
  const initialEdges: Edge[] = [];

  let startX = 50;
  const yOffset = 180;

  repos.forEach((repo, i) => {
    const nodeId = repo.name;
    const x = startX + (i % 6) * 160;
    const y = yOffset + Math.floor(i / 6) * 120;

    initialNodes.push({
      id: nodeId,
      position: { x, y },
      data: {
        label: (
          <div className="text-center">
            <div className="flex justify-center mb-2"><Package className="text-[#C68A3A]" size={16}/></div>
            <div className="font-bold text-[12px] mb-1 text-[#1E1E1E] truncate">{repo.name}</div>
            <div className="text-[10px] text-[#8B8D86] font-medium">{repo.tests} tests</div>
          </div>
        ),
        originalRepo: repo,
      },
      style: {
        background: "#FFFFFF",
        color: "#1E1E1E",
        border: "1px solid #E5E5E2",
        borderRadius: "8px",
        padding: "12px 16px",
        width: 140,
        opacity: 1,
        transition: "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
      },
      targetPosition: Position.Top,
      sourcePosition: Position.Bottom,
    });

    initialEdges.push({
      id: `source-${nodeId}`,
      source: "source",
      target: nodeId,
      animated: true,
      style: { stroke: "#E5E5E2", strokeWidth: 1.5, opacity: 0.5, transition: "all 0.5s ease" },
    });
  });

  return { initialNodes, initialEdges };
}

export default function ExplorerPage() {
  const { initialNodes, initialEdges } = useMemo(() => buildInitialGraphData(), []);
  
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setPhase(1), 2000);
    const timer2 = setTimeout(() => {
      setPhase(2);
      
      setNodes((nds) => 
        nds.map((node) => {
          if (node.id === "source") return node;
          
          const repo = node.data.originalRepo as any;
          if (!repo.isImpacted) {
            return {
              ...node,
              style: { ...node.style, opacity: 0.3, background: "#FAFAF8" },
            };
          } else {
            return {
              ...node,
              data: {
                ...node.data,
                label: (
                  <div className="text-center">
                    <div className="flex justify-center mb-2"><Package className="text-[#E5484D]" size={16}/></div>
                    <div className="font-bold text-[12px] mb-1 text-[#1E1E1E] truncate">{repo.name}</div>
                    <div className="text-[10px] text-[#E5484D] font-bold bg-[#F4F4F1] border border-[#E5E5E2] rounded px-2 py-0.5 inline-block">
                      {repo.impactedCount} impacted
                    </div>
                  </div>
                )
              },
              style: {
                ...node.style,
                background: "#FFFFFF",
                border: "1px solid #E5484D",
                boxShadow: "0 4px 12px rgba(229, 72, 77, 0.1)",
              }
            };
          }
        })
      );

      setEdges((eds) => 
        eds.map((edge) => {
          const targetNode = initialNodes.find(n => n.id === edge.target);
          const repo = targetNode?.data.originalRepo as any;
          
          if (!repo || !repo.isImpacted) {
            return { ...edge, animated: false, style: { ...edge.style, opacity: 0.2 } };
          }
          return {
            ...edge,
            animated: true,
            style: { stroke: "#E5484D", strokeWidth: 2, opacity: 1 },
          };
        })
      );
    }, 4000);

    return () => { clearTimeout(timer1); clearTimeout(timer2); };
  }, [initialNodes]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500 h-[calc(100vh-140px)] flex flex-col pb-12 max-w-[1400px] mx-auto w-full text-[#1E1E1E]">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-display-md mb-2">Graph Explorer</h1>
          <p className="text-[#8B8D86]">Watch Crosscut traverse the dependency graph and optimize the test suite.</p>
        </div>
        
        <div className="text-right">
          {phase === 0 && <div className="px-4 py-2 rounded bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] font-bold uppercase tracking-widest text-[10px] shadow-sm">Analyzing 418 Tests...</div>}
          {phase === 1 && <div className="px-4 py-2 rounded bg-[#F4F4F1] border border-[#C68A3A] text-[#C68A3A] font-bold uppercase tracking-widest text-[10px] flex items-center gap-2 shadow-sm"><div className="w-2 h-2 rounded-full bg-[#C68A3A] animate-pulse" />Traversing Graph...</div>}
          {phase === 2 && <div className="px-4 py-2 rounded bg-[#F4F4F1] border border-[#E5484D] text-[#E5484D] font-bold uppercase tracking-widest text-[10px] flex items-center gap-2 shadow-sm"><div className="w-2 h-2 rounded-full bg-[#E5484D]" />Reduced to 12 Tests</div>}
        </div>
      </div>

      <div className="flex-1 bg-[#FAFAF8] relative min-h-[600px] rounded-xl overflow-hidden border border-[#E5E5E2] shadow-sm">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          attributionPosition="bottom-left"
          minZoom={0.3}
          maxZoom={2}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#E5E5E2" gap={24} />
          <Controls className="bg-white border-[#E5E5E2] fill-[#1E1E1E] rounded overflow-hidden shadow-sm" />
        </ReactFlow>
      </div>
    </div>
  );
}
