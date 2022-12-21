import psycopg2, os, json, io
from fastapi import HTTPException

def db_connect():
    try:
        db_host = os.environ.get('GEODB_HOST')
        db_name = os.environ.get('GEODB_DB')
        db_user = os.environ.get('GEODB_USER')
        db_pwd  = os.environ.get('GEODB_PASSWORD')
        conn    = psycopg2.connect(" host=" + db_host + " dbname=" + db_name + \
                                   " user=" + db_user + " password=" + db_pwd)
        cur = conn.cursor()
        return cur
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=400, detail=f"{e}")

def create_coordinate_table(cur, file, no_header):
    cur.execute("""
    create temp table coordenates_csv (
        id text not null,
        lat float not null,
        lon float not null)
    """)
    sql_copy = "copy coordenates_csv from stdin with csv delimiter ','"
    if no_header != "1":
        sql_copy = sql_copy + " header"
    cur.copy_expert(sql=sql_copy,file=file)
    file.close()

def search_layers(cur, layers, no_header, include_coordinates):
    srid = os.environ.get('SRID',4326)
    sql = """
    create temp table return_csv as
      select mc.id """ 
    if include_coordinates == '1':
        sql = sql + ", mc.lat as latitude, mc.lon as longitude"
    sql_from = "\n            from coordenates_csv as mc"
    for l in layers:
        sql = sql + "\n                ," + \
                    "\n                ,".join([l+"."+k+" as "+v for k, v in layers[l].items()])
        sql_from = sql_from + "\n            left outer join " + l + \
                   "\n              on st_within(st_point(mc.lon,mc.lat,"+srid+"),"+l+".geom)"
    sql = sql + sql_from
    cur.execute(sql)
    
    sql_copy = "copy return_csv to stdout with csv delimiter ',' quote '\"'"
    if no_header != "1":
        sql_copy = sql_copy + " header"
    f = io.StringIO("")
    cur.copy_expert(sql=sql_copy,file=f)
    cur.close()
    
    f.seek(0)
    contents = f.read()
    f.close()
    return contents

def available_layers(cur, include_columns,select_layer):
    if include_columns == "1":
        sql = """
        select '{'||string_agg('"'||table_name||'":'
               ||(select '{'||string_agg('"'||c.column_name||'":"'
                            ||substring(c.table_name,1,3)||'_'||c.column_name||'"'
                           ,',' order by ordinal_position)||'}'
                    from information_schema.columns c
                   where c.table_name=t.table_name
                 and c.column_name!='geom'),',')||'}' json
          from information_schema.columns t
         where t.column_name='geom'
        """
    else:
        sql = """
        select '{'||string_agg('"'||table_name||'":"*"',',')||'}' json
          from information_schema.columns t
         where t.column_name='geom'
        """
    if type(select_layer) is list:
        sql = sql + "   and t.table_name in (" + \
              ",".join(map(lambda a:"'"+a+"'",select_layer)) + ")"
    cur.execute(sql)
    return cur.fetchone()[0]

def check_layers(cur, layers_def):
    try:
       layers = json.loads(layers_def)
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=400, detail="layers_def: JSON syntax error")

    db_layers_columns = json.loads(available_layers(cur, include_columns="1", select_layer=None))
    for l in layers:
        if type(layers[l]) is dict:
            for c in layers[l].keys():
                try:
                    t = db_layers_columns[l][c]
                except KeyError:
                    raise HTTPException(status_code=400,
                                     detail=f"layers_def: column {c} not found in layer {l}")
        elif type(layers[l]) is str and layers[l] == "*":
            try:
                layers[l] = dict(db_layers_columns[l])
            except KeyError:
                raise HTTPException(status_code=400,
                                 detail=f"layers_def: layer {l} not found in database")
        else:
            raise HTTPException(status_code=400,
                                detail=f"layers_def: layer {l} incorrectly formatted")
    return layers
