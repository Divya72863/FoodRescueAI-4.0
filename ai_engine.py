
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

        elapsed_minutes = current_minutes - preparation_minutes

        if elapsed_minutes < 0:
            elapsed_minutes += 24 * 60

        hours_since_preparation = elapsed_minutes / 60

    else:

        try:
            hours_since_preparation = float(preparation_time)
        except:
            hours_since_preparation = 0

    # ============================================================
    # FRESHNESS ANALYSIS
    # ============================================================

    if hours_since_preparation <= 2:

        score += 3

        reasons.append(
            "Food was prepared recently and can be redistributed quickly."
        )

    elif hours_since_preparation <= 4:

        score += 2

        reasons.append(
            "Food is within the recent redistribution window."
        )

    else:

        score += 3

        reasons.append(
            "Food has been waiting longer and requires timely action."
        )

    # ============================================================
    # QUANTITY ANALYSIS
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
    # STORAGE ANALYSIS
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
    # FOOD TYPE ANALYSIS
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

    if any(word in food_name.lower() for word in prepared_food_keywords):

        score += 2

        reasons.append(
            "Prepared food requires timely pickup and redistribution."
        )

    # ============================================================
    # PRIORITY CLASSIFICATION
    # ============================================================

    if score >= 8:

        priority = "HIGH"
        recommendation = "Arrange pickup immediately"

    elif score >= 5:

        priority = "MEDIUM"
        recommendation = "Arrange pickup soon"

    else:

        priority = "LOW"
        recommendation = "Pickup can be scheduled"

    # ============================================================
    # RETURN RESULT
    # ============================================================

    return {
        "priority": priority,
        "score": score,
        "reasons": reasons,
        "recommendation": recommendation,
        "hours_since_preparation": round(hours_since_preparation, 1)
    }
