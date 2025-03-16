import psycopg2
import psycopg2.extras


def connect_db():
    conn = psycopg2.connect(
        dbname="VKB",
        user="neondb_owner",
        password="npg_Ta5XZNco7sGU",
        host="ep-lucky-fog-a9bpnxdm-pooler.gwc.azure.neon.tech",
        sslmode="require",
    )
    return conn


def fetch_data(query, params=None):
    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, params or ())
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        print("Error fetching data:", e)
        return None


def insert_data(query, params):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
        print("Data inserted successfully")
    except Exception as e:
        print("Error inserting data:", e)


def create_tables_if_not_exists():
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Skapa tabellen 'API_VKB' om den inte redan finns
        create_api_vkb_table = """
        CREATE TABLE IF NOT EXISTS API (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(100) NOT NULL,
            user_mail VARCHAR(100) NOT NULL,
            api_key VARCHAR(64) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Skapa tabellen 'Car' om den inte redan finns
        create_car_table = """
        CREATE TABLE IF NOT EXISTS Car (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(100),
            series VARCHAR(100),
            model VARCHAR(100),
            generation VARCHAR(100),
            model_gen_engine VARCHAR(255),
            car_name VARCHAR(255),
            chassis VARCHAR(100),
            engine VARCHAR(255),
            engine_type VARCHAR(100),
            horsepower INTEGER,
            engine_start_year INTEGER,
            engine_end_year INTEGER,
            model_year INTEGER,
            trim_package VARCHAR(100),
            licence_plate VARCHAR(20) UNIQUE NOT NULL,
            vin VARCHAR(50),
            vehicle_type VARCHAR(50),
            engine_name VARCHAR(255),
            body_code VARCHAR(50),
            sales_name VARCHAR(255),
            attribute_values JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Skapa tabellen 'Payment' om den inte redan finns
        create_payment_table = """
        CREATE TABLE IF NOT EXISTS Payment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES API(id),
            amount FLOAT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Utför alla skapa-tabell frågor
        cur.execute(create_api_vkb_table)
        cur.execute(create_car_table)
        cur.execute(create_payment_table)

        conn.commit()
        cur.close()
        conn.close()
        print("Tabeller skapades eller finns redan.")
    except Exception as e:
        print("Fel vid skapande av tabeller:", e)


if __name__ == "__main__":
    # Skapa tabellerna om de inte finns
    create_tables_if_not_exists()

    # Exempel: Hämta data från API
    select_query = "SELECT * FROM API;"
    rows = fetch_data(select_query)
    if rows:
        for row in rows:
            print(dict(row))
