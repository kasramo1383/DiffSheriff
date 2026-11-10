FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential clang libclang-rt-18-dev llvm cmake git \
    python3 python3-pip python3-venv python3-yaml python3-click python3-pyelftools \
    binutils ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV HOME=/tmp
WORKDIR /opt/diffsheriff
COPY pyproject.toml README.md ./
COPY diffsheriff/ diffsheriff/
RUN pip install --no-cache-dir --no-build-isolation --no-deps .
WORKDIR /src
ENTRYPOINT ["diffsheriff"]
