from fastapi import FastAPI, File, APIRouter, UploadFile, Response, Form, Query, HTTPException
from lib.functions import *

tags_metadata = [
    {
        "name": "list",
        "description": """Lists the available layers and its attibutes.
         Returns a json object that can be used as input for _/geodb-api/search_""",
    },
    {
        "name": "search",
        "description": """Searches the configured layers for polygons that match
                          the coordinates in the coordinates file """,
    },
]

app = FastAPI(
    title="Layer search",
    description="""
    While lookups of coordinates in a polygon layer can be done on a one by one basis,
    this tends to be rather slow, certainly if one needs to do thousands of coordinate lookups.
    This api reads a block of multiple coordinates in a csv file and returns atributes of matching
    polygons for each coodinate pair.
    """,
    version="0.1.0",
    contact={
        "name": "Andries Algera",
        "email": "andries.algera@gmail.com",
    },
    openapi_url="/geodb-api/openapi.json",
    docs_url="/geodb-api/docs",
    redoc_url="/geodb-api/redoc",
    openapi_tags=tags_metadata
)
prefix = APIRouter(prefix="/geodb-api")


@prefix.get("/list", tags=["list"])
async def list(select_layer: list[str] | None = Query(default=None) 
                     ,include_columns: str = Query(default="0",regex="^[01]$")):
    cur = db_connect()
    return Response(content=available_layers(cur, include_columns, select_layer), 
                    media_type="application/json")

@prefix.get("/search", tags=["search"])
async def search(layers_def: str = Query()
                ,lat: float = Query()
                ,lon: float = Query()
                ,include_coordinates: str = Query(default="0",regex="^[01]$")):
    cur = db_connect()
    layers = check_layers(cur, layers_def)
    create_coordinate_table_latlon(cur, lat, lon)
    return search_layers(cur, layers, "1", include_coordinates, csv=False)

@prefix.post("/search", tags=["search"])
async def search(layers_def: str = Form()
                ,coordinates_file: UploadFile = File(...)
                ,no_input_csv_header: str = Form(default="0",regex="^[01]$")
                ,no_output_csv_header: str = Form(default="0",regex="^[01]$")
                ,include_coordinates: str = Form(default="0",regex="^[01]$")):
    cur = db_connect()
    layers = check_layers(cur, layers_def)
    create_coordinate_table_csv(cur, coordinates_file.file, no_input_csv_header)
    csv_return = search_layers(cur, layers, no_output_csv_header, include_coordinates, csv=True)
    return Response(content=csv_return, media_type="text/csv")

app.include_router(prefix)
