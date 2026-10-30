FROM python:3.14

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

# Define container app directory
RUN mkdir /app
WORKDIR /app/

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && sed -i 's/\r$//' /entrypoint.sh

EXPOSE 4000

# IMPORTANT: use entrypoint, not command
ENTRYPOINT ["/entrypoint.sh"]
# CMD ["python", "app.py"]
