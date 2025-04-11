FROM python

ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    PYTHONPATH='/app'

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

VOLUME /app

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry install --no-interaction --no-root

CMD ["bash", "startup.sh"]