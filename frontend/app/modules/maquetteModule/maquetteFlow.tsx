import React, { useState, useCallback, useEffect, useRef } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  type Connection,
  type Edge,
  type EdgeTypes,
  type NodeProps,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import FloatingEdge from "./floatingEdge";
import CustomNode from "@/app/modules/maquetteModule/customNode";
import floatingConnectionLine from "@/app/modules/maquetteModule/floatingConnectionLine";
import CourseCard from "@/app/modules/maquetteSequence/courseCard";
import type { CourseData, ModuleSequenceNode } from "@/app/modules/maquetteModule/types";

export default function MaquetteFlow({initialNodes, initialEdges, setWidth}:{ initialNodes: ModuleSequenceNode[], initialEdges: Edge[], setWidth: (width: number) => void}) {
  const componentRef = useRef<HTMLDivElement>(null);
  const { fitView } = useReactFlow();
  const [majWidth, setMajWidth] = useState(0);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const [displayCardCourse, setDisplayCardCourse] = useState<CourseData>({});

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      fitView({ padding: 0.1, duration: 700 });
    }, 100);

    return () => clearTimeout(timeout);

  }, [majWidth, initialEdges, initialNodes]);

  useEffect(() => {
    const element = componentRef.current;
    if (!element) return;

    const resizeObserver = new ResizeObserver((entries) => {
      if (entries.length > 0) {
        const newWidth = entries[0].contentRect.width;
        setWidth(newWidth);
        setMajWidth(newWidth);
      }
    });

    resizeObserver.observe(element);
    return () => resizeObserver.disconnect();
  }, []);

  const onConnect = useCallback(
    (params: Connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: "floating",
            markerEnd: { type: MarkerType.ArrowClosed },
          },
          eds
        )
      ),
    [setEdges]
  );

  const nodeTypes: NodeTypes = {
    customNode: (nodeProps: NodeProps<ModuleSequenceNode>) => (
      <CustomNode {...nodeProps} setDisplayCardCourse={setDisplayCardCourse} />
    ),
  };

  const edgeTypes: EdgeTypes = {
    floating: FloatingEdge,
  };

  const formatDuration = (duration: number | undefined) => {
    if (duration === undefined) return "N/A";
    const hours = Math.floor(duration);
    const minutes = Math.round((duration - hours) * 60);
    return `${hours}h ${minutes > 0 ? minutes + "min" : ""}`;
  };

  const colorSelector = (type: string | undefined) => {
    if (type === "CM") {
        return "bg-cm-red";
      } else if (type === "TD") {
        return "bg-td-green";
      } else if (type === "TP") {
        return "bg-tp-yellow";
      } else if (type === "Exam") {
        return "bg-exam-blue";
      } else {
        return "bg-other-pink";
      }
  }

  return (
    <div ref={componentRef} style={{ height: "100%", width: "100%" }}>
      {nodes.length === 0 && edges.length === 0 ? (
        <div className={"h-full w-full flex items-center justify-center"}>
          <p className={"font-bold text-2xl text-usmb-red"}>
            Pas de maquette à afficher
          </p>
        </div>
      ) : (
        <div style={{ height: "100%", width: "100%" }}>
          {displayCardCourse && Object.keys(displayCardCourse).length > 0 && (
            <CourseCard
              label={displayCardCourse.label || "N/A"}
              type={displayCardCourse.typeCourse || "N/A"}
              moduleCode={displayCardCourse.moduleCode || "N/A"}
              session={`${displayCardCourse.currentNumber || "N/A"}/${displayCardCourse.totalNumber || "N/A"}`}
              duration={formatDuration(displayCardCourse.duration) || "N/A"}
              bgColor={colorSelector(displayCardCourse.typeCourse)}
            />
          )}
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            onConnect={onConnect}
            connectionLineComponent={floatingConnectionLine}
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      )}
    </div>
  );
}
