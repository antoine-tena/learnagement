# learnagement#T-38 · Le RAG hors de l'image Dash
- **Type**: improvement
- **Priority**: 🟠 important
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture ; priorité relevée le 2026-11-17 (serveur déjà surchargé)

`dashboards/apc_dash/polytech_rag/` embarque `sentence-transformers` et `faiss-cpu` dans l'image
de tous les tableaux de bord. Le sortir dans son propre conteneur, appelé par `apc20_chatbot`, en
respectant [AI-FEATURES].
