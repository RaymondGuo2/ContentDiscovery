from flask import Flask, jsonify, request
import os
import psycopg2
from dotenv import load_dotenv
from flask_cors import CORS
import pycountry

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


def country_valid(code):
    try:
        country = pycountry.countries.lookup(code.upper())
        return country is not None
    except LookupError:
        return False


@app.route('/shows')
def get_shows():
    country_iso2 = request.args.get('country', default='GB', type=str)

    if not country_valid(country_iso2):
        return jsonify({"error": "Invalid country code."}), 400

    try:
        conn = psycopg2.connect(connection_string)
    except psycopg2.OperationalError as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return jsonify(
            {"error": "Internal server error, could not connect to database."}
        ), 500

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
    if not show_titles:
        return jsonify(
            {"message": "There are no unique shows for this country."}), 200
    return jsonify(show_titles)


@app.route('/search')
def search():
    search_query = request.args.get('query', '')

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    sql_query = """SELECT DISTINCT show_title FROM "netflix" WHERE
        country_name ILIKE %s OR
        country_iso2 ILIKE %s OR
        show_title ILIKE %s;"""
    like_pattern = f'%{search_query}%'
    cur.execute(sql_query, (like_pattern, like_pattern, like_pattern))

    results = cur.fetchall()
    cur.close()
    conn.close()

    show_titles = [result[0] for result in results]

    return jsonify(show_titles)


if __name__ == "__main__":
    app.run(debug=True)
