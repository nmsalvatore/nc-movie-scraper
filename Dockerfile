FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROMIUM_PATH=/usr/bin/chromium

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

RUN useradd -m mumble \
    && chown -R mumble:mumble /app
USER mumble

CMD ["python", "-m", "moviescraper"]
