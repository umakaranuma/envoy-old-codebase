# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13
 
FROM python:${PYTHON_VERSION}-slim AS builder
 
WORKDIR /usr/src/app
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
&& rm -rf /var/lib/apt/lists/*
 
RUN pip install --upgrade pip
 
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 

FROM python:${PYTHON_VERSION}-slim AS final

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
&& rm -rf /var/lib/apt/lists/*
 

RUN useradd -m -r django && \
    mkdir -p /app/logs && \
    chown -R django:django /app
 

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
WORKDIR /app
COPY --chown=django:django . .
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
 
USER django
 
EXPOSE 8000
 
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "envoy.wsgi:application"]