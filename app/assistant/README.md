# L'assistant APC (RAG)

La recherche par le sens dans les PDF des formations : les PDF sont découpés en morceaux, chaque
morceau devient un vecteur (sentence-transformers), l'index FAISS retrouve les plus proches
d'une question. Ce composant vit hors de l'image des tableaux de bord : son environnement (torch
en version CPU) pèse 1,5 Go.

Il n'est pas encore en production : aucun conteneur ne le lance, et l'assistant du tableau de bord
APC (`app/dashboards/apc_dash/polytech_rag/`) lit les PDF directement, sans index. Le brancher sur
`apc20_chatbot` reste à faire (learnagement#T-38).

## Construire l'index

Les PDF vont dans `data/raw_pdfs/<formation>/` (ignoré par git) ; `ASSISTANT_DATA_DIR` place
`data/` ailleurs.

```bash
cd app/assistant
uv sync
uv run learnagement-assistant-chunks   # PDF → data/processed/*.json
uv run learnagement-assistant-index    # morceaux → data/indexes/faiss_index.bin
```

Le premier index télécharge le modèle `all-MiniLM-L6-v2` depuis Hugging Face.

## Le code

`src/learnagement_assistant/` : `loader.py` (PDF → pages), `cleaner.py`, `chunker.py` (pages →
morceaux), `metadata_builder.py` (catégorie d'après le nom du fichier), `embedder.py`,
`vectorstore.py` (l'index FAISS), `retriever.py`, `generator.py` (réponse qui cite ses sources),
`query_service.py` (questions guidées par formation et catégorie). Tests : `uv run pytest`.
