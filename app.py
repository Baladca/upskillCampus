from flask import Flask, render_template, request, redirect
import random
import string
import mysql.connector
app = Flask(__name__)
def get_db_connection():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="url_shortener"
    )
    return db
def generate_shortened_url(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['original_url']
    shortened_url = generate_shortened_url()
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO urls (original_url, shortened_url, clicks) VALUES (%s, %s, %s)", 
                (original_url, shortened_url, 0))
    db.commit()
    cursor.close()
    db.close()
    return f"Shortened URL is: <a href='/{shortened_url}'>/{shortened_url}</a>"
@app.route('/<shortened_url>')
def redirect_to_url(shortened_url):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT original_url, clicks FROM urls WHERE shortened_url = %s", (shortened_url,))
    result = cursor.fetchone()
    if result:
        new_click_count = result[1] + 1
        cursor.execute("UPDATE urls SET clicks = %s WHERE shortened_url = %s", (new_click_count, shortened_url))
        db.commit()
        cursor.close()
        db.close()
        return redirect(result[0])
    else:
        cursor.close()
        db.close()
        return "URL not found!", 404
@app.route('/analytics/<shortened_url>')
def view_analytics(shortened_url):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT original_url, clicks FROM urls WHERE shortened_url = %s", (shortened_url,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:
        original_url = result[0]
        clicks = result[1]
        return render_template('analytics.html', shortened_url=shortened_url, original_url=original_url, clicks=clicks)
    else:
        return "URL not found!", 404
if __name__ == '__main__':
    app.run(debug=True)
