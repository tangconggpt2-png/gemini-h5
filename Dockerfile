FROM ubuntu:24.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        nginx supervisor python3 python3-flask ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gemini-h5/backend /opt/frp /var/log

COPY backend/ /opt/gemini-h5/backend/
COPY defaults/ /opt/gemini-h5/defaults/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY html/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf
COPY frp/frpc /opt/frp/frpc
COPY frp/frpc.ini /opt/frp/frpc.ini

RUN chmod +x /opt/frp/frpc

EXPOSE 10000

CMD ["/entrypoint.sh"]
