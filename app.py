from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import os

# ============================================================
# FOOD RESCUE AI
# Single-file FastAPI prototype
# ============================================================

app = FastAPI(
    title="Food Rescue AI",
    description="AI-powered food donation prioritization and NGO recommendation",
    version="1.0.0"
)

# ============================================================
# DATABASE
# ============================================================

DB_FILE = "food_rescue.db"


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
    }
]

# ============================================================
# DATA MODEL
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

    # -------------------------
    # Freshness / urgency
    # -------------------------

    if data.freshness_hours <= 2:
        score += 40
        reasons.append(
            "The food is extremely time-sensitive"
        )

    elif data.freshness_hours <= 6:
        score += 30
        reasons.append(
            "The food should be redistributed soon"
        )

    elif data.freshness_hours <= 12:
        score += 20
        reasons.append(
            "The food has moderate redistribution urgency"
        )

    else:
        score += 10
        reasons.append(
            "The food has relatively longer usability"
        )

    # -------------------------
    # Quantity
    # -------------------------

    if data.quantity >= 100:
        score += 30
        reasons.append(
            "The large quantity can support many beneficiaries"
        )

    elif data.quantity >= 50:
        score += 20
        reasons.append(
            "The donation contains a useful quantity of food"
        )

    elif data.quantity >= 20:
        score += 12
        reasons.append(
            "The donation can support a community distribution"
        )

    else:
        score += 5

    # -------------------------
    # Food type
    # -------------------------

    food_type = data.food_type.lower()

    if food_type == "cooked":
        score += 20
        reasons.append(
            "Cooked food has higher redistribution urgency"
        )

    elif food_type == "bakery":
        score += 15
        reasons.append(
            "Bakery items can be redistributed quickly"
        )

    elif food_type == "fruits":
        score += 12
        reasons.append(
            "Fresh produce benefits from quick redistribution"
        )

    elif food_type == "vegetarian":
        score += 15
        reasons.append(
            "Vegetarian food is suitable for broad distribution"
        )

    else:
        score += 8

    score = min(score, 100)

    if score >= 80:
        level = "CRITICAL"

    elif score >= 60:
        level = "HIGH"

    elif score >= 40:
        level = "MEDIUM"

    else:
        level = "LOW"

    reason = ". ".join(reasons) + "."

    return score, level, reason


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

        # Location match
        if ngo["location"].lower() in location:
            score += 20

        if score > best_score:
            best_score = score
            best_ngo = ngo

    return best_ngo


# ============================================================
# MAIN HTML APPLICATION
# ============================================================


HTML = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

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
    --bg: #f5f7fb;
    --dark: #11182d;
    --dark2: #1b2440;
    --purple: #6757e8;
    --purple2: #5040d0;
    --text: #171c2f;
    --muted: #7d8497;
    --border: #e5e8f0;
    --green: #20b574;
    --orange: #f29a3f;
    --red: #ef5b5b;
    --white: #ffffff;
}

body {
    font-family: "DM Sans", sans-serif;
    background: var(--bg);
    color: var(--text);
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
    width: 245px;
    min-height: 100vh;
    background: var(--dark);
    color: white;
    padding: 25px 17px;
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
}

.logo {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 0 10px 35px;
}

.logo-icon {
    width: 43px;
    height: 43px;
    border-radius: 12px;
    background: linear-gradient(
        135deg,
        #7768ef,
        #4d3bc3
    );
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 22px;
}

.logo h2 {
    font-family: "Space Grotesk";
    font-size: 17px;
}

.logo small {
    color: #858ea9;
    font-size: 10px;
}

.nav {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.nav button {
    border: none;
    background: transparent;
    color: #8e97b1;
    padding: 13px;
    border-radius: 10px;
    text-align: left;
    font-size: 13px;
}

.nav button:hover,
.nav button.active {
    background: var(--dark2);
    color: white;
}

.sidebar-bottom {
    margin-top: auto;
}

.ai-status {
    padding: 13px;
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 11px;
    display: flex;
    gap: 10px;
    align-items: center;
}

.status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #34d88d;
    box-shadow: 0 0 10px #34d88d;
}

.ai-status strong {
    display: block;
    font-size: 11px;
}

.ai-status span {
    color: #77819d;
    font-size: 9px;
}


/* =========================================================
   MAIN
   ========================================================= */

.main {
    margin-left: 245px;
    width: calc(100% - 245px);
    padding: 28px 35px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.eyebrow {
    color: var(--purple);
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 5px;
}

.topbar h1 {
    font-family: "Space Grotesk";
    font-size: 27px;
}

.top-actions {
    display: flex;
    align-items: center;
    gap: 15px;
}

.live {
    color: var(--muted);
    font-size: 11px;
}

.live span {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green);
    margin-right: 5px;
}

.primary-btn {
    border: none;
    background: var(--purple);
    color: white;
    padding: 11px 16px;
    border-radius: 8px;
    font-weight: 600;
}

.primary-btn:hover {
    background: var(--purple2);
}


/* =========================================================
   SECTIONS
   ========================================================= */

.section {
    display: none;
}

.section.active {
    display: block;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    min-height: 280px;
    border-radius: 19px;
    padding: 38px 42px;
    color: white;
    background:
        radial-gradient(
            circle at 85% 25%,
            rgba(117,102,240,.45),
            transparent 30%
        ),
        linear-gradient(
            120deg,
            #161d38,
            #342d69
        );
    display: flex;
    overflow: hidden;
}

.hero-left {
    width: 58%;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,.08);
    padding: 6px 10px;
    border-radius: 20px;
    font-size: 8px;
    letter-spacing: 1.2px;
    margin-bottom: 15px;
}

.hero h2 {
    font-family: "Space Grotesk";
    font-size: 34px;
    line-height: 1.15;
}

.hero h2 span {
    color: #aaa1ff;
}

.hero p {
    color: #b9bfd2;
    font-size: 12px;
    line-height: 1.7;
    max-width: 520px;
    margin: 13px 0 20px;
}

.hero-btn {
    border: none;
    background: white;
    color: #393071;
    padding: 11px 17px;
    border-radius: 8px;
    font-weight: 600;
}

.hero-right {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.food-card {
    width: 235px;
    padding: 15px;
    border-radius: 15px;
    background: rgba(255,255,255,.09);
    border: 1px solid rgba(255,255,255,.15);
    backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    gap: 11px;
}

.food-icon {
    width: 43px;
    height: 43px;
    background: white;
    border-radius: 11px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 21px;
}

.food-card strong {
    display: block;
    font-size: 12px;
}

.food-card small {
    color: #aab1c7;
    font-size: 9px;
}

.food-score {
    margin-left: auto;
    font-size: 18px;
    color: #83e6b5;
    font-weight: 700;
}


/* =========================================================
   METRICS
   ========================================================= */

.metrics {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 14px;
    margin: 19px 0;
}

.metric {
    background: white;
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 18px;
}

.metric span {
    color: var(--muted);
    font-size: 10px;
}

.metric strong {
    display: block;
    margin-top: 5px;
    font-family: "Space Grotesk";
    font-size: 24px;
}


/* =========================================================
   DASHBOARD PANELS
   ========================================================= */

.dashboard-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 16px;
}

.panel {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px;
}

.panel h3 {
    font-family: "Space Grotesk";
    font-size: 16px;
}

.workflow {
    display: flex;
    align-items: center;
    margin-top: 25px;
}

.step {
    text-align: center;
}

.step-circle {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #eeeaff;
    color: var(--purple);
    display: flex;
    justify-content: center;
    align-items: center;
    margin: auto;
    font-size: 10px;
    font-weight: 700;
}

.step span {
    display: block;
    color: #747c90;
    font-size: 9px;
    margin-top: 7px;
}

.workflow-line {
    flex: 1;
    height: 1px;
    background: #dfe2ea;
    margin: 0 8px 20px;
}

.impact {
    color: white;
    background: linear-gradient(
        145deg,
        #6757e8,
        #4031aa
    );
}

.impact .eyebrow {
    color: #bdb5ff;
}

.impact-number {
    font-family: "Space Grotesk";
    font-size: 46px;
    font-weight: 700;
    margin: 12px 0 5px;
}

.impact p {
    color: #c5c7df;
    font-size: 11px;
    line-height: 1.6;
}


/* =========================================================
   FORM
   ========================================================= */

.heading {
    margin-bottom: 22px;
}

.heading h2 {
    font-family: "Space Grotesk";
    font-size: 28px;
}

.heading p:last-child {
    color: var(--muted);
    font-size: 12px;
    margin-top: 6px;
}

.donation-grid {
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 18px;
}

.form-card,
.ai-card,
.table-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 24px;
}

.row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 13px;
}

.field {
    margin-bottom: 15px;
}

.field label {
    display: block;
    font-size: 10px;
    font-weight: 600;
    color: #52596d;
    margin-bottom: 6px;
}

.field input,
.field select {
    width: 100%;
    border: 1px solid #dfe2e9;
    background: #fafbfd;
    border-radius: 8px;
    padding: 11px;
    font-size: 11px;
    outline: none;
}

.field input:focus,
.field select:focus {
    border-color: var(--purple);
    background: white;
}

.analyze {
    width: 100%;
    border: none;
    background: var(--purple);
    color: white;
    padding: 13px;
    border-radius: 8px;
    font-weight: 600;
    margin-top: 3px;
}

.analyze:hover {
    background: var(--purple2);
}


/* =========================================================
   AI RESULT
   ========================================================= */

.ai-card {
    background:
        linear-gradient(
            150deg,
            #171d35,
            #282450
        );
    color: white;
}

.ai-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ai-title span {
    color: #a9a0ff;
    font-size: 8px;
    letter-spacing: 1.2px;
}

.level {
    padding: 5px 8px;
    border-radius: 20px;
    background: rgba(255,255,255,.1);
    font-size: 8px;
    font-weight: 700;
}

.score-area {
    display: flex;
    gap: 17px;
    align-items: center;
    margin: 25px 0 18px;
}

.score-circle {
    width: 95px;
    height: 95px;
    border-radius: 50%;
    border: 8px solid var(--purple);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}

.score-circle strong {
    font-family: "Space Grotesk";
    font-size: 28px;
}

.score-circle small {
    color: #929ab4;
    font-size: 8px;
}

.score-area > div:last-child small {
    color: #8e96b1;
    font-size: 8px;
}

.score-area h3 {
    margin-top: 5px;
    font-size: 16px;
}

.reason {
    background: rgba(255,255,255,.06);
    border-radius: 9px;
    padding: 13px;
    margin-bottom: 14px;
}

.reason label {
    color: #aaa1ff;
    font-size: 8px;
    letter-spacing: 1px;
}

.reason p {
    color: #c1c6d7;
    font-size: 10px;
    line-height: 1.7;
    margin-top: 6px;
}

.ngo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 13px;
    background: rgba(255,255,255,.06);
    border-radius: 9px;
}

.ngo-icon {
    width: 38px;
    height: 38px;
    border-radius: 9px;
    background: #eeeaff;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ngo small,
.ngo strong,
.ngo span {
    display: block;
}

.ngo small {
    color: #8f97b0;
    font-size: 7px;
}

.ngo strong {
    font-size: 12px;
    margin: 3px 0;
}

.ngo span {
    color: #9da5bb;
    font-size: 9px;
}

.success {
    background: rgba(32,181,116,.14);
    color: #7be3b1;
    padding: 10px;
    text-align: center;
    border-radius: 7px;
    font-size: 9px;
    margin-top: 13px;
}

.hidden {
    display: none !important;
}


/* =========================================================
   RECORDS
   ========================================================= */

.table-card {
    padding: 0;
    overflow: hidden;
}

.table-head {
    padding: 18px;
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
}

.refresh {
    border: 1px solid var(--border);
    background: white;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 9px;
}

.table-wrapper {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 14px 16px;
    text-align: left;
    border-bottom: 1px solid #eef0f4;
    font-size: 10px;
}

th {
    color: #858ca0;
    font-size: 8px;
    text-transform: uppercase;
}

.priority,
.status {
    padding: 4px 7px;
    border-radius: 20px;
    font-size: 8px;
    font-weight: 700;
}

.critical {
    background: #ffe5e5;
    color: #df4b4b;
}

.high {
    background: #fff0df;
    color: #d78322;
}

.medium {
    background: #eeeaff;
    color: #6657d8;
}

.low {
    background: #e6f7ee;
    color: #219766;
}

.status {
    background: #eef0f5;
    color: #687086;
}

.status-select {
    border: 1px solid #dddfe7;
    border-radius: 5px;
    padding: 4px;
    font-size: 8px;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media(max-width: 1000px) {

    .sidebar {
        width: 200px;
    }

    .main {
        margin-left: 200px;
        width: calc(100% - 200px);
        padding: 22px;
    }

    .metrics {
        grid-template-columns: 1fr 1fr;
    }

    .donation-grid {
        grid-template-columns: 1fr;
    }
}

@media(max-width: 700px) {

    .app {
        display: block;
    }

    .sidebar {
        position: relative;
        width: 100%;
        min-height: auto;
    }

    .main {
        margin-left: 0;
        width: 100%;
    }

    .topbar {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }

    .hero-left {
        width: 100%;
    }

    .hero-right {
        display: none;
    }

    .metrics,
    .dashboard-grid,
    .row {
        grid-template-columns: 1fr;
    }

    .workflow {
        flex-direction: column;
        gap: 8px;
    }

    .workflow-line {
        width: 1px;
        height: 20px;
        margin: 0;
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
            <h2>Food Rescue</h2>
            <small>AI Platform</small>
        </div>

    </div>


    <div class="nav">

        <button
            class="active"
            onclick="showPage('dashboard',this)"
        >
            ◈ &nbsp; Dashboard
        </button>

        <button
            onclick="showPage('donate',this)"
        >
            ＋ &nbsp; Create Donation
        </button>

        <button
            onclick="showPage('records',this)"
        >
            ◫ &nbsp; Donation Records
        </button>

    </div>


    <div class="sidebar-bottom">

        <div class="ai-status">

            <div class="status-dot"></div>

            <div>
                <strong>AI Engine</strong>
                <span>Operational</span>
            </div>

        </div>

    </div>

</aside>


<!-- ======================================================
     MAIN
     ====================================================== -->

<main class="main">


<header class="topbar">

    <div>

        <div class="eyebrow">
            COMMUNITY FOOD NETWORK
        </div>

        <h1 id="pageTitle">
            Food Rescue Dashboard
        </h1>

    </div>


    <div class="top-actions">

        <div class="live">
            <span></span>
            System Live
        </div>

        <button
            class="primary-btn"
            onclick="openDonation()"
        >
            + New Donation
        </button>

    </div>

</header>


<!-- ======================================================
     DASHBOARD
     ====================================================== -->

<section
    id="dashboard"
    class="section active"
>

<div class="hero">

    <div class="hero-left">

        <div class="hero-tag">
            AI-POWERED FOOD REDISTRIBUTION
        </div>

        <h2>
            Turn surplus food into
            <span>community impact.</span>
        </h2>

        <p>
            Analyze food urgency, prioritize donations,
            and connect surplus food with suitable
            community organizations.
        </p>

        <button
            class="hero-btn"
            onclick="openDonation()"
        >
            Start a Donation →
        </button>

    </div>


    <div class="hero-right">

        <div class="food-card">

            <div class="food-icon">
                🍛
            </div>

            <div>
                <strong>Fresh Meal</strong>
                <small>AI Priority Analysis</small>
            </div>

            <div class="food-score">
                92
            </div>

        </div>

    </div>

</div>


<div class="metrics">

    <div class="metric">
        <span>Total Donations</span>
        <strong id="total">0</strong>
    </div>

    <div class="metric">
        <span>Food Delivered</span>
        <strong id="delivered">0</strong>
    </div>

    <div class="metric">
        <span>Pending Pickup</span>
        <strong id="pending">0</strong>
    </div>

    <div class="metric">
        <span>Critical Donations</span>
        <strong id="critical">0</strong>
    </div>

</div>


<div class="dashboard-grid">

    <div class="panel">

        <div class="eyebrow">
            AI WORKFLOW
        </div>

        <h3>
            From Surplus Food to Community Impact
        </h3>


        <div class="workflow">

            <div class="step">

                <div class="step-circle">
                    01
                </div>

                <span>
                    Food Details
                </span>

            </div>


            <div class="workflow-line"></div>


            <div class="step">

                <div class="step-circle">
                    02
                </div>

                <span>
                    AI Priority
                </span>

            </div>


            <div class="workflow-line"></div>


            <div class="step">

                <div class="step-circle">
                    03
                </div>

                <span>
                    NGO Match
                </span>

            </div>


            <div class="workflow-line"></div>


            <div class="step">

                <div class="step-circle">
                    04
                </div>

                <span>
                    Delivery
                </span>

            </div>

        </div>

    </div>


    <div class="panel impact">

        <div class="eyebrow">
            FOOD RESCUED
        </div>

        <div
            class="impact-number"
            id="quantity"
        >
            0
        </div>

        <p>
            total units of surplus food
            registered through the platform.
        </p>

    </div>

</div>

</section>


<!-- ======================================================
     DONATION
     ====================================================== -->

<section
    id="donate"
    class="section"
>

<div class="heading">

    <div class="eyebrow">
        DONATION MANAGEMENT
    </div>

    <h2>
        Create Food Donation
    </h2>

    <p>
        Enter the food details and let the AI
        determine urgency and the best NGO match.
    </p>

</div>


<div class="donation-grid">


<div class="form-card">

<form id="donationForm">

<div class="row">

    <div class="field">

        <label>
            Donor Name
        </label>

        <input
            id="donor_name"
            placeholder="Restaurant / Hotel / Individual"
            required
        >

    </div>


    <div class="field">

        <label>
            Food Name
        </label>

        <input
            id="food_name"
            placeholder="e.g. Vegetable Biryani"
            required
        >

    </div>

</div>


<div class="row">

    <div class="field">

        <label>
            Food Type
        </label>

        <select
            id="food_type"
            required
        >

            <option value="">
                Select type
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

            <option value="mixed">
                Mixed Food
            </option>

        </select>

    </div>


    <div class="field">

        <label>
            Quantity
        </label>

        <input
            id="quantityInput"
            type="number"
            min="1"
            placeholder="e.g. 100"
            required
        >

    </div>

</div>


<div class="row">

    <div class="field">

        <label>
            Unit
        </label>

        <select id="unit">

            <option>
                Meals
            </option>

            <option>
                Kg
            </option>

            <option>
                Packets
            </option>

            <option>
                Boxes
            </option>

        </select>

    </div>


    <div class="field">

        <label>
            Usable For (Hours)
        </label>

        <input
            id="freshness_hours"
            type="number"
            min="0"
            placeholder="e.g. 4"
            required
        >

    </div>

</div>


<div class="field">

    <label>
        Pickup Location
    </label>

    <input
        id="pickup_location"
        placeholder="e.g. Madhapur, Hyderabad"
        required
    >

</div>


<button
    class="analyze"
    type="submit"
>
    ✦ Analyze & Register Donation
</button>

</form>

</div>


<!-- AI RESULT -->

<div
    id="aiCard"
    class="ai-card hidden"
>

<div class="ai-title">

    <span>
        ✦ AI ANALYSIS
    </span>

    <div
        class="level"
        id="level"
    >
        HIGH
    </div>

</div>


<div class="score-area">

    <div
        class="score-circle"
        id="scoreCircle"
    >

        <strong id="score">
            0
        </strong>

        <small>
            / 100
        </small>

    </div>


    <div>

        <small>
            PRIORITY ASSESSMENT
        </small>

        <h3>
            Donation Priority
        </h3>

    </div>

</div>


<div class="reason">

    <label>
        AI Reasoning
    </label>

    <p id="reason">
    </p>

</div>


<div class="ngo">

    <div class="ngo-icon">
        🤝
    </div>

    <div>

        <small>
            RECOMMENDED NGO
        </small>

        <strong id="ngoName">
        </strong>

        <span id="ngoLocation">
        </span>

    </div>

</div>


<div
    class="success"
    id="success"
>
    ✓ Donation successfully registered
</div>

</div>

</div>

</section>


<!-- ======================================================
     RECORDS
     ====================================================== -->

<section
    id="records"
    class="section"
>

<div class="heading">

    <div class="eyebrow">
        DONATION HISTORY
    </div>

    <h2>
        Donation Records
    </h2>

    <p>
        Track donations from registration
        to delivery.
    </p>

</div>


<div class="table-card">

<div class="table-head">

    <strong>
        Recent Donations
    </strong>

    <button
        class="refresh"
        onclick="loadRecords()"
    >
        ↻ Refresh
    </button>

</div>


<div class="table-wrapper">

<table>

<thead>

<tr>
    <th>ID</th>
    <th>Food</th>
    <th>Quantity</th>
    <th>Priority</th>
    <th>NGO</th>
    <th>Status</th>
    <th>Update</th>
</tr>

</thead>

<tbody id="recordsTable">

</tbody>

</table>

</div>

</div>

</section>


</main>

</div>


<script>


// ==========================================================
// PAGE NAVIGATION
// ==========================================================


function showPage(page, button) {

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove("active");

        });


    document
        .getElementById(page)
        .classList.add("active");


    document
        .querySelectorAll(".nav button")
        .forEach(btn => {

            btn.classList.remove("active");

        });


    button.classList.add("active");


    const titles = {

        dashboard:
            "Food Rescue Dashboard",

        donate:
            "Create Food Donation",

        records:
            "Donation Records"

    };


    document
        .getElementById("pageTitle")
        .textContent = titles[page];


    if (page === "records") {

        loadRecords();

    }

}


function openDonation() {

    const button =
        document.querySelectorAll(".nav button")[1];

    showPage("donate", button);

}


// ==========================================================
// CREATE DONATION
// ==========================================================


document
    .getElementById("donationForm")
    .addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();


            const button =
                document.querySelector(".analyze");


            button.disabled = true;

            button.textContent =
                "✦ AI is analyzing...";


            const data = {

                donor_name:
                    document
                    .getElementById("donor_name")
                    .value,

                food_name:
                    document
                    .getElementById("food_name")
                    .value,

                food_type:
                    document
                    .getElementById("food_type")
                    .value,

                quantity:
                    Number(
                        document
                        .getElementById("quantityInput")
                        .value
                    ),

                unit:
                    document
                    .getElementById("unit")
                    .value,

                freshness_hours:
                    Number(
                        document
                        .getElementById("freshness_hours")
                        .value
                    ),

                pickup_location:
                    document
                    .getElementById("pickup_location")
                    .value

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
                                JSON.stringify(data)

                        }
                    );


                const result =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.detail ||
                        "Unable to create donation"
                    );

                }


                displayAI(result);

                loadMetrics();

            }

            catch(error) {

                alert(error.message);

            }


            finally {

                button.disabled = false;

                button.textContent =
                    "✦ Analyze & Register Donation";

            }

        }
    );


// ==========================================================
// DISPLAY AI
// ==========================================================


function displayAI(result) {

    document
        .getElementById("aiCard")
        .classList.remove("hidden");


    document
        .getElementById("score")
        .textContent =
        result.priority_score;


    document
        .getElementById("level")
        .textContent =
        result.priority_level;


    document
        .getElementById("reason")
        .textContent =
        result.priority_reason;


    document
        .getElementById("ngoName")
        .textContent =
        result.recommended_ngo;


    document
        .getElementById("ngoLocation")
        .textContent =
        result.ngo_location;


    document
        .getElementById("success")
        .textContent =
        "✓ Donation #" +
        result.donation_id +
        " successfully registered";


    const circle =
        document.getElementById(
            "scoreCircle"
        );


    if (result.priority_score >= 80) {

        circle.style.borderColor =
            "#ef5b5b";

    }

    else if (result.priority_score >= 60) {

        circle.style.borderColor =
            "#f29a3f";

    }

    else {

        circle.style.borderColor =
            "#6757e8";

    }

}


// ==========================================================
// METRICS
// ==========================================================


async function loadMetrics() {

    try {

        const response =
            await fetch("/api/metrics");


        const data =
            await response.json();


        document.getElementById("total")
            .textContent =
            data.total_donations;


        document.getElementById("delivered")
            .textContent =
            data.delivered_donations;


        document.getElementById("pending")
            .textContent =
            data.pending_donations;


        document.getElementById("critical")
            .textContent =
            data.critical_donations;


        document.getElementById("quantity")
            .textContent =
            data.food_quantity;

    }

    catch(error) {

        console.error(error);

    }

}


// ==========================================================
// RECORDS
// ==========================================================


async function loadRecords() {

    const table =
        document.getElementById(
            "recordsTable"
        );


    table.innerHTML = `
        <tr>
            <td colspan="7">
                Loading...
            </td>
        </tr>
    `;


    try {

        const response =
            await fetch("/api/donations");


        const records =
            await response.json();


        if (records.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="7">
                        No donations registered yet.
                    </td>
                </tr>
            `;

            return;

        }


        table.innerHTML = "";


        records.forEach(record => {

            const priority =
                record.priority_level
                .toLowerCase();


            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    #${record.id}
                </td>

                <td>
                    ${escapeHTML(record.food_name)}
                </td>

                <td>
                    ${record.quantity}
                    ${escapeHTML(record.unit)}
                </td>

                <td>
                    <span
                        class="priority ${priority}"
                    >
                        ${record.priority_level}
                    </span>
                </td>

                <td>
                    ${escapeHTML(record.ngo_name)}
                </td>

                <td>
                    <span class="status">
                        ${escapeHTML(record.status)}
                    </span>
                </td>

                <td>

                    <select
                        class="status-select"
                        onchange="
                            updateStatus(
                                ${record.id},
                                this.value
                            )
                        "
                    >

                        <option>
                            Update
                        </option>

                        <option>
                            Pending Pickup
                        </option>

                        <option>
                            Pickup Assigned
                        </option>

                        <option>
                            Picked Up
                        </option>

                        <option>
                            Delivered
                        </option>

                        <option>
                            Completed
                        </option>

                    </select>

                </td>
            `;


            table.appendChild(row);

        });

    }

    catch(error) {

        table.innerHTML = `
            <tr>
                <td colspan="7">
                    Unable to load records.
                </td>
            </tr>
        `;

    }

}


// ==========================================================
// UPDATE STATUS
// ==========================================================


async function updateStatus(id, status) {

    if (status === "Update") {

        return;

    }


    try {

        const response =
            await fetch(
                "/api/donations/" +
                id +
                "/status",
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


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.detail ||
                "Unable to update"
            );

        }


        loadRecords();

        loadMetrics();

    }

    catch(error) {

        alert(error.message);

    }

}


// ==========================================================
// SECURITY
// ==========================================================


function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;

}


// ==========================================================
// INITIAL LOAD
// ==========================================================

loadMetrics();

</script>

</body>

</html>
"""


# ============================================================
# HOME
# ============================================================


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


# ============================================================
# HEALTH
# ============================================================


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "Food Rescue AI"
    }


# ============================================================
# ANALYZE DONATION
# ============================================================


@app.post("/api/analyze")
def analyze(data: Donation):

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero."
        )

    if data.freshness_hours < 0:
        raise HTTPException(
            status_code=400,
            detail="Freshness hours cannot be negative."
        )

    score, level, reason = analyze_food(data)

    ngo = recommend_ngo(data)

    return {
        "priority_score": score,
        "priority_level": level,
        "priority_reason": reason,
        "recommended_ngo": ngo["name"],
        "ngo_location": ngo["location"]
    }


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
            detail="Freshness hours cannot be negative."
        )

    score, level, reason = analyze_food(data)

    ngo = recommend_ngo(data)

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = get_db()

    cursor = conn.execute(
        """
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
        """,
        (
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
            created_at
        )
    )

    donation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "donation_id": donation_id,
        "priority_score": score,
        "priority_level": level,
        "priority_reason": reason,
        "recommended_ngo": ngo["name"],
        "ngo_location": ngo["location"],
        "status": "Pending Pickup"
    }


# ============================================================
# GET DONATIONS
# ============================================================


@app.get("/api/donations")
def get_donations():

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM donations
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# GET SINGLE DONATION
# ============================================================


@app.get("/api/donations/{donation_id}")
def get_donation(donation_id: int):

    conn = get_db()

    row = conn.execute(
        """
        SELECT *
        FROM donations
        WHERE id = ?
        """,
        (donation_id,)
    ).fetchone()

    conn.close()

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Donation not found."
        )

    return dict(row)


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
        "Pickup Assigned",
        "Picked Up",
        "Delivered",
        "Completed"
    ]

    if data.status not in allowed:

        raise HTTPException(
            status_code=400,
            detail="Invalid status."
        )

    conn = get_db()

    cursor = conn.execute(
        """
        UPDATE donations
        SET status = ?
        WHERE id = ?
        """,
        (
            data.status,
            donation_id
        )
    )

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

    delivered = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM donations
        WHERE status IN ('Delivered','Completed')
        """
    ).fetchone()["c"]

    pending = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM donations
        WHERE status NOT IN ('Delivered','Completed')
        """
    ).fetchone()["c"]

    critical = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM donations
        WHERE priority_level = 'CRITICAL'
        """
    ).fetchone()["c"]

    quantity = conn.execute(
        """
        SELECT COALESCE(SUM(quantity),0) AS q
        FROM donations
        """
    ).fetchone()["q"]

    conn.close()

    return {
        "total_donations": total,
        "delivered_donations": delivered,
        "pending_donations": pending,
        "critical_donations": critical,
        "food_quantity": quantity
    }


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
