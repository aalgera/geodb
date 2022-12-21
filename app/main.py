from fastapi import FastAPI, File, UploadFile, Response, Form, Query, HTTPException
from lib.functions import db_connect, available_layers, check_layers, create_coordinate_table, search_layers

app = FastAPI()

@app.get("/list-layers")
async def list_layers(select_layer: list[str] | None = Query(default=None) 
                     ,include_columns: str = Query(default="0",regex="^[01]$")):
    cur = db_connect()
    return Response(content=available_layers(cur, include_columns, select_layer), 
                    media_type="application/json")

@app.post("/get-layers")
async def get_layers(layers_def: str = Form()
                    ,file: UploadFile = File(...)
                    ,no_input_csv_header: str = Form(default="0",regex="^[01]$")
                    ,no_output_csv_header: str = Form(default="0",regex="^[01]$")
                    ,include_coordinates: str = Form(default="0",regex="^[01]$")):
    cur = db_connect()
    layers = check_layers(cur, layers_def)
    create_coordinate_table(cur, file.file, no_input_csv_header)
    csv_return = search_layers(cur, layers, no_output_csv_header, include_coordinates)
    return Response(content=csv_return, media_type="text/csv")
