from os import getenv
from bson import ObjectId

from flask import Flask, request, render_template, redirect, url_for

from databases.databases_model import Databases
from query_model import QueryModel

app = Flask(__name__)


def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    if isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    return obj


@app.route('/')
def index():
    client = get_default_connection()
    items = client.get_data()
    return render_template('index.html', items=items)


@app.route('/crud/mysql')
def crud_mysql():
    conn = get_connection_by_type('mysql')
    items = conn.get_data()
    return render_template('index.html', items=items, database_type='mysql')


@app.route('/crud/redis')
def crud_redis():
    conn = get_connection_by_type('redis')
    items = conn.get_data()
    return render_template('index.html', items=items, database_type='redis')


@app.route('/crud/mongodb')
def crud_mongodb():
    conn = get_connection_by_type('mongodb')
    items = [x for x in conn.get_all()]
    # set _id to id for compatibility with the template
    for item in items:
        item['id'] = str(item['_id'])
        del item['_id']
    print(items)
    return render_template('index.html', items=items, database_type='mongodb')


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


@app.route('/crud/<database_type>/delete/<target_id>', methods=['POST'])
def delete_item_by_type(database_type, target_id):
    conn = get_connection_by_type(database_type)
    conn.delete_data_by_id(target_id)
    return redirect(f"/crud/{database_type}")


@app.route('/crud/<database_type>/add', methods=['POST'])
def add_item_by_type(database_type):
    item_id = request.form.get('id')
    external_id = request.form.get('external_id')
    conn = get_connection_by_type(database_type)
    conn.insert_data({"id": item_id, "external_id": external_id})
    return redirect(f"/crud/{database_type}")


@app.route('/crud/<database_type>/update/<target_id>', methods=['GET', 'POST'])
def update_item_by_type(database_type, target_id):
    conn = get_connection_by_type(database_type)
    item = conn.get_data_by_id(target_id)
    if request.method == 'POST':
        conn.update_data_by_id(target_id, {'name': request.form.get('name')})
        return redirect(f"/crud/{database_type}")
    return render_template('update.html', item=item, database_type=database_type)


@app.route('/query', methods=['GET', 'POST'])
def query_data():
    if request.method == 'POST':
        import json
        request_dict = json.loads(request.form.get("query"))
        if request_dict is not None:
            try:
                parsed_query = QueryModel(query_request=request_dict)
                parsed_query.execute_query()
                result = convert_objectid(parsed_query.result)
                return render_template('query.html', result=json.dumps(result, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                return f"Invalid JSON query: {e}", 400
    return render_template('query.html')

@app.route('/api/query', methods=['GET', 'POST'])
def api_query_data():
    if request.method == 'POST':
        import json
        request_dict = request.get_json()
        if request_dict is not None:
            try:
                parsed_query = QueryModel(query_request=request_dict)
                parsed_query.execute_query()
                result = convert_objectid(parsed_query.result)
                return json.dumps({"result": result})
            except json.JSONDecodeError as e:
                return json.dumps({"error": f"Invalid JSON query: {e}"}), 400
    return {"error": "Invalid request method"}, 400


if __name__ == '__main__':
    app.run(host='0.0.0.0')
