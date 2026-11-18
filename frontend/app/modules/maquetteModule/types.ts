import type { Node } from "@xyflow/react";

/** Une dépendance entre séquences, telle que la renvoie `selectMaquette`. */
export interface SequenceDependency {
  "séance précédente": string;
  "séance suivante": string;
}

export interface ModuleSequenceNodeData extends Record<string, unknown> {
  label: string;
  color: string;
  session?: string;
}

export type ModuleSequenceNode = Node<ModuleSequenceNodeData, "customNode">;

/** La séquence affichée dans la carte, après un clic sur son nœud. */
export interface CourseData {
  label?: string;
  moduleCode?: string;
  session?: string;
  duration?: number;
  color?: string;
  typeCourse?: string;
  currentNumber?: number;
  totalNumber?: number;
}
