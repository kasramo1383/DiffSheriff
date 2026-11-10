FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    llvm \
    gdb \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-venv \
    binutils \
    patchelf \
    libelf-dev \
    valgrind \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /workspace

COPY pyproject.toml .
COPY README.md .
COPY diffsheriff/ diffsheriff/

RUN pip install --no-cache-dir .

ENTRYPOINT ["diffsheriff"]
