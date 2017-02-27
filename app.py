# import the Flask class from the flask module
import os
import numpy as np
import pandas as pd
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, jsonify
from pprint import pprint
import json

# # Establish connection with our SQLite database.
# conn = sqlite3.connect('test.db')
# c = conn.cursor()

# Create global-level containers for final output.
skus = []
doorlists = []

# Create the application object.
app = Flask(__name__)

# Define routes/callback functions.
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('temp_all.html')

@app.route('/receive_sku')
def process_sku():
    sku = request.args.get('sku_val', 'NO_SKU', type=str)
    skus.append(sku)
    return jsonify(res = sku)

@app.route('/receive_sql')
def process_sql():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    sql = request.args.get('sql_val', 'NO_SQL', type=str)
    query = 'SELECT StoreID FROM Store WHERE {}'.format(sql)
    c.execute(query)
    qr = c.fetchall()
    qr = [v[0] for v in qr]
    doorlists.append(qr)
    print(doorlists)
    return jsonify(res = qr)

@app.route('/show_results')
def disp_res():
    dfs = [
    pd.DataFrame(data=dl, columns=[sku]) for dl, sku in zip(doorlists, skus)
    ]
    mdf = pd.concat(dfs, axis=1, ignore_index=True)
    mdf.columns = skus
    print(mdf.columns.values)
    html_lit = pd.DataFrame.to_html(
        mdf, index=False, na_rep='').replace(
        'class="dataframe"', 'class="table"'
        )
    return render_template('pretty_tables.html', tbl_code=html_lit)
    # d = {k: v for k, v in zip(skus, doorlists)}
    # #jd = json.dumps(d)
    # return(json.dumps(d))

################### DB STUFF ########################

def db_initialize(path='', name='test.db'):

    with open('static/misc/db_col_names.txt', 'r') as f:
        db_col_names = f.read()

    df = pd.read_excel('static/misc/store_attributes.xlsx')
    col_names = df.columns.values
    col_names = [col_name for col_name in col_names
    if 'Unnamed' not in col_name]
    df = df[col_names].drop('SosLogin', axis=1)

    conn = sqlite3.connect(path + name)
    c = conn.cursor()

    # try:
    #     c.execute('CREATE TABLE Store {}'.format(db_col_names))
    #     conn.commit()
    # except sqlite3.OperationalError:
    #     print('Warning: table \'Store\' already exists.')    

    df.to_sql('Store', con=conn, index=False, if_exists='fail')

#####################################################


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
