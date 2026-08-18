import sqlite3

DB_NAME = "food_rescue.db"


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            food_name TEXT,

            quantity INTEGER,

            preparation_time INTEGER,

            storage_condition TEXT,

            priority TEXT,

            ngo_name TEXT,

            status TEXT

        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# ADD DONATION
# ============================================================

def add_donation(
    food_name,
    quantity,
    preparation_time,
    storage_condition,
    priority,
    ngo_name
):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO donations
        (
            food_name,
            quantity,
            preparation_time,
            storage_condition,
            priority,
            ngo_name,
            status
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (
        food_name,
        quantity,
        preparation_time,
        storage_condition,
        priority,
        ngo_name,
        "Pending Pickup"
    ))

    connection.commit()

    connection.close()


# ============================================================
# GET ALL DONATIONS
# ============================================================

def get_donations():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM donations
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    connection.close()

    return data


# ============================================================
# MARK DONATION AS DELIVERED
# ============================================================

def mark_delivered(donation_id):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE donations

        SET status = 'Delivered'

        WHERE id = ?

    """, (donation_id,))

    connection.commit()

    connection.close()

        WHERE id = ?
    """, (donation_id,))

    connection.commit()
    connection.close()
