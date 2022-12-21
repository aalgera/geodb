#!/bin/bash
set -e
export PGUSER="$POSTGRES_USER"

echo "Creating user $GEODB_USER"
psql --dbname="$POSTGRES_DB" <<EOSQL
create role $GEODB_USER with login password '$GEODB_PASSWORD';
EOSQL

cd /tmp
echo "Downloading shapefiles and converting postgis format"
for L in $LAYER_URL_MAP; do
    arrL=(${L//,/ })
    LAYER=${arrL[0]} 
    URL=${arrL[1]}
    FILE=$(basename ${URL})

    curl --output $FILE "$URL"
    unzip $FILE
    shp2pgsql -s ${SRID:-4326} -D -I $FILE $LAYER 2>/dev/null | psql --dbname="$POSTGRES_DB"
    rm -f /tmp/*
    psql --dbname="$POSTGRES_DB" <<EOSQL
grant select on $LAYER to $GEODB_USER;
EOSQL
done
