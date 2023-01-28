## Introduction
While lookups of coordinates in a polygon layer can be done on a one by one basis,
this tends to be rather slow, certainly if one needs to do thousands of coordinate lookups.
In this project a block of multiple coordinates in a csv file is processed leading
to much faster responses.

## Prerequisites
Computer with docker and docker-compose

## Setup
Clone this project and cd into it:
```
git clone https://github.com/aalgera/geodb.git
cd geodb
```

Now we have to build the docker images for the database and the api service by
running the command:
```
docker-compose build
```

On creation of the database, polygon layers will be created for Brazilian municipalities 
and states.
If you want to change or add layers, edit the LAYER\_URL\_MAP the _docker-compose.yaml_ file
__before__ starting the database for the first time. The shapefiles have to use the shp.zip format.

To start services run:
```
docker-compose up -d
```
To stop services run:
```
docker-compose down
```
To stop service and destroy the database volume:
```
docker-compose down -v
```

## Usage
This service provides 2 methods:
- _/geodb-api/lists_ lists the available layers and its attibutes. 
  Returns a json object that can be used as input for _/geodb-api/search_
- _/geodb-api/search_ searches the configured layers for polygons that match
  the coordinates in the coordinates file using the POST method or a single pair 
  of coordinates using the GET method

The json object returned by _list-layers_ has the following format:
```
{
  "layer1": {
    "column1": "alias1",
    "column2": "alias2",
    ....
  },
  "layer2": {
    "column1": "alias1",
    "column2": "alias2",
    ....
  },
  ...
}
```

You may also want to try the swagger interface on http://localhost:8080/docs for testing.

## Examples

Listing the available layers
```
curl -X GET 'http://localhost:8080/geodb-api/list'
```
Output:
```
{"municipios":"*","ufs":"*"}
```

Listing the available layers with columns
```
curl -X GET 'http://localhost:8080/geodb-api/list?include_columns=1'
```
Output:
```
{"municipios":{"gid":"mun_gid","cd_mun":"mun_cd_mun","nm_mun":"mun_nm_mun","sigla":"mun_sigla","area_km2":"mun_area_km2"},"ufs":{"gid":"ufs_gid","cd_uf":"ufs_cd_uf","nm_uf":"ufs_nm_uf","sigla":"ufs_sigla","nm_regiao":"ufs_nm_regiao"}}
```

Listing specific layers with columns
```
curl -X GET 'http://localhost:8080/geodb-api/list?include_columns=1&select_layer=ufs&select_layer=municipios'
```
Output:
```
{"municipios":{"gid":"mun_gid","cd_mun":"mun_cd_mun","nm_mun":"mun_nm_mun","sigla":"mun_sigla","area_km2":"mun_area_km2"},"ufs":{"gid":"ufs_gid","cd_uf":"ufs_cd_uf","nm_uf":"ufs_nm_uf","sigla":"ufs_sigla","nm_regiao":"ufs_nm_regiao"}}
```

Find data of a single point using the GET method of _search-layers_
```
curl -G --data-urlencode 'layers_def={"municipios":"*"}' \
    'http://localhost:8080/geodb-api/search?lat=-15.892&lon=-47.897&include_coordinates=0'
```
Output:
```
{"id":0,"mun_gid":5572,"mun_cd_mun":"5300108","mun_nm_mun":"Brasília","mun_sigla":"DF","mun_area_km2":5760.784}
```

Before being able to use POST method of _search-layers_, we need to create a file with some coordinates:
```
cat <<EOM > test.csv
id,lat,lon
78,-16.6841,-44.3635
79,-12.2333,-38.7487
80,-24.7971,-53.3006
81,-22.0267,-42.3648
EOM
```

Getting all available columns of the ufs layer:
```
curl -X 'POST' 'http://localhost:8080/geodb-api/search' \
     -F 'layers_def={"ufs":"*"}' \
     -F 'coordinates_file=@test.csv;type=text/csv'
```
Output:
```
id,ufs_gid,ufs_cd_uf,ufs_nm_uf,ufs_sigla,ufs_nm_regiao
78,17,31,Minas Gerais,MG,Sudeste
79,16,29,Bahia,BA,Nordeste
80,21,41,Paraná,PR,Sul
81,19,33,Rio de Janeiro,RJ,Sudeste
```

Using multiple layers and aliases:

```
curl -X 'POST' 'http://localhost:8080/geodb-api/search' \
-F 'layers_def={"municipios":{"cd_mun":"cod_ibge","nm_mun":"nom_mun","sigla":"sig_uf"},"ufs":{"nm_uf":"nom_uf","nm_regiao":"nom_regiao"}}' \
-F 'coordinates_file=@test.csv;type=text/csv'
```
Output:
```
id,cod_ibge,nom_mun,sig_uf,nom_uf,nom_regiao
78,3118809,Coração de Jesus,MG,Minas Gerais,Sudeste
79,2908903,Coração de Maria,BA,Bahia,Nordeste
80,4106308,Corbélia,PR,Paraná,Sul
81,3301504,Cordeiro,RJ,Rio de Janeiro,Sudeste
```
