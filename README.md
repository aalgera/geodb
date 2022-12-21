## Introduction
While lookups of coordinates in a polygon layer can be done on a one by one basis,
this tends to be rather slow, certainly if one needs to do thousands of coordinate lookups.
In this project a block of multiple coordinates in a csv file is processed leading
to much faster responses.

## Prerequisites
Computer with docker and docker-compose

## Setup
First we have to build the docker images for the database and the api service by
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
The api service provides 2 methods:
- _list-layers_ lists the available layers and its attibutes. 
  Returns a json object that can be used as input for _get_layers_
- _get-layers_ lists atribute data for each of the configures data

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

You can try the swagger on http://localhost:8080/docs for testing.

## Examples

Listing the available layers
```
curl -X GET 'http://localhost:8080/list-layers'
```
Output:
```
{"municipios":"*","ufs":"*"}
```

Listing the available layers with columns
```
curl -X GET 'http://localhost:8080/list-layers?include_columns=1'
```
Output:
```
{"municipios":{"gid":"mun_gid","cd_mun":"mun_cd_mun","nm_mun":"mun_nm_mun","sigla":"mun_sigla","area_km2":"mun_area_km2"},"ufs":{"gid":"ufs_gid","cd_uf":"ufs_cd_uf","nm_uf":"ufs_nm_uf","sigla":"ufs_sigla","nm_regiao":"ufs_nm_regiao"}}
```

Listing specific layers with columns
```
curl -X GET 'http://localhost:8080/list-layers?include_columns=1&select_layer=ufs&select_layer=municipios'
```
Output:
```
{"municipios":{"gid":"mun_gid","cd_mun":"mun_cd_mun","nm_mun":"mun_nm_mun","sigla":"mun_sigla","area_km2":"mun_area_km2"},"ufs":{"gid":"ufs_gid","cd_uf":"ufs_cd_uf","nm_uf":"ufs_nm_uf","sigla":"ufs_sigla","nm_regiao":"ufs_nm_regiao"}}
```

Before being able to use the _get-layers_ method we need to create a file with some coordinates:
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
curl -X 'POST' 'http://localhost:8080/get-layers' -F 'layers_def={"ufs":"*"}' -F 'file=@test.csv;type=text/csv'
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
curl -X 'POST' 'http://localhost:8080/get-layers' \
-F 'layers_def={"municipios":{"cd_mun":"cod_ibge","nm_mun":"nom_mun","sigla":"sig_uf"},"ufs":{"nm_uf":"nom_uf","nm_regiao":"nom_regiao"}}' \
-F 'file=@test.csv;type=text/csv'
```
Output:
```
id,cod_ibge,nom_mun,sig_uf,nom_uf,nom_regiao
78,3118809,Coração de Jesus,MG,Minas Gerais,Sudeste
79,2908903,Coração de Maria,BA,Bahia,Nordeste
80,4106308,Corbélia,PR,Paraná,Sul
81,3301504,Cordeiro,RJ,Rio de Janeiro,Sudeste
```