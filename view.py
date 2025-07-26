from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import mysql
import requests

main = Blueprint('main', __name__)

DOG_API_URL = "https://dog.ceo/api/breeds/image/random/10"

# Home route
@main.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dogs")
    dogs = cur.fetchall()
    cur.close()
    return render_template('index.html', dogs=dogs)

# Fetch new dogs
@main.route('/fetch')
def fetch_new_dogs():
    response = requests.get(DOG_API_URL)
    data = response.json()

    if data['status'] == 'success':
        cur = mysql.connection.cursor()
        for url in data['message']:
            parts = url.split("/")
            breed = parts[4] if len(parts) > 4 else "Unknown"
            cur.execute("INSERT INTO dogs (image_url, breed, likes, views) VALUES (%s, %s, 0, 0)", (url, breed))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('main.index'))

# Like
@main.route('/like/<int:id>')
def like_dog(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE dogs SET likes = likes + 1 WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('main.index'))

# View
@main.route('/view/<int:id>')
def view_dog(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE dogs SET views = views + 1 WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('main.index'))

# Breed Detail
@main.route('/breed/<breed>')
def breed_detail(breed):
    response = requests.get(f'https://dog.ceo/api/breed/{breed}/images')
    data = response.json()
    images = data['message'][:10]  # first 10 images
    return render_template('breed_detail.html', breed=breed, images=images)

# Recently viewed breed - POST
@main.route('/viewed', methods=['POST'])
def add_viewed_breed():
    data = request.get_json()
    breed = data.get('breed')
    if not breed:
        return jsonify({'error': 'Missing breed'}), 400

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO viewed (breed) VALUES (%s)", (breed,))
    mysql.connection.commit()

    cur.execute("""
        DELETE FROM viewed 
        WHERE id NOT IN (
            SELECT id FROM (
                SELECT id FROM viewed ORDER BY viewed_at DESC LIMIT 5
            ) AS recent
        )
    """)
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Viewed breed saved'}), 201

# Recently viewed breed - GET
@main.route('/viewed', methods=['GET'])
def get_recent_breeds():
    cur = mysql.connection.cursor()
    cur.execute("SELECT breed FROM viewed ORDER BY viewed_at DESC LIMIT 5")
    rows = cur.fetchall()
    cur.close()
    breeds = [row[0] for row in rows]
    return jsonify(breeds)
