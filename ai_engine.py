from datetime import datetime, time


def analyze_donation(
    food_name,
    quantity,
    preparation_time,
    storage_condition
):
    score = 0
    reasons = []

    # ============================================================
    # PREPARATION TIME ANALYSIS
    # ============================================================

    # Streamlit time_input() returns datetime.time.
    # Convert it into the number of hours since midnight.

    if isinstance(preparation_time, time):

        preparation_minutes = (
            preparation_time.hour * 60
            + preparation_time.minute
        )

        current_time = datetime.now().time()

        current_minutes = (
            current_time.hour * 60
            + current_time.minute
        )

        # Handle preparation time crossing midnight
        elapsed_minutes = current_minutes - preparation_minutes

        if elapsed_minutes < 0:
            elapsed_minutes += 24 * 60

        hours_since_preparation = elapsed_minutes / 60

    else:
        # Fallback in case a numeric value is passed
        try:
            hours_since_preparation = float(preparation_time)
        except:
            hours_since_preparation = 0

    # ============================================================
    # FRESHNESS / TIME FACTOR
    # ============================================================

    if hours_since_preparation <= 2:

        score += 3

        reasons.append(
            "Food was prepared recently and can be redistributed quickly."
        )

    elif hours_since_preparation <= 4:

        score += 2

        reasons.append(
            "Food has been prepared within the recent redistribution window."
        )

    else:

        score += 3

        reasons.append(
            "Food has been waiting longer and requires timely action."
        )

    # ============================================================
    # QUANTITY FACTOR
    # ============================================================

    if quantity >= 50:

        score += 3

        reasons.append(
            "Large quantity of surplus food available."
        )

    elif quantity >= 20:

        score += 2

        reasons.append(
            "Moderate quantity of surplus food available."
        )

    else:

        score += 1

        reasons.append(
            "Small quantity of surplus food available."
        )

    # ============================================================
    # STORAGE CONDITION
    # ============================================================

    if storage_condition == "Room Temperature":

        score += 3

        reasons.append(
            "Room-temperature food requires faster redistribution."
        )

    elif storage_condition == "Refrigerated":

        score += 1

        reasons.append(
            "Refrigerated storage helps preserve the food."
        )

    elif storage_condition == "Frozen":

        score += 0

        reasons.append(
            "Frozen storage provides additional preservation time."
        )

    # ============================================================
    # FOOD TYPE
    # ============================================================

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
        "sambar",
        "vegetable",
        "fried rice"
    ]

    if any(
        word in food_name.lower()
        for word in prepared_food_keywords
    ):

        score += 2

        reasons.append(
            "Prepared food requires timely pickup and redistribution."
        )

    # ============================================================
    # PRIORITY CLASSIFICATION
    # ============================================================

    if score >= 8:

        priority = "HIGH"

    elif score >= 5:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # ============================================================
    # RETURN RESULT
    # ============================================================

    return {
        "priority": priority,
        "score": score,
        "reasons": reasons,
        "hours_since_preparation": round(
            hours_since_preparation,
            1
        )
    }

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
