# Optional. The main path is the npm commands in README. Local, synthetic demo only.
FROM node:22-slim AS frontend
WORKDIR /build
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/
RUN npm ci --workspace frontend --include-workspace-root
COPY frontend frontend
RUN npm run build --workspace frontend

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend backend
COPY fixtures fixtures
COPY --from=frontend /build/frontend/dist frontend/dist
RUN useradd --create-home onboardiq && mkdir -p /app/.runtime && chown onboardiq /app/.runtime
USER onboardiq
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --retries=5 CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
