FROM python

ENV POETRY_VERSION=1.8.3 \
POETRY_VIRTUALENVS_CREATE=false \
POETRY_CACHE_DIR='/var/cache/pypoetry' \
POETRY_HOME='/usr/local' \
PYTHONPATH='.'

COPY api api
COPY main.py .
COPY generate.py .
COPY pyproject.toml .
COPY startup.sh .
COPY config.toml .
COPY credls.json .
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN poetry install --no-interaction --no-root
