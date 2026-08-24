from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

# ============================================================
# FOOD RESCUE AI
# Enhanced single-file prototype
# ============================================================

app = FastAPI(
    title="Food Rescue AI",
    description="AI-powered food donation prioritization and NGO recommendation",
    version="2.0.0"
)

DB_FILE = "food_rescue.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT NOT NULL,
            food_name TEXT NOT NULL,
            food_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            freshness_hours INTEGER NOT NULL,
            pickup_location TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            priority_level TEXT NOT NULL,
            priority_reason TEXT NOT NULL,
            ngo_name TEXT NOT NULL,
            ngo_location TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# NGO DATA
# ============================================================

NGOS = [
    {
        "name": "Helping Hands Foundation",
        "location": "Hyderabad",
        "focus": ["cooked", "vegetarian", "bakery"],
        "capacity": 1000
    },
    {
        "name": "Food For All",
        "location": "Secunderabad",
        "focus": ["cooked", "rice", "vegetarian"],
        "capacity": 800
    },
    {
        "name": "Hope Community Kitchen",
        "location": "Kukatpally",
        "focus": ["cooked", "bakery", "mixed"],
        "capacity": 600
    },
    {
        "name": "Care & Share NGO",
        "location": "Madhapur",
        "focus": ["fruits", "vegetarian", "bakery"],
        "capacity": 500
    },
    {
        "name": "Community Food Support",
        "location": "Miyapur",
        "focus": ["mixed", "fruits", "vegetarian"],
        "capacity": 700
    }
]


# ============================================================
# DATA MODELS
# ============================================================

class Donation(BaseModel):
    donor_name: str
    food_name: str
    food_type: str
    quantity: float
    unit: str
    freshness_hours: int
    pickup_location: str


class StatusUpdate(BaseModel):
    status: str


# ============================================================
# AI PRIORITY ENGINE
# ============================================================

def analyze_food(data):

    score = 0
    reasons = []

    # Freshness
    if data.freshness_hours <= 2:
        score += 40
        reasons.append("The food is extremely time-sensitive")

    elif data.freshness_hours <= 6:
        score += 30
        reasons.append("The food should be redistributed soon")

    elif data.freshness_hours <= 12:
        score += 20
        reasons.append("The food has moderate redistribution urgency")

    elif data.freshness_hours <= 24:
        score += 10
        reasons.append("The food has reasonable remaining freshness")

    else:
        reasons.append("The food has relatively longer freshness")

    # Quantity
    if data.quantity >= 100:
        score += 25
        reasons.append("The large quantity can support many beneficiaries")

    elif data.quantity >= 50:
        score += 20
        reasons.append("The donation provides a useful quantity of food")

    elif data.quantity >= 20:
        score += 10
        reasons.append("The donation provides a moderate quantity")

    else:
        score += 5
        reasons.append("The donation quantity is suitable for a smaller distribution")

    # Food type
    food_type = data.food_type.lower()

    if food_type == "cooked":
        score += 20
        reasons.append("Cooked food generally requires faster redistribution")

    elif food_type == "bakery":
        score += 15
        reasons.append("Bakery items can be distributed efficiently")

    elif food_type == "fruits":
        score += 12
        reasons.append("Fresh produce can support immediate nutritional needs")

    elif food_type == "vegetarian":
        score += 12
        reasons.append("Vegetarian food is suitable for broad beneficiary groups")

    else:
        score += 8
        reasons.append("The food can be considered for community redistribution")

    score = min(score, 100)

    if score >= 80:
        level = "CRITICAL"
    elif score >= 60:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, ". ".join(reasons) + "."


# ============================================================
# NGO RECOMMENDATION
# ============================================================

def recommend_ngo(data):

    food_type = data.food_type.lower()
    location = data.pickup_location.lower()

    best_ngo = None
    best_score = -1

    for ngo in NGOS:

        score = 0

        # Food compatibility
        if food_type in ngo["focus"]:
            score += 50
        elif "mixed" in ngo["focus"]:
            score += 30

        # Capacity
        if data.quantity <= ngo["capacity"]:
            score += 30

        # Location
        if ngo["location"].lower() in location:
            score += 20

        if score > best_score:
            best_score = score
            best_ngo = ngo

    return best_ngo


# ============================================================
# CREATE DONATION
# ============================================================

@app.post("/api/donations")
def create_donation(data: Donation):

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero."
        )

    if data.freshness_hours < 0:
        raise HTTPException(
            status_code=400,
            detail="Freshness cannot be negative."
        )

    score, level, reason = analyze_food(data)

    ngo = recommend_ngo(data)

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO donations (
            donor_name,
            food_name,
            food_type,
            quantity,
            unit,
            freshness_hours,
            pickup_location,
            priority_score,
            priority_level,
            priority_reason,
            ngo_name,
            ngo_location,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.donor_name,
        data.food_name,
        data.food_type,
        data.quantity,
        data.unit,
        data.freshness_hours,
        data.pickup_location,
        score,
        level,
        reason,
        ngo["name"],
        ngo["location"],
        "Pending Pickup",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    donation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "donation_id": donation_id,
        "priority_score": score,
        "priority_level": level,
        "priority_reason": reason,
        "ngo": ngo
    }


# ============================================================
# GET DONATIONS
# ============================================================

@app.get("/api/donations")
def get_donations():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM donations
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# UPDATE STATUS
# ============================================================

@app.put("/api/donations/{donation_id}/status")
def update_status(
    donation_id: int,
    data: StatusUpdate
):

    allowed = [
        "Pending Pickup",
        "Picked Up",
        "In Transit",
        "Delivered",
        "Completed"
    ]

    if data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Invalid status."
        )

    conn = get_db()

    cursor = conn.execute("""
        UPDATE donations
        SET status = ?
        WHERE id = ?
    """, (
        data.status,
        donation_id
    ))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Donation not found."
        )

    conn.close()

    return {
        "success": True,
        "donation_id": donation_id,
        "status": data.status
    }


# ============================================================
# METRICS
# ============================================================

@app.get("/api/metrics")
def metrics():

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) AS c FROM donations"
    ).fetchone()["c"]

    delivered = conn.execute("""
        SELECT COUNT(*) AS c
        FROM donations
        WHERE status IN ('Delivered', 'Completed')
    """).fetchone()["c"]

    pending = conn.execute("""
        SELECT COUNT(*) AS c
        FROM donations
        WHERE status NOT IN ('Delivered', 'Completed')
    """).fetchone()["c"]

    critical = conn.execute("""
        SELECT COUNT(*) AS c
        FROM donations
        WHERE priority_level = 'CRITICAL'
    """).fetchone()["c"]

    quantity = conn.execute("""
        SELECT COALESCE(SUM(quantity), 0) AS q
        FROM donations
    """).fetchone()["q"]

    conn.close()

    return {
        "total_donations": total,
        "delivered_donations": delivered,
        "pending_donations": pending,
        "critical_donations": critical,
        "food_quantity": quantity
    }


# ============================================================
# FRONTEND
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Food Rescue AI</title>

<style>

@import url(
'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
);

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {

    --dark: #10172b;
    --dark2: #18213d;

    --primary: #6557e8;
    --primary-dark: #5042d0;

    --bg: #f4f6fb;

    --white: #ffffff;

    --text: #171d32;

    --muted: #70798f;

    --border: #e2e6ef;

    --green: #20b477;

    --orange: #ef9b3f;

    --red: #e85b5b;

    --blue: #4386e8;
}

body {

    font-family: "DM Sans", sans-serif;

    background: var(--bg);

    color: var(--text);

    font-size: 16px;
}

button,
input,
select {

    font-family: inherit;
}

button {

    cursor: pointer;
}

.app {

    min-height: 100vh;

    display: flex;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

.sidebar {

    width: 270px;

    min-height: 100vh;

    background: linear-gradient(
        180deg,
        #10172b,
        #161f3a
    );

    color: white;

    padding: 30px 20px;

    position: fixed;

    left: 0;

    top: 0;

    bottom: 0;

    z-index: 10;
}

.logo {

    display: flex;

    align-items: center;

    gap: 14px;

    padding: 0 10px 40px;
}

.logo-icon {

    width: 50px;

    height: 50px;

    border-radius: 15px;

    background: linear-gradient(
        135deg,
        #796af1,
        #5140cf
    );

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 25px;
}

.logo-title {

    font-family: "Space Grotesk";

    font-size: 21px;

    font-weight: 700;
}

.logo-subtitle {

    font-size: 12px;

    color: #aab2c9;

    margin-top: 3px;
}

.menu-title {

    color: #777f99;

    font-size: 12px;

    text-transform: uppercase;

    letter-spacing: 1.4px;

    margin: 10px 12px 12px;
}

.nav {

    display: flex;

    flex-direction: column;

    gap: 8px;
}

.nav button {

    border: none;

    background: transparent;

    color: #aeb6ca;

    text-align: left;

    padding: 15px 15px;

    border-radius: 12px;

    font-size: 16px;

    font-weight: 600;

    display: flex;

    align-items: center;

    gap: 13px;

    transition: .2s;
}

.nav button:hover {

    background: rgba(255,255,255,.08);

    color: white;
}

.nav button.active {

    background: linear-gradient(
        135deg,
        #6959e8,
        #5142cf
    );

    color: white;

    box-shadow:
        0 8px 22px rgba(91,72,210,.3);
}

.sidebar-bottom {

    position: absolute;

    left: 20px;

    right: 20px;

    bottom: 25px;

    background: rgba(255,255,255,.06);

    padding: 17px;

    border-radius: 14px;

    border: 1px solid rgba(255,255,255,.07);
}

.sidebar-bottom strong {

    display: block;

    font-size: 14px;

    margin-bottom: 5px;
}

.sidebar-bottom span {

    color: #9099b1;

    font-size: 12px;
}


/* =========================================================
   MAIN
   ========================================================= */

.main {

    margin-left: 270px;

    width: calc(100% - 270px);

    padding: 35px 42px 60px;
}

.topbar {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 30px;
}

.page-title {

    font-family: "Space Grotesk";

    font-size: 34px;

    font-weight: 700;

    letter-spacing: -.5px;
}

.page-subtitle {

    color: var(--muted);

    font-size: 16px;

    margin-top: 7px;
}

.date-box {

    background: white;

    border: 1px solid var(--border);

    border-radius: 12px;

    padding: 12px 17px;

    color: var(--muted);

    font-size: 14px;
}


/* =========================================================
   PAGE SYSTEM
   ========================================================= */

.page {

    display: none;

    animation: fadeIn .25s ease;
}

.page.active {

    display: block;
}

@keyframes fadeIn {

    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* =========================================================
   DASHBOARD HERO
   ========================================================= */

.hero {

    background:
        radial-gradient(
            circle at 85% 25%,
            rgba(121,106,241,.35),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #1b2443,
            #121a32
        );

    color: white;

    border-radius: 22px;

    padding: 35px;

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 27px;

    overflow: hidden;

    position: relative;
}

.hero h2 {

    font-family: "Space Grotesk";

    font-size: 30px;

    margin-bottom: 10px;
}

.hero p {

    color: #c1c8db;

    max-width: 620px;

    line-height: 1.6;

    font-size: 16px;
}

.hero button {

    border: none;

    background: white;

    color: #5142cf;

    padding: 15px 22px;

    border-radius: 12px;

    font-size: 16px;

    font-weight: 700;

    margin-top: 22px;
}

.hero-icon {

    font-size: 110px;

    opacity: .18;

    padding-right: 50px;
}


/* =========================================================
   METRICS
   ========================================================= */

.metrics {

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 18px;

    margin-bottom: 27px;
}

.metric {

    background: white;

    border: 1px solid var(--border);

    border-radius: 17px;

    padding: 23px;

    box-shadow:
        0 5px 18px rgba(25,35,65,.04);
}

.metric-top {

    display: flex;

    justify-content: space-between;

    align-items: center;
}

.metric-icon {

    width: 45px;

    height: 45px;

    border-radius: 12px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #efedff;

    font-size: 21px;
}

.metric-label {

    color: var(--muted);

    font-size: 14px;

    font-weight: 600;

    margin-top: 18px;
}

.metric-value {

    font-family: "Space Grotesk";

    font-size: 32px;

    font-weight: 700;

    margin-top: 5px;
}


/* =========================================================
   CARDS
   ========================================================= */

.card {

    background: white;

    border: 1px solid var(--border);

    border-radius: 18px;

    padding: 25px;

    box-shadow:
        0 5px 18px rgba(25,35,65,.04);

    margin-bottom: 25px;
}

.card-title {

    font-family: "Space Grotesk";

    font-size: 20px;

    font-weight: 700;

    margin-bottom: 5px;
}

.card-subtitle {

    color: var(--muted);

    font-size: 14px;

    margin-bottom: 22px;
}


/* =========================================================
   DASHBOARD GRID
   ========================================================= */

.dashboard-grid {

    display: grid;

    grid-template-columns: 1.2fr .8fr;

    gap: 22px;
}


/* =========================================================
   WORKFLOW
   ========================================================= */

.workflow {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 7px;
}

.step {

    flex: 1;

    text-align: center;
}

.step-icon {

    width: 48px;

    height: 48px;

    border-radius: 50%;

    margin: auto;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #efedff;

    font-size: 20px;
}

.step span {

    display: block;

    margin-top: 9px;

    font-size: 12px;

    font-weight: 600;
}

.workflow-line {

    height: 2px;

    flex: .35;

    background: #dfe2eb;
}


/* =========================================================
   FORM
   ========================================================= */

.form-grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 20px;
}

.form-group {

    display: flex;

    flex-direction: column;

    gap: 8px;
}

.form-group.full {

    grid-column: 1 / -1;
}

.form-group label {

    font-size: 15px;

    font-weight: 700;
}

.form-group input,
.form-group select {

    width: 100%;

    border: 1px solid #dce1eb;

    border-radius: 11px;

    padding: 14px 15px;

    font-size: 16px;

    outline: none;

    background: #fbfcfe;

    transition: .2s;
}

.form-group input:focus,
.form-group select:focus {

    border-color: var(--primary);

    box-shadow:
        0 0 0 3px rgba(101,87,232,.10);

    background: white;
}

.form-help {

    color: #8a92a5;

    font-size: 12px;
}

.submit-btn {

    border: none;

    background:
        linear-gradient(
            135deg,
            #6959e8,
            #5141d0
        );

    color: white;

    padding: 16px 26px;

    border-radius: 12px;

    font-size: 17px;

    font-weight: 700;

    margin-top: 25px;

    box-shadow:
        0 8px 18px rgba(90,73,213,.25);
}

.submit-btn:hover {

    transform: translateY(-1px);
}


/* =========================================================
   AI RESULT
   ========================================================= */

.result {

    display: none;

    margin-top: 25px;

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid var(--border);
}

.result.show {

    display: block;
}

.result-header {

    padding: 22px 25px;

    background: #171f39;

    color: white;
}

.result-header h3 {

    font-family: "Space Grotesk";

    font-size: 21px;
}

.result-header p {

    color: #aeb7ce;

    margin-top: 5px;

    font-size: 14px;
}

.result-body {

    padding: 25px;

    background: white;
}

.score-box {

    display: flex;

    align-items: center;

    gap: 20px;

    margin-bottom: 22px;
}

.score-circle {

    width: 90px;

    height: 90px;

    border-radius: 50%;

    background: #efedff;

    color: #5748d7;

    display: flex;

    align-items: center;

    justify-content: center;

    font-family: "Space Grotesk";

    font-size: 26px;

    font-weight: 700;
}

.priority-badge {

    display: inline-block;

    padding: 7px 13px;

    border-radius: 30px;

    font-size: 13px;

    font-weight: 800;

    margin-top: 8px;
}

.priority-critical {

    background: #ffe5e5;

    color: #d94747;
}

.priority-high {

    background: #fff0dd;

    color: #d17c20;
}

.priority-medium {

    background: #eeeaff;

    color: #5e4ed3;
}

.priority-low {

    background: #e4f7ed;

    color: #21925f;
}

.reason-box {

    background: #f7f8fc;

    border-radius: 13px;

    padding: 18px;

    line-height: 1.6;

    color: #4e566a;

    font-size: 15px;

    margin-bottom: 20px;
}

.ngo-box {

    border: 1px solid #ddd9ff;

    background: #f7f5ff;

    border-radius: 14px;

    padding: 20px;
}

.ngo-box h4 {

    color: #5141ce;

    font-size: 13px;

    text-transform: uppercase;

    letter-spacing: .7px;

    margin-bottom: 8px;
}

.ngo-name {

    font-family: "Space Grotesk";

    font-size: 20px;

    font-weight: 700;
}

.ngo-location {

    color: #747c90;

    margin-top: 4px;

    font-size: 14px;
}


/* =========================================================
   TABLE
   ========================================================= */

.table-wrapper {

    overflow-x: auto;
}

table {

    width: 100%;

    border-collapse: collapse;

    min-width: 900px;
}

th {

    background: #f7f8fb;

    color: #70788d;

    text-transform: uppercase;

    letter-spacing: .6px;

    font-size: 12px;

    font-weight: 700;
}

th,
td {

    padding: 16px 15px;

    text-align: left;

    border-bottom: 1px solid #edf0f4;
}

td {

    font-size: 14px;

    color: #3d4558;
}

.status-select {

    border: 1px solid #d9deea;

    background: white;

    padding: 8px 10px;

    border-radius: 8px;

    font-size: 13px;
}

.empty {

    text-align: center;

    padding: 55px;

    color: var(--muted);
}


/* =========================================================
   ABOUT / INFO
   ========================================================= */

.info-grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 20px;
}

.info-card {

    background: white;

    border: 1px solid var(--border);

    border-radius: 17px;

    padding: 25px;
}

.info-card-icon {

    font-size: 32px;

    margin-bottom: 16px;
}

.info-card h3 {

    font-family: "Space Grotesk";

    font-size: 19px;

    margin-bottom: 9px;
}

.info-card p {

    color: var(--muted);

    line-height: 1.6;

    font-size: 14px;
}


/* =========================================================
   TOAST
   ========================================================= */

.toast {

    position: fixed;

    right: 25px;

    bottom: 25px;

    background: #171f39;

    color: white;

    padding: 16px 20px;

    border-radius: 12px;

    box-shadow:
        0 10px 30px rgba(0,0,0,.2);

    display: none;

    z-index: 100;

    font-size: 14px;
}

.toast.show {

    display: block;

    animation: fadeIn .25s ease;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media(max-width: 1100px) {

    .metrics {

        grid-template-columns:
            repeat(2, 1fr);
    }

    .dashboard-grid {

        grid-template-columns: 1fr;
    }

    .info-grid {

        grid-template-columns: 1fr;
    }
}

@media(max-width: 800px) {

    .sidebar {

        position: relative;

        width: 100%;

        min-height: auto;
    }

    .sidebar-bottom {

        display: none;
    }

    .app {

        display: block;
    }

    .main {

        margin-left: 0;

        width: 100%;

        padding: 25px 18px 50px;
    }

    .form-grid {

        grid-template-columns: 1fr;
    }

    .form-group.full {

        grid-column: auto;
    }

    .hero {

        padding: 25px;
    }

    .hero-icon {

        display: none;
    }

    .hero h2 {

        font-size: 25px;
    }

    .page-title {

        font-size: 28px;
    }
}

@media(max-width: 500px) {

    .metrics {

        grid-template-columns: 1fr;
    }

    .topbar {

        align-items: flex-start;

        flex-direction: column;
    }

    .workflow {

        flex-direction: column;
    }

    .workflow-line {

        width: 2px;

        height: 20px;

        flex: none;
    }
}

</style>

</head>


<body>

<div class="app">


<!-- ======================================================
     SIDEBAR
====================================================== -->

<aside class="sidebar">

    <div class="logo">

        <div class="logo-icon">
            🍲
        </div>

        <div>

            <div class="logo-title">
                Food Rescue AI
            </div>

            <div class="logo-subtitle">
                Smart Food Redistribution
            </div>

        </div>

    </div>


    <div class="menu-title">
        Main Menu
    </div>


    <nav class="nav">

        <button
            id="nav-dashboard"
            class="active"
            onclick="showPage('dashboard')"
        >
            <span>📊</span>
            Dashboard
        </button>


        <button
            id="nav-donation"
            onclick="showPage('donation')"
        >
            <span>➕</span>
            New Donation
        </button>


        <button
            id="nav-records"
            onclick="showPage('records')"
        >
            <span>📋</span>
            Donation Records
        </button>


        <button
            id="nav-about"
            onclick="showPage('about')"
        >
            <span>🤖</span>
            How It Works
        </button>

    </nav>


    <div class="sidebar-bottom">

        <strong>🌱 Every Meal Matters</strong>

        <span>
            Turn surplus food into meaningful impact.
        </span>

    </div>

</aside>


<!-- ======================================================
     MAIN
====================================================== -->

<main class="main">


<!-- ======================================================
     DASHBOARD
====================================================== -->

<section
    id="dashboard"
    class="page active"
>

    <div class="topbar">

        <div>

            <div class="page-title">
                Dashboard
            </div>

            <div class="page-subtitle">
                Monitor food donations, urgency and community impact.
            </div>

        </div>

        <div class="date-box">
            📅 <span id="today"></span>
        </div>

    </div>


    <div class="hero">

        <div>

            <h2>
                Make Every Meal Count 🌱
            </h2>

            <p>
                Food Rescue AI analyzes donated food,
                determines redistribution urgency and
                recommends the most suitable NGO for
                faster community delivery.
            </p>

            <button onclick="showPage('donation')">
                + Create New Donation
            </button>

        </div>

        <div class="hero-icon">
            🍲
        </div>

    </div>


    <!-- METRICS -->

    <div class="metrics">

        <div class="metric">

            <div class="metric-top">

                <div class="metric-icon">
                    🍱
                </div>

            </div>

            <div class="metric-label">
                Total Donations
            </div>

            <div
                class="metric-value"
                id="totalDonations"
            >
                0
            </div>

        </div>


        <div class="metric">

            <div class="metric-top">

                <div class="metric-icon">
                    🚚
                </div>

            </div>

            <div class="metric-label">
                Delivered
            </div>

            <div
                class="metric-value"
                id="deliveredDonations"
            >
                0
            </div>

        </div>


        <div class="metric">

            <div class="metric-top">

                <div class="metric-icon">
                    ⏳
                </div>

            </div>

            <div class="metric-label">
                Pending
            </div>

            <div
                class="metric-value"
                id="pendingDonations"
            >
                0
            </div>

        </div>


        <div class="metric">

            <div class="metric-top">

                <div class="metric-icon">
                    🚨
                </div>

            </div>

            <div class="metric-label">
                Critical Donations
            </div>

            <div
                class="metric-value"
                id="criticalDonations"
            >
                0
            </div>

        </div>

    </div>


    <!-- DASHBOARD GRID -->

    <div class="dashboard-grid">


        <div class="card">

            <div class="card-title">
                Donation Rescue Workflow
            </div>

            <div class="card-subtitle">
                From surplus food to community impact.
            </div>


            <div class="workflow">

                <div class="step">

                    <div class="step-icon">
                        🍱
                    </div>

                    <span>
                        Donation
                    </span>

                </div>

                <div class="workflow-line"></div>


                <div class="step">

                    <div class="step-icon">
                        🧠
                    </div>

                    <span>
                        AI Analysis
                    </span>

                </div>

                <div class="workflow-line"></div>


                <div class="step">

                    <div class="step-icon">
                        🎯
                    </div>

                    <span>
                        Priority
                    </span>

                </div>

                <div class="workflow-line"></div>


                <div class="step">

                    <div class="step-icon">
                        🤝
                    </div>

                    <span>
                        NGO Match
                    </span>

                </div>

                <div class="workflow-line"></div>


                <div class="step">

                    <div class="step-icon">
                        🚚
                    </div>

                    <span>
                        Delivery
                    </span>

                </div>

            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Community Impact
            </div>

            <div class="card-subtitle">
                Total food quantity rescued.
            </div>

            <div
                style="
                    font-family:'Space Grotesk';
                    font-size:42px;
                    font-weight:700;
                    margin-top:20px;
                "
                id="foodQuantity"
            >
                0
            </div>

            <div
                style="
                    color:#7b8397;
                    font-size:14px;
                    margin-top:5px;
                "
            >
                units of food recorded
            </div>

        </div>

    </div>

</section>


<!-- ======================================================
     NEW DONATION
====================================================== -->

<section
    id="donation"
    class="page"
>

    <div class="topbar">

        <div>

            <div class="page-title">
                Create Donation
            </div>

            <div class="page-subtitle">
                Enter surplus food details for AI-powered prioritization.
            </div>

        </div>

    </div>


    <div class="card">

        <div class="card-title">
            🥗 Food Donation Details
        </div>

        <div class="card-subtitle">
            Provide accurate information so the system can determine urgency and recommend an NGO.
        </div>


        <form id="donationForm">


            <div class="form-grid">


                <div class="form-group">

                    <label>
                        Donor Name
                    </label>

                    <input
                        id="donor_name"
                        type="text"
                        placeholder="Example: ABC Restaurant"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Food Name
                    </label>

                    <input
                        id="food_name"
                        type="text"
                        placeholder="Example: Vegetable Biryani"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Food Type
                    </label>

                    <select
                        id="food_type"
                        required
                    >

                        <option value="">
                            Select food type
                        </option>

                        <option value="cooked">
                            Cooked Food
                        </option>

                        <option value="vegetarian">
                            Vegetarian
                        </option>

                        <option value="bakery">
                            Bakery
                        </option>

                        <option value="fruits">
                            Fruits
                        </option>

                        <option value="rice">
                            Rice / Grains
                        </option>

                        <option value="mixed">
                            Mixed Food
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Quantity
                    </label>

                    <input
                        id="quantity"
                        type="number"
                        min="1"
                        placeholder="Example: 50"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Unit
                    </label>

                    <select
                        id="unit"
                        required
                    >

                        <option value="Meals">
                            Meals
                        </option>

                        <option value="Kg">
                            Kg
                        </option>

                        <option value="Packets">
                            Packets
                        </option>

                        <option value="Boxes">
                            Boxes
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Freshness Remaining
                    </label>

                    <input
                        id="freshness_hours"
                        type="number"
                        min="0"
                        placeholder="Example: 4"
                        required
                    >

                    <span class="form-help">
                        Approximate number of hours the food remains suitable for redistribution.
                    </span>

                </div>


                <div class="form-group full">

                    <label>
                        Pickup Location
                    </label>

                    <input
                        id="pickup_location"
                        type="text"
                        placeholder="Example: Kukatpally, Hyderabad"
                        required
                    >

                </div>


            </div>


            <button
                class="submit-btn"
                type="submit"
            >
                🤖 Analyze & Create Donation
            </button>

        </form>


        <!-- AI RESULT -->

        <div
            id="result"
            class="result"
        >

            <div class="result-header">

                <h3>
                    ✨ AI Donation Analysis Complete
                </h3>

                <p>
                    Your donation has been evaluated for urgency and NGO matching.
                </p>

            </div>


            <div class="result-body">


                <div class="score-box">

                    <div
                        class="score-circle"
                        id="score"
                    >
                        0
                    </div>

                    <div>

                        <strong>
                            Priority Score
                        </strong>

                        <br>

                        <span
                            id="level"
                            class="priority-badge"
                        >
                            -
                        </span>

                    </div>

                </div>


                <div class="reason-box">

                    <strong>
                        🧠 Why this priority?
                    </strong>

                    <p
                        id="reason"
                        style="margin-top:8px;"
                    ></p>

                </div>


                <div class="ngo-box">

                    <h4>
                        Recommended NGO
                    </h4>

                    <div
                        class="ngo-name"
                        id="ngoName"
                    ></div>

                    <div
                        class="ngo-location"
                        id="ngoLocation"
                    ></div>

                </div>


            </div>

        </div>

    </div>

</section>


<!-- ======================================================
     RECORDS
====================================================== -->

<section
    id="records"
    class="page"
>

    <div class="topbar">

        <div>

            <div class="page-title">
                Donation Records
            </div>

            <div class="page-subtitle">
                Track every donation and its delivery progress.
            </div>

        </div>

        <button
            class="submit-btn"
            style="margin-top:0;"
            onclick="loadRecords()"
        >
            🔄 Refresh
        </button>

    </div>


    <div class="card">

        <div class="card-title">
            📋 Donation History
        </div>

        <div class="card-subtitle">
            Manage pickup, transportation and delivery status.
        </div>


        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>ID</th>

                        <th>Food</th>

                        <th>Donor</th>

                        <th>Quantity</th>

                        <th>Priority</th>

                        <th>NGO</th>

                        <th>Status</th>

                        <th>Date</th>

                    </tr>

                </thead>

                <tbody id="recordsBody">

                </tbody>

            </table>

        </div>

    </div>

</section>


<!-- ======================================================
     ABOUT
====================================================== -->

<section
    id="about"
    class="page"
>

    <div class="topbar">

        <div>

            <div class="page-title">
                How Food Rescue AI Works
            </div>

            <div class="page-subtitle">
                A smart workflow for reducing food waste.
            </div>

        </div>

    </div>


    <div class="info-grid">


        <div class="info-card">

            <div class="info-card-icon">
                📝
            </div>

            <h3>
                1. Create Donation
            </h3>

            <p>
                Donors enter information such as food type,
                quantity, freshness and pickup location.
            </p>

        </div>


        <div class="info-card">

            <div class="info-card-icon">
                🧠
            </div>

            <h3>
                2. AI Priority Analysis
            </h3>

            <p>
                The system evaluates freshness, quantity and
                food type to calculate a priority score from 0 to 100.
            </p>

        </div>


        <div class="info-card">

            <div class="info-card-icon">
                🎯
            </div>

            <h3>
                3. Priority Level
            </h3>

            <p>
                Donations are classified as Critical, High,
                Medium or Low based on their urgency.
            </p>

        </div>


        <div class="info-card">

            <div class="info-card-icon">
                🤝
            </div>

            <h3>
                4. NGO Recommendation
            </h3>

            <p>
                The system recommends an NGO based on food
                compatibility, capacity and location.
            </p>

        </div>


        <div class="info-card">

            <div class="info-card-icon">
                🚚
            </div>

            <h3>
                5. Delivery Tracking
            </h3>

            <p>
                Donation status can progress from Pending Pickup
                through transportation to Delivered and Completed.
            </p>

        </div>


        <div class="info-card">

            <div class="info-card-icon">
                🌱
            </div>

            <h3>
                6. Social Impact
            </h3>

            <p>
                The dashboard tracks donations, deliveries,
                critical food and total rescued quantity.
            </p>

        </div>

    </div>

</section>


</main>

</div>


<div
    id="toast"
    class="toast"
></div>


<script>

/* =========================================================
   DATE
========================================================= */

document.getElementById("today").textContent =
    new Date().toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );


/* =========================================================
   PAGE NAVIGATION
========================================================= */

function showPage(pageName) {

    document.querySelectorAll(".page")
        .forEach(function(page) {

            page.classList.remove("active");

        });


    document.querySelectorAll(".nav button")
        .forEach(function(button) {

            button.classList.remove("active");

        });


    const selectedPage =
        document.getElementById(pageName);

    if (selectedPage) {

        selectedPage.classList.add("active");

    }


    const selectedNav =
        document.getElementById(
            "nav-" + pageName
        );

    if (selectedNav) {

        selectedNav.classList.add("active");

    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });


    if (pageName === "dashboard") {

        loadMetrics();

    }


    if (pageName === "records") {

        loadRecords();

    }

}


/* =========================================================
   TOAST
========================================================= */

function showToast(message) {

    const toast =
        document.getElementById("toast");

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(function() {

        toast.classList.remove("show");

    }, 3000);

}


/* =========================================================
   LOAD METRICS
========================================================= */

async function loadMetrics() {

    try {

        const response =
            await fetch("/api/metrics");

        const data =
            await response.json();


        document.getElementById(
            "totalDonations"
        ).textContent =
            data.total_donations;


        document.getElementById(
            "deliveredDonations"
        ).textContent =
            data.delivered_donations;


        document.getElementById(
            "pendingDonations"
        ).textContent =
            data.pending_donations;


        document.getElementById(
            "criticalDonations"
        ).textContent =
            data.critical_donations;


        document.getElementById(
            "foodQuantity"
        ).textContent =
            data.food_quantity;

    }

    catch (error) {

        console.error(error);

    }

}


/* =========================================================
   CREATE DONATION
========================================================= */

document.getElementById(
    "donationForm"
).addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const button =
            this.querySelector(
                ".submit-btn"
            );


        button.disabled = true;

        button.textContent =
            "⏳ Analyzing Donation...";


        const payload = {

            donor_name:
                document.getElementById(
                    "donor_name"
                ).value,

            food_name:
                document.getElementById(
                    "food_name"
                ).value,

            food_type:
                document.getElementById(
                    "food_type"
                ).value,

            quantity:
                Number(
                    document.getElementById(
                        "quantity"
                    ).value
                ),

            unit:
                document.getElementById(
                    "unit"
                ).value,

            freshness_hours:
                Number(
                    document.getElementById(
                        "freshness_hours"
                    ).value
                ),

            pickup_location:
                document.getElementById(
                    "pickup_location"
                ).value

        };


        try {

            const response =
                await fetch(
                    "/api/donations",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Unable to create donation."
                );

            }


            /* Show result */

            document.getElementById(
                "result"
            ).classList.add("show");


            document.getElementById(
                "score"
            ).textContent =
                data.priority_score;


            const level =
                document.getElementById(
                    "level"
                );


            level.textContent =
                data.priority_level;


            level.className =
                "priority-badge priority-" +
                data.priority_level.toLowerCase();


            document.getElementById(
                "reason"
            ).textContent =
                data.priority_reason;


            document.getElementById(
                "ngoName"
            ).textContent =
                data.ngo.name;


            document.getElementById(
                "ngoLocation"
            ).textContent =
                "📍 " +
                data.ngo.location;


            showToast(
                "Donation created successfully! 🎉"
            );


            loadMetrics();


            document.getElementById(
                "donationForm"
            ).reset();

        }

        catch (error) {

            showToast(
                "Error: " + error.message
            );

        }

        finally {

            button.disabled = false;

            button.textContent =
                "🤖 Analyze & Create Donation";

        }

    }
);


/* =========================================================
   LOAD RECORDS
========================================================= */

async function loadRecords() {

    const body =
        document.getElementById(
            "recordsBody"
        );


    body.innerHTML = `
        <tr>
            <td
                colspan="8"
                class="empty"
            >
                Loading donation records...
            </td>
        </tr>
    `;


    try {

        const response =
            await fetch(
                "/api/donations"
            );

        const records =
            await response.json();


        if (records.length === 0) {

            body.innerHTML = `
                <tr>
                    <td
                        colspan="8"
                        class="empty"
                    >
                        🍱 No donations yet.
                        Create your first donation!
                    </td>
                </tr>
            `;

            return;

        }


        body.innerHTML =
            records.map(function(item) {

                const priorityClass =
                    item.priority_level.toLowerCase();


                return `

                    <tr>

                        <td>
                            #${item.id}
                        </td>

                        <td>
                            <strong>
                                ${escapeHtml(item.food_name)}
                            </strong>
                            <br>
                            <span
                                style="
                                    color:#8a92a5;
                                    font-size:12px;
                                "
                            >
                                ${escapeHtml(item.food_type)}
                            </span>
                        </td>

                        <td>
                            ${escapeHtml(item.donor_name)}
                        </td>

                        <td>
                            ${item.quantity}
                            ${escapeHtml(item.unit)}
                        </td>

                        <td>

                            <span
                                class="
                                    priority-badge
                                    priority-${priorityClass}
                                "
                            >
                                ${item.priority_level}
                                ·
                                ${item.priority_score}
                            </span>

                        </td>

                        <td>

                            ${escapeHtml(item.ngo_name)}

                            <br>

                            <span
                                style="
                                    color:#8a92a5;
                                    font-size:12px;
                                "
                            >
                                📍 ${escapeHtml(item.ngo_location)}
                            </span>

                        </td>

                        <td>

                            <select
                                class="status-select"
                                onchange="
                                    updateStatus(
                                        ${item.id},
                                        this.value
                                    )
                                "
                            >

                                ${statusOptions(
                                    item.status
                                )}

                            </select>

                        </td>

                        <td>
                            ${item.created_at}
                        </td>

                    </tr>

                `;

            }).join("");

    }

    catch (error) {

        body.innerHTML = `
            <tr>
                <td
                    colspan="8"
                    class="empty"
                >
                    Unable to load records.
                </td>
            </tr>
        `;

    }

}


/* =========================================================
   STATUS OPTIONS
========================================================= */

function statusOptions(current) {

    const statuses = [

        "Pending Pickup",
        "Picked Up",
        "In Transit",
        "Delivered",
        "Completed"

    ];


    return statuses.map(function(status) {

        return `
            <option
                value="${status}"
                ${status === current ? "selected" : ""}
            >
                ${status}
            </option>
        `;

    }).join("");

}


/* =========================================================
   UPDATE STATUS
========================================================= */

async function updateStatus(
    id,
    status
) {

    try {

        const response =
            await fetch(
                `/api/donations/${id}/status`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            status: status
                        })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Status update failed."
            );

        }


        showToast(
            "Donation status updated successfully."
        );


        loadMetrics();

    }

    catch (error) {

        showToast(
            "Error: " + error.message
        );

        loadRecords();

    }

}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";

    }

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}


/* =========================================================
   INITIAL LOAD
========================================================= */

loadMetrics();

</script>

</body>

</html>
"""


# ============================================================
# FRONTEND ROUTE
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


# ============================================================
# RENDER ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
