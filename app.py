from flask import Flask, render_template, request, jsonify
import psycopg2
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def connect_to_db():
    """Connect to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            dbname="spatialproject",
            user="mahi",
            password="mahi",
            host="localhost"
        )
        logging.info("Database connection successful.")
        return connection
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise


@app.route('/')
def index():
    """Display the main page with buttons for each query."""
    return render_template('buttons.html')


@app.route('/query', methods=['POST'])
def query():
    """Handle queries based on user input."""
    query_type = request.form.get('query_type')
    user_input = request.form.get('user_input', '')
    radius = request.form.get('radius', None)
    landmark_type = request.form.get('landmark_type', None)

    conn = connect_to_db()
    cursor = conn.cursor()

    # Queries based on query type
    if query_type == "landmarks_in_city":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s;
        """
        cursor.execute(query, (user_input,))
        result = cursor.fetchall()

    elif query_type == "landmarks_in_radius":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s AND ST_DWithin(c.location, l.location, %s);
        """
        cursor.execute(query, (user_input, float(radius) * 1000))
        result = cursor.fetchall()

    elif query_type == "reviews_for_landmark":
        query = """
            SELECT r.review_text, r.rating, r.review_date
            FROM reviews r
            JOIN landmarks l ON r.landmark_id = l.id
            WHERE l.name = %s;
        """
        cursor.execute(query, (user_input,))
        result = cursor.fetchall()

    elif query_type == "landmarks_of_type":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s AND l.type = %s;
        """
        cursor.execute(query, (user_input, landmark_type))
        result = cursor.fetchall()

    elif query_type == "landmarks_by_rating":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN reviews r ON l.id = r.landmark_id
            WHERE r.rating = %s;
        """
        cursor.execute(query, (user_input,))
        result = cursor.fetchall()

    elif query_type == "landmarks_in_country":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            JOIN countries co ON c.country_id = co.id
            WHERE co.name = %s;
        """
        cursor.execute(query, (user_input,))
        result = cursor.fetchall()

    elif query_type == "nearby_landmarks":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN landmarks ln ON ST_DWithin(l.location, ln.location, 1000)
            WHERE ln.name = %s;
        """
        cursor.execute(query, (user_input,))
        result = cursor.fetchall()

    elif query_type == "landmarks_by_keyword":
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN reviews r ON l.id = r.landmark_id
            WHERE r.review_text ILIKE %s;
        """
        cursor.execute(query, ('%' + user_input + '%',))
        result = cursor.fetchall()

    else:
        result = []

    # Return JSON response
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
