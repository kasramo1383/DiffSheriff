# Offline verification overlay using the retained native runtime's dependencies.
# Tag sha256:55d389e754d88b310bbbda5b12c72225ff4e0d37d4749a4be79679671ccc4e00
# as diffsheriff:verification-base before building this overlay.
FROM diffsheriff:verification-base
WORKDIR /opt/diffsheriff
COPY pyproject.toml README.md ./
COPY diffsheriff/ diffsheriff/
RUN pip install --no-cache-dir --no-build-isolation --no-deps .
WORKDIR /src
