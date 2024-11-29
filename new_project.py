import psycopg2
from psycopg2 import sql
import logging
from colorama import Fore

# Database connection

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="spatialproject",
            user="mahi",
            password="mahi",
            host="localhost",
            port="5432",
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Query functions

def find_neighboring_cities(city_name, radius_km):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT c2.name
            FROM cities c1
            JOIN cities c2 ON c1.id != c2.id
            WHERE c1.name = %s AND ST_DWithin(c1.location, c2.location, %s);
        """
        cursor.execute(query, (city_name, radius_km * 1000))
        cities = cursor.fetchall()
        conn.close()
        return cities
    except Exception as e:
        logging.error(f"Error in find_neighboring_cities: {e}")
        return []

def find_landmarks_along_route(route_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT l.name
            FROM landmarks l
            JOIN routes r ON ST_Intersects(l.location, r.path)
            WHERE r.id = %s;
        """
        cursor.execute(query, (route_id,))
        landmarks = cursor.fetchall()
        conn.close()
        return landmarks
    except Exception as e:
        logging.error(f"Error in find_landmarks_along_route: {e}")
        return []

def calculate_bounding_box(city_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT ST_Extent(l.location) AS bounding_box
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s;
        """
        cursor.execute(query, (city_name,))
        bounding_box = cursor.fetchone()
        conn.close()
        return bounding_box[0] if bounding_box else None
    except Exception as e:
        logging.error(f"Error in calculate_bounding_box: {e}")
        return None

def find_closest_landmark(lat, lon):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT name, ST_Distance(location, ST_SetSRID(ST_Point(%s, %s), 4326)) AS distance
            FROM landmarks
            ORDER BY distance ASC
            LIMIT 1;
        """
        cursor.execute(query, (lon, lat))  # Longitude first, latitude second
        landmark = cursor.fetchone()
        conn.close()
        return landmark
    except Exception as e:
        logging.error(f"Error in find_closest_landmark: {e}")
        return None

def is_landmark_in_region(landmark_name, region_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT EXISTS(
                SELECT 1
                FROM landmarks l
                JOIN regions r ON ST_Within(l.location, r.boundary)
                WHERE l.name = %s AND r.id = %s
            ) AS is_inside;
        """
        cursor.execute(query, (landmark_name, region_id))
        result = cursor.fetchone()
        conn.close()
        return result[0]
    except Exception as e:
        logging.error(f"Error in is_landmark_in_region: {e}")
        return False

def find_city_landmark_center(city_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT ST_Centroid(ST_Collect(l.location)) AS center
            FROM landmarks l
            JOIN cities c ON l.city_id = c.id
            WHERE c.name = %s;
        """
        cursor.execute(query, (city_name,))
        center = cursor.fetchone()
        conn.close()
        return center[0] if center else None
    except Exception as e:
        logging.error(f"Error in find_city_landmark_center: {e}")
        return None

def find_intersection_area(region_id1, region_id2):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = """
            SELECT ST_Area(ST_Intersection(r1.boundary, r2.boundary)) AS intersection_area
            FROM regions r1, regions r2
            WHERE r1.id = %s AND r2.id = %s;
        """
        cursor.execute(query, (region_id1, region_id2))
        intersection_area = cursor.fetchone()
        conn.close()
        return intersection_area[0] if intersection_area else None
    except Exception as e:
        logging.error(f"Error in find_intersection_area: {e}")
        return None

# Main menu

def main():
    while True:
        print(Fore.CYAN + "Spatial Database Application")
        print(Fore.CYAN + "1. Find neighboring cities")
        print(Fore.CYAN + "2. Find landmarks along a route")
        print(Fore.CYAN + "3. Calculate bounding box for a city's landmarks")
        print(Fore.CYAN + "4. Find closest landmark to a given point")
        print(Fore.CYAN + "5. Check if a landmark is inside a specific region")
        print(Fore.CYAN + "6. Find the center of all landmarks in a city")
        print(Fore.CYAN + "7. Find the intersection area between two regions")
        print(Fore.CYAN + "0. Exit")

        choice = input(Fore.YELLOW + "Enter your choice: ")

        if choice == "1":
            city_name = input(Fore.YELLOW + "Enter the city name: ")
            radius_km = float(input(Fore.YELLOW + "Enter the radius in kilometers: "))
            cities = find_neighboring_cities(city_name, radius_km)
            if not cities:
                print(Fore.RED + "No neighboring cities found.")
            else:
                print(Fore.GREEN + f"Neighboring cities within {radius_km} km of {city_name}:")
                for city in cities:
                    print(Fore.GREEN + f"- {city[0]}")

        elif choice == "2":
            route_id = input(Fore.YELLOW + "Enter the route ID: ")
            landmarks = find_landmarks_along_route(route_id)
            if not landmarks:
                print(Fore.RED + "No landmarks found along the route.")
            else:
                print(Fore.GREEN + "Landmarks along the route:")
                for landmark in landmarks:
                    print(Fore.GREEN + f"- {landmark[0]}")

        elif choice == "3":
            city_name = input(Fore.YELLOW + "Enter the city name: ")
            bounding_box = calculate_bounding_box(city_name)
            if not bounding_box:
                print(Fore.RED + "Bounding box could not be calculated.")
            else:
                print(Fore.GREEN + f"Bounding box for landmarks in {city_name}: {bounding_box}")

        elif choice == "4":
            lat = float(input(Fore.YELLOW + "Enter latitude: "))
            lon = float(input(Fore.YELLOW + "Enter longitude: "))
            landmark = find_closest_landmark(lat, lon)
            if not landmark:
                print(Fore.RED + "No landmark found nearby.")
            else:
                print(Fore.GREEN + f"Closest landmark: {landmark[0]} ({landmark[1]:.2f} meters away)")

        elif choice == "5":
            landmark_name = input(Fore.YELLOW + "Enter the landmark name: ")
            region_id = input(Fore.YELLOW + "Enter the region ID: ")
            is_inside = is_landmark_in_region(landmark_name, region_id)
            print(Fore.GREEN + f"Is the landmark inside the region? {'Yes' if is_inside else 'No'}")

        elif choice == "6":
            city_name = input(Fore.YELLOW + "Enter the city name: ")
            center = find_city_landmark_center(city_name)
            if not center:
                print(Fore.RED + "Center could not be fetched")

        elif choice == "7":
            region_id1 = input(Fore.YELLOW + "Enter the first region ID: ")
            region_id2 = input(Fore.YELLOW + "Enter the second region ID: ")
            intersection_area = find_intersection_area(region_id1, region_id2)
            if not intersection_area:
                print(Fore.RED + "No intersection area calculated.")
            else:
                print(Fore.GREEN + f"Intersection area: {intersection_area} square meters")

        elif choice == "0":
            print(Fore.CYAN + "Exiting the application. Goodbye!")
            break

    else:
        print(Fore.RED + "Invalid choice. Please try again.")

main()