FROM postgis/postgis
ARG LAYER_URL_MAP

COPY db/20_municipios.sh /docker-entrypoint-initdb.d
RUN apt-get update \
 && apt-get install postgis unzip curl -y \
 && apt-get clean \
 && chmod +x /docker-entrypoint-initdb.d/20_municipios.sh \
 && localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8
# && sed -i -e "s|\"LAYER_URL_MAP\"|\"$LAYER_URL_MAP\"|" /docker-entrypoint-initdb.d/20_municipios.sh \
