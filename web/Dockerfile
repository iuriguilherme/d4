FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/base.txt
COPY requirements/web.txt requirements/web.txt
RUN pip install --no-cache-dir -r requirements/web.txt

COPY web/ web/

ENV PYTHONPATH=/app
ENV FLASK_APP=web.app:create_app
ENV FLASK_ENV=development

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]
