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

def extract_columns(items) -> list[str]:
    columns = []
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                for k in item.keys():
                    if k not in columns:
                        columns.append(k)
    return columns


def itens_for_template(conn, database_type):
    items = conn.get_data()
    if hasattr(items, '__iter__') and not isinstance(items, (dict, str)):
        items = list(items)
    else:
        items = [items] if items is not None else []
    items = convert_objectid(items)
    if database_type == 'redis':
        for item in items:
            if isinstance(item, dict) and 'external_id' not in item and 'value' in item:
                item['external_id'] = str(item['value'])
    return items

def get_default_connection(database: str = None, database_name: str = None, database_params: str = None):
    db = Databases()
    db.database_type = database or getenv('DB')
    db.database = database_name or getenv('DB_NAME')
    raw_params = database_params or getenv('DB_PARAMS', '')
    params = {param.split('=')[0]: param.split('=')[1] for param in raw_params.split(',') if '=' in param}
    db.params = params
    return db.get_connection()


AVAILABLE_SCHEMAS = {
    'mysql': {
        'cms': {
            'label': 'CMS - Gestão de Clientes',
            'tables': ['clientes', 'enderecos', 'meios_pagamento']
        },
        'sms': {
            'label': 'SMS - Gestão de Estoque',
            'tables': ['produtos', 'galpoes', 'setores']
        },
        'fnms': {
            'label': 'FNMS - Gestão Financeira',
            'tables': ['notas_fiscais', 'linhas_nota', 'cobrancas', 'pagamentos']
        },
        'test_db': {
            'label': 'Test DB (Legado)',
            'tables': ['table_test']
        }
    },
    'mongodb': {
        'oms': {
            'label': 'OMS - Gestão de Pedidos',
            'tables': ['pedidos']
        },
        'fms': {
            'label': 'FMS - Gestão de Frotas',
            'tables': ['rotas', 'veiculos']
        },
        'test_db': {
            'label': 'Test DB (Legado)',
            'tables': ['test']
        }
    },
    'redis': {
        '0': {
            'label': 'FMS GPS / Cache (DB 0)',
            'tables': ['gps_positions']
        }
    }
}


def get_connection_by_type(database_type, database=None, table=None):
    db = Databases()
    db.database_type = database_type
    
    if database_type == 'mongodb':
        db_name = database or 'oms'
        table_name = table or 'pedidos'
        db.database = db_name
        db.params = {'host': getenv('MONGO_HOST', 'localhost'), 'port': 27017, 'target': table_name}
    elif database_type == 'mysql':
        db_name = database or 'cms'
        table_name = table or 'clientes'
        db.database = db_name
        db.params = {
            'host': getenv('MYSQL_HOST', 'localhost'),
            'port': 3306,
            'user': 'root',
            'password': 'rootpassword',
            'target': table_name
        }
    elif database_type == 'redis':
        db_name = database or '0'
        table_name = table or 'gps_positions'
        db.database = db_name
        db.params = {'host': getenv('REDIS_HOST', 'localhost'), 'port': 6379}
    else:
        raise ValueError(f"Database type '{database_type}' not supported")

    conn = db.get_connection()
    setattr(conn, 'current_db', db_name)
    setattr(conn, 'current_table', table_name)
    return conn

def prossess_query_request(request_dict) -> dict[Any, Any] | list[Any] | str | Any:
    parsed_query = QueryModel(query_request=request_dict)
    parsed_query.execute_query()
    result = convert_objectid(parsed_query.result)
    return result