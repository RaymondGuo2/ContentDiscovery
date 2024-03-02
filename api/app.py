from flask import Flask, jsonify, request
import os
import psycopg2
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

CORS(app)

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

connection_string = (
    f"dbname={DB_NAME} user={DB_USER} "
    f"password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
)


@app.route('/shows')
def get_shows():
    country_iso2 = request.args.get('country', default='GB', type=str)

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    cur.execute("""SELECT DISTINCT show_title
        FROM "netflix" AS s1
        WHERE country_iso2 = %s
        AND NOT EXISTS (
            SELECT 1
            FROM "netflix" AS s2
            WHERE s2.show_title = s1.show_title
            AND s2.country_iso2 != %s
        );
    """, (country_iso2, country_iso2))

    shows = cur.fetchall()

    cur.close()
    conn.close()

    show_titles = [show[0] for show in shows]
    return jsonify(show_titles)


if __name__ == "__main__":
    app.run(debug=True)
