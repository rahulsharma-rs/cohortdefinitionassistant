# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/Frontend
COPY Frontend/package*.json ./
RUN npm install
COPY Frontend/ ./
RUN npm run build

# --- Stage 2: Final Image ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (if needed, e.g., for sqlite/bert models)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend and install dependencies
COPY Backend/requirements.txt ./Backend/requirements.txt

# Force CPU-only torch to save ~2.5GB of image size
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r ./Backend/requirements.txt
RUN pip install gunicorn

# Pre-download the Hugging Face model during build to avoid runtime rate-limits
RUN python -c "from llama_index.embeddings.huggingface import HuggingFaceEmbedding; HuggingFaceEmbedding(model_name='BAAI/bge-small-en-v1.5')"

# Optimize memory allocation and prevent network calls to Hugging Face
ENV MALLOC_ARENA_MAX=2
ENV HF_HUB_OFFLINE=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Copy backend code
COPY Backend/ ./Backend/

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/Frontend/dist ./Frontend/dist

# Expose port (Cloud Run uses PORT env var, defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Environment variables for models (can also be set in GCP UI)
ENV FLASK_DEBUG=false
ENV SQLITE_DB_PATH=/app/database/cohort.db
ENV VECTOR_DB_PATH=/app/database/storage
ENV CATALOG_DIR=/app/Backend/catelogue
ENV CATALOG_DESCRIPTION_FILE=/app/Backend/EHR_Population_catelogue.txt

# Start the application using gunicorn for production
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --chdir Backend app:app"]
