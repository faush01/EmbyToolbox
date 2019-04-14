from flask import Flask, jsonify, render_template, request
import sqlite3
from emby_client import load_emby_data

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

app = Flask(__name__)


@app.route('/load_data', methods=['GET', 'POST'])
def load_data():
    content = request.json
    server_host = content.get("server_host")
    server_user = content.get("server_user")
    server_password = content.get("server_password")

    config = {}
    config["emby_server"] = "http://%s:8096" % server_host
    config["user_name"] = server_user
    config["user_password"] = server_password

    count = load_emby_data(cursor, config)
    conn.commit()

    return_data = {}
    return_data["message"] = "Data Loaded : %s" % count

    return jsonify(return_data)

@app.route('/report', methods=['GET', 'POST'])
def get_report_data():
    content = request.json
    query = content.get("query")

    return_data = {}
    return_data["error"] = ""

    try:
        result = cursor.execute(query)

        col_names = list(map(lambda x: x[0], result.description))

        return_data["headers"] = col_names
        return_data["items"] = []

        for row in result:
            line_data = []
            for item in row:
                if type(item) == int:
                    item = str(item)
                line_data.append(item)

            return_data["items"].append(line_data)
    except Exception as err:
        return_data["error"] = str(err)

    return jsonify(return_data)


@app.route('/')
def home():
    return render_template("home.html")


if __name__ == '__main__':
    app.run()
