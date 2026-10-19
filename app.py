from os import getenv
import json
from flask import Flask, request, render_template, redirect, url_for

from utils import (
    itens_for_template,
    get_connection_by_type,
    get_default_connection,
    prossess_query_request,
    extract_columns,
    convert_objectid,
    AVAILABLE_SCHEMAS
)

app = Flask(__name__)

@app.route('/')
def index():
    db_type = request.args.get('type') or getenv('DB', 'mysql')
    db_name = request.args.get('db', 'cms' if db_type == 'mysql' else ('oms' if db_type == 'mongodb' else '0'))
    table_name = request.args.get('table', 'clientes' if db_type == 'mysql' else ('pedidos' if db_type == 'mongodb' else 'gps_positions'))
    return redirect(url_for('crud_database', database_type=db_type, db=db_name, table=table_name))


@app.route('/crud/<database_type>')
def crud_database(database_type):
    db_name = request.args.get('db')
    table_name = request.args.get('table')
    conn = get_connection_by_type(database_type, database=db_name, table=table_name)
    items = itens_for_template(conn, database_type)
    columns = extract_columns(items)
    current_db = getattr(conn, 'current_db', db_name)
    current_table = getattr(conn, 'current_table', table_name)
    return render_template(
        'index.html',
        items=items,
        columns=columns,
        database_type=database_type,
        current_db=current_db,
        current_table=current_table,
        available_schemas=AVAILABLE_SCHEMAS.get(database_type, {}),
        all_schemas=AVAILABLE_SCHEMAS
    )


@app.route('/crud/<database_type>/<target_id>', methods=['DELETE'])
def delete_item_by_type(database_type, target_id):
    db_name = request.args.get('db')
    table_name = request.args.get('table')
    conn = get_connection_by_type(database_type, database=db_name, table=table_name)
    conn.delete_data_by_id(target_id)
    return ('', 204)


@app.route('/crud/<database_type>', methods=['POST'])
def add_item_by_type(database_type):
    db_name = request.form.get('_db') or request.args.get('db')
    table_name = request.form.get('_table') or request.args.get('table')
    conn = get_connection_by_type(database_type, database=db_name, table=table_name)
    data = {}
    for k, v in request.form.items():
        if k.startswith('_') or v == '':
            continue
        val = v.strip()
        if database_type == 'mongodb' and (val.startswith('{') or val.startswith('[')):
            try:
                val = json.loads(val)
            except Exception:
                pass
        data[k] = val

    if data:
        conn.insert_data(data)

    current_db = getattr(conn, 'current_db', db_name)
    current_table = getattr(conn, 'current_table', table_name)
    redirect_url = f"/crud/{database_type}"
    params = []
    if current_db:
        params.append(f"db={current_db}")
    if current_table:
        params.append(f"table={current_table}")
    if params:
        redirect_url += "?" + "&".join(params)
    return redirect(redirect_url)


@app.route('/crud/<database_type>/<target_id>', methods=['POST', 'GET'])
def update_item_by_type(database_type, target_id):
    db_name = request.args.get('db') or request.form.get('_db')
    table_name = request.args.get('table') or request.form.get('_table')
    conn = get_connection_by_type(database_type, database=db_name, table=table_name)
    if request.method == 'POST':
        update_data = {}
        for k, v in request.form.items():
            if k.startswith('_') or k in ('id', '_id'):
                continue
            val = v.strip()
            if database_type == 'mongodb' and (val.startswith('{') or val.startswith('[')):
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            update_data[k] = val

        if update_data:
            conn.update_data_by_id(target_id, update_data)

        redirect_url = f"/crud/{database_type}"
        params = []
        if db_name:
            params.append(f"db={db_name}")
        if table_name:
            params.append(f"table={table_name}")
        if params:
            redirect_url += "?" + "&".join(params)
        return redirect(redirect_url)

    item = conn.get_data_by_id(target_id)
    if isinstance(item, dict):
        item = convert_objectid(item)
    return render_template(
        'update.html',
        item=item,
        database_type=database_type,
        target_id=target_id,
        current_db=db_name,
        current_table=table_name
    )


@app.route('/query', methods=['GET', 'POST'])
def query_data():
    if request.method == 'POST':
        raw_query = request.form.get("query", "").strip()
        try:
            request_dict = json.loads(raw_query)
            result = prossess_query_request(request_dict)
            return render_template(
                'query.html',
                result=json.dumps(result, indent=2, ensure_ascii=False),
                raw_query=raw_query,
                record_count=len(result) if isinstance(result, list) else (1 if result else 0)
            )
        except Exception as e:
            return render_template('query.html', error=str(e), raw_query=raw_query), 400
    return render_template('query.html')

@app.route('/api/query', methods=['GET', 'POST'])
def api_query_data():
    if request.method == 'POST':
        import json
        request_dict = request.get_json()
        if request_dict is not None:
            try:
                result = prossess_query_request(request_dict)
                return json.dumps({"result": result})
            except json.JSONDecodeError as e:
                return json.dumps({"error": f"Invalid JSON query: {e}"}), 400
    return {"error": "Invalid request method"}, 400


if __name__ == '__main__':
    app.run(host='0.0.0.0')
