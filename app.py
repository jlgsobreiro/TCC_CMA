from flask import Flask, request, render_template, redirect, url_for

from utils import itens_for_template, get_connection_by_type, get_default_connection, prossess_query_request

app = Flask(__name__)

@app.route('/')
def index():
    client = get_default_connection()
    items = client.get_data()
    return render_template('index.html', items=items)


@app.route('/crud/<database_type>')
def crud_database(database_type):
    conn = get_connection_by_type(database_type)
    itens = itens_for_template(conn, database_type)
    print(itens)
    return render_template('index.html', items=itens, database_type=database_type)


@app.route('/crud/<database_type>/<target_id>', methods=['DELETE'])
def delete_item_by_type(database_type, target_id):
    conn = get_connection_by_type(database_type)
    conn.delete_data_by_id(target_id)
    return redirect(f"/crud/{database_type}")


@app.route('/crud/<database_type>', methods=['POST'])
def add_item_by_type(database_type):
    item_id = request.form.get('id')
    external_id = request.form.get('external_id')
    conn = get_connection_by_type(database_type)
    conn.insert_data({"id": item_id, "external_id": external_id})
    return redirect(f"/crud/{database_type}")


@app.route('/crud/<database_type>/<target_id>', methods=['POST', 'GET'])
def update_item_by_type(database_type, target_id):
    conn = get_connection_by_type(database_type)
    item = conn.get_data_by_id(target_id)
    if request.method == 'POST':
        conn.update_data_by_id(target_id, {'external_id': request.form.get('external_id')})
        return redirect(f"/crud/{database_type}")
    return render_template('update.html', item=item, database_type=database_type)


@app.route('/query', methods=['GET', 'POST'])
def query_data():
    if request.method == 'POST':
        import json
        request_dict = json.loads(request.form.get("query"))
        if request_dict is not None:
            try:
                result = prossess_query_request(request_dict)
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
                result = prossess_query_request(request_dict)
                return json.dumps({"result": result})
            except json.JSONDecodeError as e:
                return json.dumps({"error": f"Invalid JSON query: {e}"}), 400
    return {"error": "Invalid request method"}, 400


if __name__ == '__main__':
    app.run(host='0.0.0.0')
