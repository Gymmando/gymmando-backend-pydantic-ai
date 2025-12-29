FROM python:3.12-slim

# Install system dependencies required by LiveKit and GObject
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/gymmando_graph/

CMD ["python", "-u", "-m", "gymmando_graph.livekit_agent", "start"]
