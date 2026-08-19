# ============================================================
# FOOD RESCUE AI 4.0
# NGO RECOMMENDATION DATA
# ============================================================

NGOS = [
    {
        "name": "Hope Community Kitchen",
        "location": "Hyderabad",
        "distance": 3.2,
        "capacity": "High",
        "need": "High"
    },
    {
        "name": "Helping Hands Foundation",
        "location": "Hyderabad",
        "distance": 5.1,
        "capacity": "Medium",
        "need": "High"
    },
    {
        "name": "Community Care Center",
        "location": "Hyderabad",
        "distance": 7.4,
        "capacity": "High",
        "need": "Medium"
    }
]


def recommend_ngo():

    # Find NGOs that currently have capacity
    available_ngos = [
        ngo
        for ngo in NGOS
        if ngo["capacity"] in ["High", "Medium"]
    ]

    # If no NGO is available
    if not available_ngos:
        return {
            "name": "No NGO Available",
            "location": "N/A",
            "distance": 0,
            "capacity": "Unavailable",
            "need": "N/A"
        }

    # Prioritize higher-need NGOs
    # and then choose the closest suitable NGO
    available_ngos.sort(
        key=lambda ngo: (
            0 if ngo["need"] == "High" else 1,
            ngo["distance"]
        )
    )

    return available_ngos[0]
