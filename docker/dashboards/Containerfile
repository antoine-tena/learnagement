FROM python:3.14@sha256:e5de6bc932256f8138c2353023dc4fd24d010d72f6b5cb06be126f0a4cd53784

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

# Bibliothèques système installées une fois, à la création de l'image
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

# Define container app directory
RUN mkdir /app
WORKDIR /app/

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && sed -i 's/\r$//' /entrypoint.sh

EXPOSE 8050

# IMPORTANT: use entrypoint, not command
RUN useradd --system --create-home --shell /usr/sbin/nologin app
USER app
ENTRYPOINT ["/entrypoint.sh"]
# CMD ["python", "main.py"]
