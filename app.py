from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from datetime import datetime, time

from ai_engine import analyze_donation
from ngo_data import recommend_ngo, NGOS
from database import (
    create_database,
    add_donation,
    get_donations,
    mark_delivered
)

import sqlite3
import os


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "food-rescue-ai-demo-secret"
)


# ============================================================
# DATABASE
# ============================================================

create_database()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def update_status(donation_id, status):

    connection = sqlite3.connect(
        "food_rescue.db"
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE donations
        SET status = ?
        WHERE id = ?
        """,
        (status, donation_id)
    )

    connection.commit()
    connection.close()


def get_dashboard_stats():

    donations = get_donations()

    total_donations = len(donations)

    total_meals = sum(
        donation[2]
        for donation in donations
    )

    pending = sum(
        1
        for donation in donations
        if donation[7] == "Pending Pickup"
    )

    accepted = sum(
        1
        for donation in donations
        if donation[7] == "Accepted"
    )

    picked_up = sum(
        1
        for donation in donations
        if donation[7] == "Picked Up"
    )

    delivered = sum(
        1
        for donation in donations
        if donation[7] == "Delivered"
    )

    delivered_meals = sum(
        donation[2]
        for donation in donations
        if donation[7] == "Delivered"
    )

    return {
        "total_donations": total_donations,
        "total_meals": total_meals,
        "pending": pending,
        "accepted": accepted,
        "picked_up": picked_up,
        "delivered": delivered,
        "delivered_meals": delivered_meals
    }


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required():

    return "user" in session


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user" in session:

        if session["role"] == "Donor":
            return redirect(
                url_for("donor_dashboard")
            )

        return redirect(
            url_for("ngo_dashboard")
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "Donor"
        )

        if not email or not password:

            flash(
                "Please enter email and password.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        # Prototype authentication.
        # Any non-empty email/password works.

        session["user"] = email
        session["role"] = role

        flash(
            "Welcome to Food Rescue AI 4.0!",
            "success"
        )

        if role == "Donor":

            return redirect(
                url_for("donor_dashboard")
            )

        return redirect(
            url_for("ngo_dashboard")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# DONOR DASHBOARD
# ============================================================

@app.route("/donor")
def donor_dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "Donor":

        return redirect(
            url_for("ngo_dashboard")
        )

    stats = get_dashboard_stats()

    return render_template(
        "donor_dashboard.html",
        stats=stats,
        user=session["user"]
    )


# ============================================================
# CREATE DONATION
# ============================================================

@app.route(
    "/donation/create",
    methods=["GET", "POST"]
)
def create_donation():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "Donor":

        return redirect(
            url_for("ngo_dashboard")
        )

    if request.method == "POST":

        food_name = request.form.get(
            "food_name",
            ""
        ).strip()

        quantity_raw = request.form.get(
            "quantity",
            "0"
        )

        preparation_time_raw = request.form.get(
            "preparation_time",
            ""
        )

        storage_condition = request.form.get(
            "storage_condition",
            ""
        )

        donor_location = request.form.get(
            "donor_location",
            "Hyderabad"
        )

        if not food_name:

            flash(
                "Please enter the food name.",
                "error"
            )

            return redirect(
                url_for("create_donation")
            )

        try:

            quantity = int(
                quantity_raw
            )

        except ValueError:

            flash(
                "Quantity must be a valid number.",
                "error"
            )

            return redirect(
                url_for("create_donation")
            )

        if quantity <= 0:

            flash(
                "Quantity must be greater than zero.",
                "error"
            )

            return redirect(
                url_for("create_donation")
            )

        # ----------------------------------------------------
        # Convert HTML time input to datetime.time
        # ----------------------------------------------------

        try:

            preparation_time = datetime.strptime(
                preparation_time_raw,
                "%H:%M"
            ).time()

        except ValueError:

            preparation_time = datetime.now().time()

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        result = analyze_donation(
            food_name,
            quantity,
            preparation_time,
            storage_condition
        )

        # ----------------------------------------------------
        # NGO RECOMMENDATION
        # ----------------------------------------------------

        best_ngo, all_matches = recommend_ngo(
            donor_location=donor_location,
            quantity=quantity,
            priority=result["priority"]
        )

        # ----------------------------------------------------
        # SAVE DONATION
        # ----------------------------------------------------

        add_donation(
            food_name,
            quantity,
            preparation_time.strftime(
                "%H:%M"
            ),
            storage_condition,
            result["priority"],
            best_ngo["name"]
        )

        return render_template(
            "create_donation.html",
            result=result,
            ngo=best_ngo,
            matches=all_matches,
            submitted=True
        )

    return render_template(
        "create_donation.html",
        submitted=False
    )


# ============================================================
# MY DONATIONS
# ============================================================

@app.route("/donations")
def my_donations():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "Donor":

        return redirect(
            url_for("ngo_dashboard")
        )

    donations = get_donations()

    return render_template(
        "my_donations.html",
        donations=donations
    )


# ============================================================
# NGO DASHBOARD
# ============================================================

@app.route("/ngo")
def ngo_dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "NGO":

        return redirect(
            url_for("donor_dashboard")
        )

    stats = get_dashboard_stats()

    return render_template(
        "ngo_dashboard.html",
        stats=stats,
        user=session["user"]
    )


# ============================================================
# AVAILABLE DONATIONS
# ============================================================

@app.route("/ngo/donations")
def available_donations():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "NGO":

        return redirect(
            url_for("donor_dashboard")
        )

    donations = get_donations()

    available = [
        donation
        for donation in donations
        if donation[7] == "Pending Pickup"
    ]

    return render_template(
        "available_donations.html",
        donations=available
    )


# ============================================================
# ACCEPT DONATION
# ============================================================

@app.route(
    "/ngo/accept/<int:donation_id>",
    methods=["POST"]
)
def accept_donation(donation_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "NGO":

        return redirect(
            url_for("donor_dashboard")
        )

    update_status(
        donation_id,
        "Accepted"
    )

    flash(
        "Donation accepted successfully.",
        "success"
    )

    return redirect(
        url_for("available_donations")
    )


# ============================================================
# ACTIVE DELIVERIES
# ============================================================

@app.route("/ngo/deliveries")
def active_deliveries():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "NGO":

        return redirect(
            url_for("donor_dashboard")
        )

    donations = get_donations()

    active = [
        donation
        for donation in donations
        if donation[7] in [
            "Accepted",
            "Picked Up"
        ]
    ]

    return render_template(
        "active_deliveries.html",
        donations=active
    )


# ============================================================
# PICKUP
# ============================================================

@app.route(
    "/ngo/pickup/<int:donation_id>",
    methods=["POST"]
)
def pickup_donation(donation_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "NGO":

        return redirect(
            url_for("donor_dashboard")
        )

    update_status(
        donation_id,
        "Picked Up"
    )

    flash(
        "Pickup recorded successfully.",
        "success"
    )

    return redirect(
        url_for("active_deliveries")
    )


# ============================================================
# DELIVERY
# ============================================================

@app.route(
    "/ngo/deliver/<int:donation_id>",
    methods=["POST"]
)
def deliver_donation(donation_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session["role"] != "NGO":

        return redirect(
            url_for("donor_dashboard")
        )

    mark_delivered(
        donation_id
    )

    flash(
        "Donation marked as delivered!",
        "success"
    )

    return redirect(
        url_for("active_deliveries")
    )


# ============================================================
# IMPACT
# ============================================================

@app.route("/impact")
def impact():

    if not login_required():

        return redirect(
            url_for("login")
        )

    stats = get_dashboard_stats()

    return render_template(
        "impact.html",
        stats=stats
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return {
        "status": "healthy",
        "application": "Food Rescue AI 4.0"
    }


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=True
    )
