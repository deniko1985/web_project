# FROM node:20.5 AS build
# WORKDIR /app
# COPY package*.json ./
# RUN npm install -g http-server
# COPY . .

# EXPOSE 6001

# RUN npm run build

# CMD [ "http-server", "dist", "host", "0.0.0.0", "port", "6001" ]

FROM nginx:1.25.1

RUN groupadd --gid 1000 appuser \
    && useradd --home-dir /home/appuser --create-home --uid 1000 \
        --gid 1000 --shell /bin/sh --skel /dev/null appuser
RUN apt-get update && apt-get -y install nano

COPY ./src/ /var/www

EXPOSE 6001

RUN rm /var/log/nginx/*

# CMD ["nginx", "-g", "daemon off;"]