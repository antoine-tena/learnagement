# Utiliser l'image officielle de Node.js
FROM node:26-alpine@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5

#RUN apk add --no-cache --upgrade bash

# Définir le répertoire de travail dans le conteneur
RUN mkdir /app
WORKDIR /app

# pnpm installe les dépendances du front (pnpm-lock.yaml)
RUN npm install -g pnpm@12.8.1

# Copier les fichiers nécessaires pour installer les dépendances
#COPY package.json pnpm-lock.yaml ./

# Supprimer les dépendances existantes et les réinstaller
#RUN pnpm install --frozen-lockfile

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && sed -i 's/\r$//' /entrypoint.sh

# Exposer le port 3000 pour le serveur Next.js
EXPOSE 3000

# IMPORTANT: use entrypoint, not command
USER node
ENTRYPOINT ["/entrypoint.sh"]
