FROM python:3.10.6

RUN groupadd --gid 1000 appuser \
    && useradd --home-dir /home/appuser --create-home --uid 1000 \
        --gid 1000 --shell /bin/sh --skel /dev/null appuser
RUN apt-get update && apt-get -y install nano

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./src/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./src/requirements.txt

COPY --chown=appuser . /src

COPY . .

EXPOSE 5001

RUN chown -R appuser.appuser /var /run /src /tmp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]

