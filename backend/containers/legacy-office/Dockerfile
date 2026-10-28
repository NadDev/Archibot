FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libreoffice-writer libreoffice-impress python3 coreutils fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY convert.py /opt/archibot/convert.py
USER 65534:65534
ENV HOME=/work
WORKDIR /work
ENTRYPOINT ["/usr/bin/python3", "/opt/archibot/convert.py"]