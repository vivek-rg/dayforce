# Single-container build for hosting: FastAPI serves the API and the built frontend on one origin.

FROM node:22-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/
RUN npm ci --workspace frontend --include-workspace-root=false
COPY frontend frontend
RUN npm run build --workspace frontend

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend backend
COPY fixtures fixtures
COPY scripts/serve.py scripts/
COPY --from=frontend /app/frontend/dist frontend/dist
EXPOSE 8000
CMD ["python", "scripts/serve.py"]
