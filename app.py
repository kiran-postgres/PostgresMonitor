import logging
import sys
from logging.handlers import RotatingFileHandler
import os

import psycopg2
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin

from config.queries import qry
from utils.utils import format_data

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config.from_object('settings')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

# Setup logging
logfile_location = 'logs/web-application-log.log'
log_level = logging.DEBUG
log_format = '%(asctime)s %(levelname)s: %(message)s [in %(filename)s:%(lineno)d]'

logger = logging.getLogger()
handler = RotatingFileHandler(logfile_location, maxBytes=100000, backupCount=10)
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(log_level)

# Holds queries
query = dict()


class DBConnection:
    db_connection = None

    # noinspection PyBroadException
    @staticmethod
    def get_db_connection():
        username = app.config['USERNAME']
        password = app.config['PASSWORD']
        endpoint = app.config['ENDPOINT']
        db = app.config['DB']
        port = app.config['PORT']

        if DBConnection.db_connection is not None:
            return DBConnection.db_connection

        try:
            print('DB Connection', DBConnection.db_connection)
            DBConnection.db_connection = psycopg2.connect(host=endpoint, user=username, password=password,
                                             dbname=db, port=port)
            print('DB Connection acquired!')
        except Exception as err:
            app.logger.error('Unable to get a DB connection to {}'.format(endpoint))
            sys.exit(1)

        return DBConnection.db_connection


# noinspection PyBroadException
def execute_query(query, parameters):
    connection = DBConnection.get_db_connection()
    print(connection)
    app.logger.debug('Query to be executed:')
    app.logger.debug(query)

    records = []
    try:
        cur = connection.cursor()
        cur.execute(query, parameters)

        # Get Column names
        field_names = [i[0].upper() for i in cur.description]
        records.append(field_names)

        # Process all the records
        for record in cur:
            rec = []

            # SQL Query result can contain different types of data - Int, Char, Decimal, CLOB, etc.
            # Converting all types to Char so that, when preparing JSON format, there won't be any
            # errors.
            for i in range(len(record)):
                string_value = ''
                try:
                    string_value = str(record[i]) if record[i] is not None else ''
                except Exception as error:
                    print('Unable to convert value to String; value: {}'.format(record[i]))

                rec.append(string_value)
            records.append(rec)
        cur.close()
    except Exception as err:
        # A SQL Query could fail due to any number of reasons. Syntax could be wrong, Database could be down,
        # the User may not have required privileges to execute the query, No Temporary table space, no CPU
        # availability, to name a few. In such cases, Return the Exception.
        print(err)
        print(str(err))
        records.append("Exception: " + str(err))

    print('Result:', records)
    return records


@app.route('/')
def home():
    """
    Index page
    """
    pie_chart = os.path.join(app.config['UPLOAD_FOLDER'], 'postgresql_elephant.svg')
    return render_template('index.html', pie_chart=pie_chart)


@app.route('/get_query_map')
@cross_origin()
def get_query_map():
    config_data = dict()

    for key in qry.keys():
        formatted_key = key.replace(' ', '-').lower().strip()

        config_data[formatted_key] = {
            'heading': qry[key]['heading'],
            'caption': qry[key]['caption'],
            'table-width': qry[key]['table-width'],
            'graph-width': qry[key]['graph-width'],
            'graph-required': qry[key]['graph-required'],
            'graph-type': qry[key]['graph-type']
        }

    return jsonify(config_data)


@app.route('/get-table/<string:table>', methods=['GET'])
def get_table(table):
    records = execute_query('SELECT * FROM ' + table + ' WHERE ROWNUM < 1000', [])
    result = format_data(records)
    return result


@app.route('/get-list-of-data-dictionary-tables', methods=['GET'])
def get_list_of_data_dictionary_tables():
    query = qry['data-dictionary-views']
    records = execute_query(query, [])
    result = format_data(records)
    return result


@app.route('/query_execution/<string:query_id>', methods=['GET'])
def query_execution(query_id):
    parameter_names = list(request.args)
    paramerter_values = list()
    [paramerter_values.append(request.args[parm]) for parm in parameter_names]

    app.logger.debug('Query parameters for {}'.format(query_id))
    app.logger.debug(parameter_names)
    app.logger.debug(paramerter_values)

    # Holds Query results
    records = list()
    parameters = []

    if len(paramerter_values) == 0:
        parameters = None
    else:
        parameters = paramerter_values

    if query_id in qry.keys():
        query = qry[query_id]['query']
        records = execute_query(query, parameters)
    else:
        records.append('Exception: ' + query_id + ' not found in list of configured queries')

    # Format Query results in JSON form.
    result = format_data(records)
    return result


@app.route('/report_sql_monitor/<string:sql_id>', methods=['GET'])
def report_sql_monitor(sql_id):
    query = 'SELECT DBMS_SQLTUNE.REPORT_SQL_MONITOR(' + "'" + sql_id + "')" + ' FROM DUAL'

    records = execute_query(query, '')

    # Data of this query is a LOB Object. Convert it to a String first.
    result = convert_lob_object_to_string(records[1][0])

    records = [['STATUS'], [result]]
    result = format_data(records)
    return result


@app.route('/report_sql_monitor_active/<string:sql_id>', methods=['GET'])
def report_sql_monitor_active(sql_id):
    query = 'SELECT DBMS_SQLTUNE.REPORT_SQL_MONITOR(' + "'" + sql_id + "'," \
            + "type => 'active', report_level => 'ALL') FROM DUAL"

    records = execute_query(query, '')

    # Data of this query is a LOB Object. Convert it to a String first.
    result = convert_lob_object_to_string(records[1][0])
    return result


@app.route('/execute_custom_sql', methods=['POST', 'OPTIONS'])
@cross_origin()
def execute_custom_sql():
    payload = request.json
    sql_text = payload['query']

    records = execute_query(sql_text, None)
    result = format_data(records)
    return result, 201


def convert_lob_object_to_string(lob_object):
    # Create a temp file
    filename = 'temp.txt'

    # Write the contents of the LOB Object to a file
    temp = open(filename, 'w')
    print(lob_object, file=temp)
    temp.close()

    # Read the temp file
    temp = open(filename, 'r')
    result = ""

    # Read all the lines
    for line in temp:
        result += line

    temp.close()

    return result


if __name__ == '__main__':
    app.run()
