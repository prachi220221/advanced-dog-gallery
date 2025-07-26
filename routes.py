from flask import Blueprint, render_template, request, redirect, url_for
import requests
from app import mysql

main = Blueprint('main', __name__)

@main.route('/')
def index():
    filter_option = request.args.get('filter', 'all')
    sort_option = request.args.get('sort', 'az')

    cur = mysql.connection.cursor()

    query = """
        SELECT d.id, d.image_url, d.breed,
               COALESCE(l.like_count, 0) AS likes,
               COALESCE(v.view_count, 0) AS views
        FROM dogs d
        LEFT JOIN (
            SELECT breed, COUNT(*) AS like_count
            FROM likes
            GROUP BY breed
        ) l ON d.breed = l.breed
        LEFT JOIN (
            SELECT breed, COUNT(*) AS view_count
            FROM viewed
            GROUP BY breed
        ) v ON d.breed = v.breed
    """

    if sort_option == "az":
        query += " ORDER BY d.breed ASC"
    elif sort_option == "za":
        query += " ORDER BY d.breed DESC"
    elif sort_option == "most_liked":
        query += " ORDER BY likes DESC"
    elif sort_option == "most_viewed":
        query += " ORDER BY views DESC"

    cur.execute(query)
    dogs = cur.fetchall()
    cur.close()

    return render_template("index.html", dogs=dogs)

@main.route('/fetch')
def fetch_new_dogs():
    response = requests.get("https://dog.ceo/api/breeds/image/random/10")
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

@main.route('/like/<int:id>')
def like_dog(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE dogs SET likes = likes + 1 WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('main.index'))

@main.route('/view/<int:id>')
def view_dog(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE dogs SET views = views + 1 WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('main.index'))

@main.route('/breed/<breed>')
def breed_detail(breed):
    api_breed = breed.replace("-", "/")

    try:
        response = requests.get(f'https://dog.ceo/api/breed/{api_breed}/images', timeout=5)
        response.raise_for_status()
        data = response.json()

        if data['status'] != 'success' or not data['message']:
            return render_template("error.html", message="No images found for this breed.")

        images = data['message'][:10]

        # Log viewed breed
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO viewed (breed) VALUES (%s)", (breed,))
        mysql.connection.commit()
        cur.close()

        return render_template("breed_detail.html", breed=breed.replace("-", " ").title(), images=images)

    except (requests.exceptions.RequestException, ValueError):
        return render_template("error.html", message="Failed to load images. Try again.")

@main.route('/viewed', methods=['POST'])
def add_viewed():
        data = request.get_json()
        breed = data.get('breed')

        if not breed:
            return jsonify({'error': 'Breed is required'}), 400

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO viewed (breed) VALUES (%s)", (breed,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Viewed breed added'}), 201

@main.route('/viewed', methods=['GET'])
def get_recently_viewed():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT breed FROM viewed
        ORDER BY viewed_at DESC
        LIMIT 5
    """)
    breeds = [row[0] for row in cur.fetchall()]
    cur.close()
    return jsonify(breeds)

@main.route('/')
def index():
    cur = mysql.connection.cursor()

    # Main dog data
    cur.execute("""
        SELECT d.id, d.image_url, d.breed,
               COALESCE(l.like_count, 0) AS likes,
               COALESCE(v.view_count, 0) AS views
        FROM dogs d
        LEFT JOIN (
            SELECT breed, COUNT(*) AS like_count
            FROM likes GROUP BY breed
        ) l ON d.breed = l.breed
        LEFT JOIN (
            SELECT breed, COUNT(*) AS view_count
            FROM viewed GROUP BY breed
        ) v ON d.breed = v.breed
    """)
    dogs = cur.fetchall()

    # Recent views
    cur.execute("SELECT DISTINCT breed FROM viewed ORDER BY viewed_at DESC LIMIT 5")
    recent_breeds = [row[0] for row in cur.fetchall()]

    cur.close()
    return render_template('index.html', dogs=dogs, recent_breeds=recent_breeds)
@main.route("/breed/<breed>")
def breed_detail(breed):
    cur = mysql.connection.cursor()

    # Update view count
    cur.execute("UPDATE dogs SET views = views + 1 WHERE breed = %s", (breed,))
    mysql.connection.commit()

    # Fetch dog info to show on breed detail page
    cur.execute("SELECT * FROM dogs WHERE breed = %s", (breed,))
    dog = cur.fetchone()
    cur.close()

    return render_template("breed_detail.html", dog=dog)

@main.route("/like/<breed>", methods=["POST"])
def like_breed(breed):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE dogs SET likes = likes + 1 WHERE breed = %s", (breed,))
    mysql.connection.commit()
    cur.close()
    return redirect("/")
dogs = [
    {'image_url': 'image1.jpg', 'name': 'Max', 'description': 'A playful young Airedale.'},
    {'image_url': 'image2.jpg', 'name': 'Bella', 'description': 'A curious companion.'}
]


@main.route('/fetch')
def fetch_new_dogs():
    response = requests.get("https://dog.ceo/api/breeds/image/random/5")  # fetch 5 random dogs
    if response.status_code == 200:
        data = response.json()
        images = data['message']  # list of image URLs

        cur = mysql.connection.cursor()
        for image_url in images:
            cur.execute("INSERT INTO dogs (image_url) VALUES (%s)", (image_url,))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('main.index'))  # go back to homepage after adding

@main.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dogs ORDER BY id DESC")
    dogs = cur.fetchall()
    cur.close()
    return render_template("index.html", dogs=dogs)

