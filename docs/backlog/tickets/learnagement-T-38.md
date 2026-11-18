# learnagement#T-38 · Le RAG hors de l'image Dash
- **Type**: improvement
- **Priority**: 🟠 important
- **Status**: in progress — branch feat/t38, since 2026-11-18
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: @antoine-tena · **Due**: —
- **Origin**: revue de l'architecture ; priorité relevée le 2026-11-17 (serveur déjà surchargé)

`dashboards/apc_dash/polytech_rag/` embarque `sentence-transformers` et `faiss-cpu` dans l'image
de tous les tableaux de bord. Le sortir dans son propre conteneur, appelé par `apc20_chatbot`, en
respectant [AI-FEATURES].

La recherche vectorielle n'était importée par aucune page : l'assistant du tableau de bord
(`FileService`) lit les PDF avec PyMuPDF seul, et `apc20_chatbot` (Groq) ne l'appelle pas.

- [x] Sortir le pipeline vectoriel dans son composant `assistant/` (`learnagement_assistant`,
  torch en version CPU), avec ses tests et son job de CI
- [x] Retirer `faiss-cpu` et `sentence-transformers` (donc torch et CUDA) de l'image Dash
- [ ] Construire l'index sur les vrais PDF des formations (absents du repo, à demander)
- [ ] Le conteneur de l'assistant (`Containerfile`, fragment compose, sondes) et son appel par
  `apc20_chatbot`, comme outil, par une file d'attente ([AI-FEATURES])
