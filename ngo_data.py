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
    available_ngos = [
        ngo for ngo in NGOS
        if ngo["capacity"] in ["High", "Medium"]
    ]

    available_ngos.sort(key=lambda x: x["distance"])

    return available_ngos[0]
