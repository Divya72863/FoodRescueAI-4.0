from datetime import datetime


def analyze_donation(food_name, quantity, preparation_time, storage_condition):
    score = 0
    reasons = []

    # Quantity factor
    if quantity >= 50:
        score += 3
        reasons.append("Large quantity of surplus food")
    elif quantity >= 20:
        score += 2
        reasons.append("Moderate quantity of surplus food")
    else:
        score += 1

    # Storage condition
    if storage_condition == "Room Temperature":
        score += 3
        reasons.append("Food requires faster redistribution")
    elif storage_condition == "Refrigerated":
        score += 1
        reasons.append("Refrigerated storage available")
    else:
        score += 2

    # Food type
    prepared_food_keywords = [
        "biryani",
        "rice",
        "meal",
        "curry",
        "food",
        "pulao",
        "chapati"
    ]

    if any(word in food_name.lower() for word in prepared_food_keywords):
        score += 2
        reasons.append("Prepared food requires timely pickup")

    # Priority
    if score >= 6:
        priority = "HIGH"
    elif score >= 4:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "priority": priority,
        "score": score,
        "reasons": reasons
    }
