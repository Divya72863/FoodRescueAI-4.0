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


def recommend_ngo(quantity):

    candidates = []

    for ngo in NGOS:

        if ngo["capacity"] == "High":
            capacity_score = 3
        elif ngo["capacity"] == "Medium":
            capacity_score = 2
        else:
            capacity_score = 1

        if ngo["need"] == "High":
            need_score = 3
        else:
            need_score = 2

        # Smaller distance = better
        distance_score = max(
            1,
            10 - ngo["distance"]
        )

        total_score = (
            capacity_score
            + need_score
            + distance_score
        )

        candidates.append({
            **ngo,
            "match_score": round(total_score, 2)
        })

    candidates.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return candidates[0], candidates
