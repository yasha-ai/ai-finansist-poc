# Stage 1: Build frontend
FROM node:22-slim AS frontend
WORKDIR /frontend
COPY package*.json ./
RUN npm ci
COPY app/ ./app/
COPY next.config.js ./
COPY .env* ./
RUN npx next build

# Stage 2: Backend + serve frontend
FROM python:3.12-slim
WORKDIR /app

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ .

# Copy frontend static build
COPY --from=frontend /frontend/out ./frontend/out

ENV PORT=3000
EXPOSE 3000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
