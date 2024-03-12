FROM python:3.11.3-slim-bullseye as base

USER 0
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get -qq update \
    && apt-get -qq install -y gcc make libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install poetry==1.5.1
COPY src/pyproject.toml /app/pyproject.toml
COPY src/poetry.lock /app/poetry.lock

RUN poetry config virtualenvs.create false
RUN poetry install

COPY src /app

EXPOSE 8000

CMD ["make", "run_prod"]
