# Stage 1: Build the UI
FROM node:20-slim AS build-stage
WORKDIR /ui
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy the built UI from Stage 1 into a directory outside the synced volume
COPY --from=build-stage /ui/dist /app/static

# Set working directory to root for consistent app package imports
WORKDIR /app

# Expose port (internal)
EXPOSE 8000

# Run uvicorn as a package
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
