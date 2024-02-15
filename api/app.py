from flask import Flask, render_template
import os
import psycopg2

app = Flask(__name__)

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

connection_string = (
    f"dbname={DB_NAME} user={DB_USER} "
    f"password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
)


@app.route('/')
def index():
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute("""SELECT DISTINCT show_title
        FROM "netflix" AS s1
        WHERE country_iso2 = 'JP'
        AND NOT EXISTS (
        SELECT 1
        FROM "netflix" AS s2
        WHERE s2.show_title = s1.show_title
        AND s2.country_iso2 != 'JP'
    );
    """)
    shows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", shows=shows)


if __name__ == "__main__":
    app.run(debug=True)
