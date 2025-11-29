from os import getenv
from typing import Any

from bson import ObjectId

from databases.databases_model import Databases
from query_model import QueryModel


def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    if isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    return obj

def itens_for_template(conn, database_type):
    items = conn.get_data()
    if database_type == 'redis':
        for item in items:
            item['external_id'] = str(item['value'])
    return items

def get_default_connection(database: str = None, database_name: str = None, database_params: str = None):
    db = Databases()
    db.database_type = database or getenv('DB')
    db.database = database_name or getenv('DB_NAME')
    params = database_params.split(',') or getenv('DB_PARAMS').split(',')
    params = {param.split('=')[0]: param.split('=')[1] for param in params}
    db.params = params
    return db.get_connection()


def get_connection_by_type(database_type):
    db = Databases()
    db.database_type = database_type
    if database_type == 'mongodb':
        db.database = 'test_db'
        db.params = {'host': 'localhost', 'port': 27017, 'target': 'test'}
    elif database_type == 'mysql':
        db.database = 'test_db'
        db.params = {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'rootpassword'}
    elif database_type == 'redis':
        db.database = '0'
        db.params = {'host': 'localhost', 'port': 6379}
    else:
        return "Database type not supported", 400

    return db.get_connection()

def prossess_query_request(request_dict) -> dict[Any, Any] | list[Any] | str | Any:
    parsed_query = QueryModel(query_request=request_dict)
    parsed_query.execute_query()
    result = convert_objectid(parsed_query.result)
    return result