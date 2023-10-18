from flask import Flask, request, jsonify, redirect, g
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import hashlib
import datetime

load_dotenv()

app = Flask(__name__)

# Database configuration
DATABASE_POOL = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=os.getenv("DB_USER"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    cursor_factory=RealDictCursor
)

# Get connection from pool before entering route handler
@app.before_request
def get_db():
    if 'db_conn' not in g:
        g.db_conn = DATABASE_POOL.getconn()

# Put connection back in pool after request is finished
@app.teardown_appcontext
def release_db_conn(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        DATABASE_POOL.putconn(db_conn)

def create_short_url(url):
    hash_obj = hashlib.sha256((url + str(datetime.datetime.now())).encode())
    hash_hex = hash_obj.hexdigest()
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    num = int(hash_hex, 16)
    base62_str = ""
    for _ in range(6):
        base62_str = chars[num % 62] + base62_str
        num //= 62
    return base62_str

@app.route("/<short_code>")
def redirect_to_original(short_code):
    try:
        with g.db_conn.cursor() as cursor:
            cursor.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
            data = cursor.fetchone()
            if not data:
                return "Short code not found", 404
            return redirect(data['original_url'])
    except Exception as e:
        return f"Error retrieving from database: {str(e)}", 500

@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    original_url = request.json.get("original_url")
    if not original_url:
        return "Original URL is required", 400
    short_code = create_short_url(original_url)
    try:
        with g.db_conn.cursor() as cursor:
            cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (%s, %s) RETURNING *", 
                           (original_url, short_code))
            data = cursor.fetchone()
        g.db_conn.commit()
        return jsonify(data)
    except Exception as e:
        return f"Error saving to database: {str(e)}", 500

@app.route("/api/<short_code>", methods=["GET"])
def retrieve_original_url(short_code):
    try:
        with g.db_conn.cursor() as cursor:
            cursor.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
            data = cursor.fetchone()
            if not data:
                return "Short code not found", 404
            return jsonify(data)
    except Exception as e:
        return f"Error retrieving from database: {str(e)}", 500

@app.route("/api/<short_code>", methods=["PUT"])
def update_original_url(short_code):
    original_url = request.json.get("original_url")
    if not original_url:
        return "Original URL is required for update", 400
    try:
        with g.db_conn.cursor() as cursor:
            cursor.execute("UPDATE urls SET original_url = %s WHERE short_code = %s RETURNING *", (original_url, short_code))
            data = cursor.fetchone()
        g.db_conn.commit()
        if not data:
            return "Short code not found", 404
        return jsonify(data)
    except Exception as e:
        return f"Error updating in database: {str(e)}", 500

@app.route("/api/<short_code>", methods=["DELETE"])
def delete_short_url(short_code):
    try:
        with g.db_conn.cursor() as cursor:
            cursor.execute("DELETE FROM urls WHERE short_code = %s", (short_code,))
        g.db_conn.commit()
        return "Short URL deleted successfully"
    except Exception as e:
        return f"Error deleting from database: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=3000)