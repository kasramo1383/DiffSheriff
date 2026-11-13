# Offline overlay on the retained workflow compiler/runtime image.
# Tag sha256:e8c4e3dd4d497a15b4973a0cd575b246538490fc80909990eb4c0411581372b5
# as diffsheriff:minimized-results-base before building.
FROM diffsheriff:minimized-results-base
WORKDIR /opt/diffsheriff
COPY pyproject.toml README.md ./
COPY diffsheriff/ diffsheriff/
RUN pip install --no-cache-dir --no-build-isolation --no-deps .
WORKDIR /src
