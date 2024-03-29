FROM python:3.10.6

RUN groupadd --gid 1000 appuser \
    && useradd --home-dir /home/appuser --create-home --uid 1000 \
        --gid 1000 --shell /bin/sh --skel /dev/null appuser
RUN apt-get update && apt-get -y install nano && apt-get -y install ffmpeg

WORKDIR /backend

COPY poetry.lock pyproject.toml /backend/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

COPY --chown=appuser . /backend

EXPOSE 6002

RUN chown -R appuser.appuser /var /run /backend /tmp

ENTRYPOINT ["poetry", "run"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6002", "--reload", "--proxy-headers"]

