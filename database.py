import sqlite3

DB_NAME = "food_rescue.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            preparation_time TEXT,
            storage_condition TEXT,
            donor_location TEXT,
            priority TEXT,
            priority_score INTEGER,
            ngo_name TEXT,
            ngo_distance REAL,
            status TEXT DEFAULT 'Pending Pickup',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
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
    donor_location,
    priority,
    priority_score,
    ngo_name,
    ngo_distance
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO donations (
            food_name,
            quantity,
            preparation_time,
            storage_condition,
            donor_location,
            priority,
            priority_score,
            ngo_name,
            ngo_distance,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        food_name,
        quantity,
        preparation_time,
        storage_condition,
        donor_location,
        priority,
        priority_score,
        ngo_name,
        ngo_distance,
        "Pending Pickup"
    ))

    connection.commit()

    donation_id = cursor.lastrowid

    connection.close()

    return donation_id


# ============================================================
# GET ALL DONATIONS
# ============================================================

def get_donations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            food_name,
            quantity,
            preparation_time,
            storage_condition,
            donor_location,
            priority,
            priority_score,
            ngo_name,
            ngo_distance,
            status,
            created_at
        FROM donations
        ORDER BY id DESC
    """)

    donations = cursor.fetchall()

    connection.close()

    return [dict(row) for row in donations]


# ============================================================
# GET SINGLE DONATION
# ============================================================

def get_donation(donation_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            food_name,
            quantity,
            preparation_time,
            storage_condition,
            donor_location,
            priority,
            priority_score,
            ngo_name,
            ngo_distance,
            status,
            created_at
        FROM donations
        WHERE id = ?
    """, (donation_id,))

    donation = cursor.fetchone()

    connection.close()

    if donation:
        return dict(donation)

    return None


# ============================================================
# UPDATE DONATION STATUS
# ============================================================

def update_status(donation_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE donations
        SET status = ?
        WHERE id = ?
    """, (
        status,
        donation_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# ============================================================
# MARK AS PICKED UP
# ============================================================

def mark_picked_up(donation_id):
    return update_status(
        donation_id,
        "Picked Up"
    )


# ============================================================
# MARK AS DELIVERED
# ============================================================

def mark_delivered(donation_id):
    return update_status(
        donation_id,
        "Delivered"
    )


# ============================================================
# GET DONOR DASHBOARD STATISTICS
# ============================================================

def get_dashboard_stats():

    connection = get_connection()
    cursor = connection.cursor()

    # Total donations
    cursor.execute("""
        SELECT COUNT(*)
        FROM donations
    """)

    total_donations = cursor.fetchone()[0]

    # Total meals
    cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM donations
    """)

    total_meals = cursor.fetchone()[0]

    # Delivered donations
    cursor.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE status = 'Delivered'
    """)

    delivered_donations = cursor.fetchone()[0]

    # Pending donations
    cursor.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE status = 'Pending Pickup'
    """)

    pending_donations = cursor.fetchone()[0]

    # Picked up donations
    cursor.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE status = 'Picked Up'
    """)

    picked_up_donations = cursor.fetchone()[0]

    connection.close()

    return {
        "total_donations": total_donations,
        "total_meals": total_meals,
        "delivered_donations": delivered_donations,
        "pending_donations": pending_donations,
        "picked_up_donations": picked_up_donations
    }


# ============================================================
# GET NGO DONATIONS
# ============================================================

def get_ngo_donations(ngo_name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            food_name,
            quantity,
            preparation_time,
            storage_condition,
            donor_location,
            priority,
            priority_score,
            ngo_name,
            ngo_distance,
            status,
            created_at
        FROM donations
        WHERE ngo_name = ?
        ORDER BY id DESC
    """, (ngo_name,))

    donations = cursor.fetchall()

    connection.close()

    return [dict(row) for row in donations]


# ============================================================
# GET NGO STATISTICS
# ============================================================

def get_ngo_stats(ngo_name):

    connection = get_connection()
    cursor = connection.cursor()

    # Assigned donations
    cursor.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE ngo_name = ?
    """, (ngo_name,))

    total_donations = cursor.fetchone()[0]

    # Total meals
    cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM donations
        WHERE ngo_name = ?
    """, (ngo_name,))

    total_meals = cursor.fetchone()[0]

    # Delivered meals
    cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM donations
        WHERE ngo_name = ?
        AND status = 'Delivered'
    """, (ngo_name,))

    delivered_meals = cursor.fetchone()[0]

    # Pending pickups
    cursor.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE ngo_name = ?
        AND status = 'Pending Pickup'
    """, (ngo_name,))

    pending_pickups = cursor.fetchone()[0]

    connection.close()

    return {
        "total_donations": total_donations,
        "total_meals": total_meals,
        "delivered_meals": delivered_meals,
        "pending_pickups": pending_pickups
    }


# ============================================================
# INITIALIZE DATABASE
# ============================================================

create_database()
