FROM python:3.8

WORKDIR /bot

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry install --no-root && apt update && apt install sqlite3

COPY *.py ./

COPY createdb.sql ./

ENTRYPOINT [ "python", "server.py" ]