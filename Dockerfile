# Production
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS prod

EXPOSE 5051
WORKDIR /src

# --- add toolchain ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (needed by maturin/fastuuid)
RUN curl -fsSL https://sh.rustup.rs | sh -s -- -y \
 && /root/.cargo/bin/rustc --version
ENV PATH="/root/.cargo/bin:${PATH}"
# --- end toolchain ---

# copy files
COPY mcp_services/client.py .
COPY creds.env .
COPY requirements.txt .

# install deps
RUN uv pip install --no-cache-dir -r requirements.txt --system

ENTRYPOINT ["python3"]
CMD ["client.py"]
