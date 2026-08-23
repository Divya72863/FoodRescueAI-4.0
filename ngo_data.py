# ============================================================
# FOOD RESCUE AI 4.0
# INTELLIGENT NGO MATCHING ENGINE
# ============================================================

import math


# ------------------------------------------------------------
# SAMPLE NGO DATABASE
# ------------------------------------------------------------
# These are prototype/demo organizations.
# They do NOT represent real partnerships.

NGOS = [
    {
        "name": "Hope Community Kitchen",
        "location": "Hyderabad",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "capacity": 100,
        "need": "High"
    },
    {
        "name": "Helping Hands Foundation",
        "location": "Hyderabad",
        "latitude": 17.4065,
        "longitude": 78.4772,
        "capacity": 50,
        "need": "High"
    },
    {
        "name": "Community Care Center",
        "location": "Hyderabad",
        "latitude": 17.3616,
        "longitude": 78.4747,
        "capacity": 150,
        "need": "Medium"
    },
    {
        "name": "Food For All Center",
        "location": "Hyderabad",
        "latitude": 17.4156,
        "longitude": 78.4347,
        "capacity": 75,
        "need": "Medium"
    }
]


# ------------------------------------------------------------
# DEMO LOCATION DATABASE
# ------------------------------------------------------------

LOCATIONS = {

    "Hyderabad": {
        "latitude": 17.3850,
        "longitude": 78.4867
    },

    "Secunderabad": {
        "latitude": 17.4399,
        "longitude": 78.4983
    },

    "Kukatpally": {
        "latitude": 17.4849,
        "longitude": 78.4138
    },

    "Madhapur": {
        "latitude": 17.4483,
        "longitude": 78.3915
    },

    "Gachibowli": {
        "latitude": 17.4401,
        "longitude": 78.3489
    },

    "Begumpet": {
        "latitude": 17.4448,
        "longitude": 78.4667
    }
}


# ------------------------------------------------------------
# DISTANCE CALCULATION
# ------------------------------------------------------------

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    """
    Calculate approximate distance between
    two geographic coordinates using Haversine formula.
    """

    earth_radius = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# ------------------------------------------------------------
# GET DONOR LOCATION
# ------------------------------------------------------------

def get_location_coordinates(
    location_name
):

    location_name = location_name.strip()

    # Exact match
    if location_name in LOCATIONS:
        return LOCATIONS[location_name]

    # Case-insensitive match
    for name, coordinates in LOCATIONS.items():

        if name.lower() == location_name.lower():
            return coordinates

    # Default location
    return LOCATIONS["Hyderabad"]


# ------------------------------------------------------------
# NGO MATCHING
# ------------------------------------------------------------

def recommend_ngo(
    donor_location="Hyderabad",
    quantity=50,
    priority="MEDIUM"
):

    donor_coordinates = get_location_coordinates(
        donor_location
    )

    donor_lat = donor_coordinates["latitude"]
    donor_lon = donor_coordinates["longitude"]

    recommendations = []

    for ngo in NGOS:

        # ----------------------------------------------------
        # DISTANCE
        # ----------------------------------------------------

        distance = calculate_distance(
            donor_lat,
            donor_lon,
            ngo["latitude"],
            ngo["longitude"]
        )

        # ----------------------------------------------------
        # CAPACITY SCORE
        # ----------------------------------------------------

        if ngo["capacity"] >= quantity:

            capacity_score = 100

        elif ngo["capacity"] >= quantity * 0.5:

            capacity_score = 60

        else:

            capacity_score = 20

        # ----------------------------------------------------
        # NEED SCORE
        # ----------------------------------------------------

        if ngo["need"] == "High":

            need_score = 100

        elif ngo["need"] == "Medium":

            need_score = 70

        else:

            need_score = 40

        # ----------------------------------------------------
        # DISTANCE SCORE
        # ----------------------------------------------------

        if distance <= 3:

            distance_score = 100

        elif distance <= 5:

            distance_score = 80

        elif distance <= 10:

            distance_score = 60

        else:

            distance_score = 30

        # ----------------------------------------------------
        # PRIORITY ADJUSTMENT
        # ----------------------------------------------------

        if priority == "HIGH":

            # Distance becomes more important
            final_score = (
                capacity_score * 0.35
                +
                need_score * 0.25
                +
                distance_score * 0.40
            )

        elif priority == "MEDIUM":

            final_score = (
                capacity_score * 0.40
                +
                need_score * 0.30
                +
                distance_score * 0.30
            )

        else:

            final_score = (
                capacity_score * 0.45
                +
                need_score * 0.35
                +
                distance_score * 0.20
            )

        recommendations.append({

            "name": ngo["name"],

            "location": ngo["location"],

            "distance": round(
                distance,
                2
            ),

            "capacity": ngo["capacity"],

            "need": ngo["need"],

            "capacity_score": capacity_score,

            "need_score": need_score,

            "distance_score": distance_score,

            "match_score": round(
                final_score,
                1
            )

        })

    # --------------------------------------------------------
    # SORT BY MATCH SCORE
    # --------------------------------------------------------

    recommendations.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    # Best NGO
    best_ngo = recommendations[0]

    return best_ngo, recommendations
