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

    SQL="select count(*) as cnt from $LAYER where geometrytype(geom) like '%POLYGON%'"
    POLYGON_CNT=$(echo "$SQL" | psql --pset=tuples_only geodb)
    if [ $POLYGON_CNT =  0 ] ; then
        echo "Dropping layer $LAYER because it doesn't contain (multi-polygons)"
        psql --dbname="$POSTGRES_DB" <<EOSQL
drop table $LAYER;
EOSQL
    else
        psql --dbname="$POSTGRES_DB" <<EOSQL
grant select on $LAYER to $GEODB_USER;
EOSQL
    fi
done
