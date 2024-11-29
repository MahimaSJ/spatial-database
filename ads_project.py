import psycopg2
import logging
from colorama import init, Fore, Back, Style
import time

init(autoreset=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def connect_to_db():
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

def show_progress(message):
    print(f"{Fore.CYAN}{message}...", end="", flush=True)
    for _ in range(3):  
        time.sleep(1)
        print(".", end="", flush=True)
    print(" Done!")

def display_title():
    print(Fore.GREEN + Style.BRIGHT + "===========================")
    print(Fore.YELLOW + Style.BRIGHT + "Spatial Database Application")
    print(Fore.GREEN + Style.BRIGHT + "===========================")

def find_landmarks_in_city(city_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s;
        """
        cursor.execute(query, (city_name,))
        landmarks = cursor.fetchall()
        conn.close()
        return landmarks
    except Exception as e:
        logging.error(f"Error in find_landmarks_in_city: {e}")
        return []

# Query to find landmarks within a radius
def find_landmarks_within_radius(city_name, radius_km):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s AND ST_DWithin(c.location, l.location, %s);
        """
        cursor.execute(query, (city_name, radius_km * 1000))  
        landmarks = cursor.fetchall()
        conn.close()
        return landmarks
    except Exception as e:
        logging.error(f"Error in find_landmarks_within_radius: {e}")
        return []

def calculate_distance(landmark1, landmark2):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT ST_Distance(
                (SELECT location FROM landmarks WHERE name = %s),
                (SELECT location FROM landmarks WHERE name = %s)
            ) AS distance_in_meters;
        """
        cursor.execute(query, (landmark1, landmark2))
        result = cursor.fetchone()

        if result is None or result[0] is None:
            conn.close()
            return None  

        distance = result[0]
        conn.close()
        return distance
    except Exception as e:
        logging.error(f"Error in calculate_distance: {e}")
        return None

def find_visitors(landmark_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT v.name, v.visit_date
            FROM visitors v
            JOIN landmarks l ON v.landmark_id = l.id
            WHERE l.name = %s;
        """
        cursor.execute(query, (landmark_name,))
        visitors = cursor.fetchall()
        conn.close()
        return visitors
    except Exception as e:
        logging.error(f"Error in find_visitors: {e}")
        return []

def fetch_reviews(landmark_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT r.review_text, r.rating, r.review_date
            FROM reviews r
            JOIN landmarks l ON r.landmark_id = l.id
            WHERE l.name = %s;
        """
        cursor.execute(query, (landmark_name,))
        reviews = cursor.fetchall()
        conn.close()
        return reviews
    except Exception as e:
        logging.error(f"Error in fetch_reviews: {e}")
        return []

def top_visited_landmarks():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT l.name, COUNT(v.id) AS visit_count
            FROM landmarks l
            LEFT JOIN visitors v ON l.id = v.landmark_id
            GROUP BY l.id
            ORDER BY visit_count DESC
            LIMIT 5;
        """
        cursor.execute(query)
        landmarks = cursor.fetchall()
        conn.close()
        return landmarks
    except Exception as e:
        logging.error(f"Error in top_visited_landmarks: {e}")
        return []

def average_rating(landmark_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT AVG(r.rating) AS average_rating
            FROM reviews r
            JOIN landmarks l ON r.landmark_id = l.id
            WHERE l.name = %s;
        """
        cursor.execute(query, (landmark_name,))
        avg_rating = cursor.fetchone()[0]
        conn.close()
        return avg_rating
    except Exception as e:
        logging.error(f"Error in average_rating: {e}")
        return None

def landmarks_no_visitors():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT l.name
            FROM landmarks l
            LEFT JOIN visitors v ON l.id = v.landmark_id
            WHERE v.id IS NULL;
        """
        cursor.execute(query)
        landmarks = cursor.fetchall()
        conn.close()
        return landmarks
    except Exception as e:
        logging.error(f"Error in landmarks_no_visitors: {e}")
        return []

def main():
    display_title()  
    
    while True:
        print(Fore.GREEN + "\nMenu:")
        print(Fore.CYAN + "1. Find landmarks in a city")
        print(Fore.CYAN + "2. Find landmarks within a radius")
        print(Fore.CYAN + "3. Calculate distance between two landmarks")
        print(Fore.CYAN + "4. Find visitors to a landmark")
        print(Fore.CYAN + "5. Fetch reviews for a landmark")
        print(Fore.CYAN + "6. Show top 5 most visited landmarks")
        print(Fore.CYAN + "7. Show average rating for a landmark")
        print(Fore.CYAN + "8. Show landmarks with no visitors")
        print(Fore.RED + "9. Exit")
        
        choice = input(Fore.YELLOW + "Enter your choice: ")

        if choice == "1":
            city_name = input(Fore.YELLOW + "Enter the city name: ")
            landmarks = find_landmarks_in_city(city_name)
            if not landmarks:
                print(Fore.RED + f"No landmarks found in {city_name}.")
            else:
                print(Fore.GREEN + f"Landmarks in {city_name}:")
                for landmark in landmarks:
                    print(Fore.GREEN + f"- {landmark[0]}")
        elif choice == "2":
            city_name = input(Fore.YELLOW + "Enter the city name: ")
            radius_km = float(input(Fore.YELLOW + "Enter the radius in kilometers: "))
            landmarks = find_landmarks_within_radius(city_name, radius_km)
            if not landmarks:
                print(Fore.RED + f"No landmarks found within {radius_km} km of {city_name}.")
            else:
                print(Fore.GREEN + f"Landmarks within {radius_km} km of {city_name}:")
                for landmark in landmarks:
                    print(Fore.GREEN + f"- {landmark[0]}")
        elif choice == "3":
            landmark1 = input(Fore.YELLOW + "Enter the first landmark name: ")
            landmark2 = input(Fore.YELLOW + "Enter the second landmark name: ")
            distance = calculate_distance(landmark1, landmark2)
            if distance is None:
                print(Fore.RED + f"Could not calculate the distance between {landmark1} and {landmark2}.")
            else:
                print(Fore.GREEN + f"Distance between {landmark1} and {landmark2}: {distance/1000:.2f} km")
        elif choice == "4":
            landmark_name = input(Fore.YELLOW + "Enter the landmark name: ")
            visitors = find_visitors(landmark_name)
            if not visitors:
                print(Fore.RED + f"No visitors found for {landmark_name}.")
            else:
                print(Fore.GREEN + f"Visitors to {landmark_name}:")
                for visitor in visitors:
                    print(Fore.GREEN + f"- {visitor[0]} on {visitor[1]}")
        elif choice == "5":
            landmark_name = input(Fore.YELLOW + "Enter the landmark name: ")
            reviews = fetch_reviews(landmark_name)
            if not reviews:
                print(Fore.RED + f"No reviews found for {landmark_name}.")
            else:
                print(Fore.GREEN + f"Reviews for {landmark_name}:")
                for review in reviews:
                    print(Fore.GREEN + f"- {review[0]} (Rating: {review[1]}/5) on {review[2]}")
        elif choice == "6":
            landmarks = top_visited_landmarks()
            if not landmarks:
                print(Fore.RED + "No landmarks found.")
            else:
                print(Fore.GREEN + "Top 5 Most Visited Landmarks:")
                for landmark in landmarks:
                    print(Fore.GREEN + f"- {landmark[0]} with {landmark[1]} visits")
        elif choice == "7":
            landmark_name = input(Fore.YELLOW + "Enter the landmark name: ")
            avg_rating = average_rating(landmark_name)
            if avg_rating is None:
                print(Fore.RED + f"No reviews found for {landmark_name}.")
            else:
                print(Fore.GREEN + f"Average rating for {landmark_name}: {avg_rating:.2f}")
        elif choice == "8":
            landmarks = landmarks_no_visitors()
            if not landmarks:
                print(Fore.RED + "All landmarks have visitors.")
            else:
                print(Fore.GREEN + "Landmarks with no visitors:")
                for landmark in landmarks:
                    print(Fore.GREEN + f"- {landmark[0]}")
        elif choice == "9":
            print(Fore.RED + "Exiting the application.")
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
