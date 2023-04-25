FROM python:3.10.6

RUN groupadd --gid 1000 appuser \
    && useradd --home-dir /home/appuser --create-home --uid 1000 \
        --gid 1000 --shell /bin/sh --skel /dev/null appuser
RUN apt-get update && apt-get -y install ffmpeg\
    && apt-get -y install nano

WORKDIR /app
#ENTRYPOINT ["./docker-entrypoint.sh"]

#RUN pip install uvicorn fastapi

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./app/requirements.txt

COPY --chown=appuser . /app

COPY . .

EXPOSE 5001

RUN chown -R appuser.appuser /var /run /app /tmp

#ENV APP_VERSION=1.0
#ENV APP_NAME=web_app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
# CMD [ "python", "-u", "main.py"]


