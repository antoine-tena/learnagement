"use client";

import axios from "axios";
import React, { useEffect, useMemo, useState } from "react";
import { MarkerType, Position, ReactFlowProvider, type Edge } from "@xyflow/react";

import MaquetteFlow from "@/app/modules/maquetteModule/maquetteFlow";
import Loader from "@/app/indicators/loading";
import type { ModuleSequenceNode, SequenceDependency } from "@/app/modules/maquetteModule/types";

const PREVIOUS = "séance précédente";
const NEXT = "séance suivante";
const NODE_SPACING = 200;
const ERROR_DELAY_MS = 2000;
const SESSION_TYPE_COLORS: Record<string, string> = {
  CM: "bg-cm-red",
  TD: "bg-td-green",
  TP: "bg-tp-yellow",
  Ex: "bg-exam-blue",
};
const DEFAULT_COLOR = "bg-other-pink";
const NO_MAQUETTE: SequenceDependency[] = [];

interface LoadedMaquette {
  code_module: string;
  maquette: SequenceDependency[];
}

/* liste des séances de cours dans le bon ordre (selon les liens) */
function getSeances(maquette: SequenceDependency[]): string[] {
  const seances = [maquette[0][PREVIOUS], maquette[0][NEXT]];
  let seanceSuiv = maquette[0][NEXT];

  for (let i = 0; i < maquette.length; i++) {
    const index = maquette.findIndex((link) => link[PREVIOUS] === seanceSuiv);

    if (index != -1) {
      seanceSuiv = maquette[index][NEXT];
      seances.push(seanceSuiv);
    } else {
      /* Traitement du cas où il y a une rupture dans les liens de tous les cours */
      seanceSuiv = maquette[i][NEXT];
      seances.push(maquette[i][PREVIOUS], seanceSuiv);
    }
  }

  return [...new Set(seances)];
}

/* placement des nœuds en lignes, selon la largeur d'écran (-1 : pas encore mesurée) */
function createNodes(maquette: SequenceDependency[], width: number): ModuleSequenceNode[] {
  let x = 0;
  let y = 0;

  return getSeances(maquette).map((seance) => {
    const node: ModuleSequenceNode = {
      id: seance,
      type: "customNode",
      position: { x: x, y: y },
      data: { label: seance, color: SESSION_TYPE_COLORS[seance.slice(0, 2)] ?? DEFAULT_COLOR },
      sourcePosition: Position.Right, // Les liens sortent par la droite
      targetPosition: Position.Left, // Les liens entrent par la gauche
    };

    if (x >= width && width != -1) {
      y += NODE_SPACING;
      x = 0;
    } else {
      x += NODE_SPACING;
    }
    return node;
  });
}

function createEdges(maquette: SequenceDependency[]): Edge[] {
  return maquette.map((link) => ({
    id: link[PREVIOUS] + "-" + link[NEXT],
    source: link[PREVIOUS],
    target: link[NEXT],
    animated: true,
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 30,
      height: 30,
    },
    type: "floating",
  }));
}

export default function MaquetteModule({code_module}: {code_module: string; }) {
  const [loaded, setLoaded] = useState<LoadedMaquette | null>(null);
  const [width, setWidth] = useState(-1);
  const isLoading = loaded?.code_module !== code_module;
  const maquette = loaded?.maquette ?? NO_MAQUETTE;

  useEffect(() => {
    const showEmptyLater = () => setTimeout(() => setLoaded({ code_module, maquette: [] }), ERROR_DELAY_MS);
    const loadMaquette = async () => {
      const form_data = new FormData();
      form_data.append("code_module", code_module);
      try {
        const response = await axios.post("/api/proxy/select/selectMaquette", form_data, {withCredentials: true});
        if (response.status == 200) {
          setLoaded({ code_module, maquette: response.data });
        } else {
          console.error(response.data);
          showEmptyLater();
        }
      } catch (error) {
        console.error("selectMaquette :", axios.isAxiosError(error) ? error.response?.status : error);
        showEmptyLater();
      }
    };
    loadMaquette();
  }, [code_module]);

  /* création des nodes des edges (besoins de la largeur d'écran pour placer les nodes) */
  const nodes = useMemo(() => (maquette.length > 0 ? createNodes(maquette, width) : []), [maquette, width]);
  const edges = useMemo(() => createEdges(maquette), [maquette]);

  return (
    <div className={"h-screen w-full"}>
      {!isLoading ? (
        <ReactFlowProvider>
          <MaquetteFlow
            initialNodes={nodes}
            initialEdges={edges}
            setWidth={setWidth}
          />
        </ReactFlowProvider>
      ) : (
        <div className={"h-full w-full flex items-center justify-center"}>
          <Loader />
        </div>
      )}
    </div>
  );
}
