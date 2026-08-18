def analyze_donation(
    food_name,
    quantity,
    preparation_time,
    storage_condition
):
    score = 0
    reasons = []

    # -------------------------
    # Quantity analysis
    # -------------------------
    if quantity >= 50:
        score += 3
        reasons.append("Large quantity of surplus food")
    elif quantity >= 20:
        score += 2
        reasons.append("Moderate quantity of surplus food")
    else:
        score += 1
        reasons.append("Small quantity of surplus food")

    # -------------------------
    # Storage analysis
    # -------------------------
    if storage_condition == "Room Temperature":
        score += 3
        reasons.append("Faster redistribution recommended")
    elif storage_condition == "Refrigerated":
        score += 1
        reasons.append("Refrigerated storage available")
    else:
        score += 2
        reasons.append("Storage condition requires monitoring")

    # -------------------------
    # Food type analysis
    # -------------------------
    prepared_food_keywords = [
        "biryani",
        "rice",
        "meal",
        "curry",
        "food",
        "pulao",
        "chapati",
        "roti",
        "dal",
        "vegetable"
    ]

    if any(
        word in food_name.lower()
        for word in prepared_food_keywords
    ):
        score += 2
        reasons.append(
            "Prepared food requires timely pickup"
        )

    # -------------------------
    # Preparation time
    # -------------------------
    if preparation_time <= 2:
        score += 2
        reasons.append(
            "Recently prepared food"
        )
    elif preparation_time <= 5:
        score += 1
        reasons.append(
            "Food was prepared several hours ago"
        )
    else:
        reasons.append(
            "Food has been prepared for an extended period"
        )

    # -------------------------
    # Priority
    # -------------------------
    if score >= 8:
        priority = "HIGH"
        recommendation = "Arrange pickup immediately"
    elif score >= 5:
        priority = "MEDIUM"
        recommendation = "Arrange pickup soon"
    else:
        priority = "LOW"
        recommendation = "Pickup can be scheduled"

    return {
        "priority": priority,
        "score": score,
        "reasons": reasons,
        "recommendation": recommendation
    }

    return {
        "priority": priority,
        "score": score,
        "reasons": reasons
    }
