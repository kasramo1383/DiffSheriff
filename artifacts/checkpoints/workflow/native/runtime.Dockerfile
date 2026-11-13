# Offline overlay on the previously verified compiler/runtime image.
# Tag sha256:ec88e772250a0af68a300f5b17eaccc37f401a6b024d2b14add921a3c071c482
# as diffsheriff:workflow-base before building.
FROM diffsheriff:workflow-base
WORKDIR /opt/diffsheriff
COPY pyproject.toml README.md ./
COPY diffsheriff/ diffsheriff/
RUN pip install --no-cache-dir --no-build-isolation --no-deps .
WORKDIR /src
