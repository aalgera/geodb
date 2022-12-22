FROM postgis/postgis

COPY db/20_geodb.sh /docker-entrypoint-initdb.d
RUN apt-get update \
 && apt-get install postgis unzip curl -y \
 && apt-get clean \
 && chmod +x /docker-entrypoint-initdb.d/20_geodb.sh \
 && localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8
