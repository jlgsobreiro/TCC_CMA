from os import getenv

from flask import Flask, request, render_template, redirect, url_for

from databases.databases_model import Databases

app = Flask(__name__)


@app.route('/')
def index():
    client = get_default_connection()
    items = client.get_all()
    return render_template('index.html', items=items)


def get_default_connection():
    db = Databases()
    db.database_type = getenv('DB')
    db.database = getenv('DB_NAME')
    params = getenv('DB_PARAMS').split(',')
    params = {param.split('=')[0]: param.split('=')[1] for param in params}
    db.params = params
    return db.get_connection()

#TODO: Receber json com os dados a serem inseridos
@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('name')
    conn = get_default_connection()
    conn.insert_data({'id': name})
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['POST'])
def update_item(target_id):
    conn = get_default_connection()
    item = conn.get_data({'id': target_id})
    if request.method == 'POST':
        item = conn.update_data({'id': target_id}, {'name': request.form.get('name')})
        return redirect(url_for('index'))
    return render_template('update.html', item=item)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(target_id):
    conn = get_default_connection()
    conn.delete_data({'id': target_id})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
