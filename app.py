import streamlit as st
import pandas as pd

from ai_engine import analyze_donation
from ngo_data import recommend_ngo
from database import (
    create_database,
    add_donation,
    get_donations,
    mark_delivered
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Food Rescue AI 4.0",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f7f9fc;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #071a2f 0%,
            #0b2947 100%
        );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .sidebar-logo {
        text-align: center;
        padding: 10px 0 25px 0;
    }

    .sidebar-icon {
        font-size: 42px;
    }

    .sidebar-title {
        font-size: 21px;
        font-weight: 800;
        margin-top: 5px;
    }

    .sidebar-subtitle {
        font-size: 12px;
        opacity: 0.7;
        line-height: 1.5;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 25px;
        font-size: 11px;
        opacity: 0.55;
    }

    /* ---------- HERO ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #071a2f 0%,
            #0b4268 55%,
            #087f73 100%
        );
        padding: 42px 45px;
        border-radius: 24px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(7, 26, 47, 0.15);
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.13);
        padding: 7px 15px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 15px;
    }

    .hero h1 {
        font-size: 44px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero h2 {
        font-size: 20px;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 10px;
    }

    .hero p {
        font-size: 15px;
        line-height: 1.7;
        max-width: 760px;
        opacity: 0.82;
        margin-top: 18px;
    }

    /* ---------- SECTION HEADERS ---------- */

    .section-title {
        font-size: 25px;
        font-weight: 750;
        color: #09243d;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 22px;
    }

    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        background: white;
        border-radius: 18px;
        padding: 22px;
        border: 1px solid #e8edf3;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
        min-height: 135px;
    }

    .metric-icon {
        font-size: 25px;
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        margin-top: 10px;
    }

    .metric-value {
        color: #09243d;
        font-size: 30px;
        font-weight: 800;
        margin-top: 2px;
    }

    /* ---------- FEATURE CARDS ---------- */

    .feature-card {
        background: white;
        border: 1px solid #e8edf3;
        border-radius: 18px;
        padding: 25px;
        height: 100%;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .feature-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }

    .feature-title {
        color: #09243d;
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .feature-text {
        color: #64748b;
        font-size: 13px;
        line-height: 1.6;
    }

    /* ---------- WORKFLOW ---------- */

    .workflow {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e8edf3;
        margin-top: 20px;
    }

    .workflow-item {
        text-align: center;
        flex: 1;
    }

    .workflow-icon {
        font-size: 28px;
    }

    .workflow-label {
        font-size: 12px;
        color: #334155;
        font-weight: 600;
        margin-top: 7px;
    }

    .workflow-arrow {
        color: #0b8f83;
        font-size: 22px;
        font-weight: bold;
    }

    /* ---------- AI RESULT ---------- */

    .ai-card {
        background: linear-gradient(
            135deg,
            #071a2f,
            #0b4268
        );
        border-radius: 22px;
        padding: 30px;
        color: white;
        box-shadow: 0 10px 30px rgba(7, 26, 47, 0.15);
    }

    .ai-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.65;
    }

    .ai-value {
        font-size: 34px;
        font-weight: 800;
        margin-top: 4px;
    }

    .priority-high {
        color: #ffb4b4;
    }

    .priority-medium {
        color: #ffd58a;
    }

    .priority-low {
        color: #a7f3d0;
    }

    /* ---------- NGO CARD ---------- */

    .ngo-card {
        background: white;
        border: 1px solid #e8edf3;
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
    }

    .ngo-name {
        color: #09243d;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 18px;
    }

    .ngo-detail {
        color: #64748b;
        font-size: 14px;
        margin: 9px 0;
    }

    /* ---------- INFO BOX ---------- */

    .info-card {
        background: #eef8f7;
        border-left: 5px solid #0b8f83;
        padding: 18px 20px;
        border-radius: 12px;
        color: #164e4a;
        font-size: 13px;
        line-height: 1.6;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 10px;
        border: none;
        font-weight: 700;
        padding: 0.65rem 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }

    /* ---------- INPUTS ---------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 10px;
    }

    /* ---------- TABLE ---------- */

    .dataframe {
        border-radius: 12px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        padding-top: 40px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

create_database()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-icon">🍱</div>
        <div class="sidebar-title">FOOD RESCUE AI 4.0</div>
        <div class="sidebar-subtitle">
            Intelligent Food Waste Management &
            Redistribution Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "🍱 Create Donation",
            "🤖 AI Recommendation",
            "📊 Impact Dashboard"
        ],
        label_visibility="visible"
    )

    st.markdown("""
    <div class="sidebar-footer">
        MSME Innovation Prototype<br>
        AI-Powered Food Redistribution
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            ♻️ AI-POWERED FOOD REDISTRIBUTION
        </div>

        <h1>Food Rescue AI 4.0</h1>

        <h2>
            Turning surplus food into meaningful impact.
        </h2>

        <p>
            An intelligent coordination platform designed to
            connect surplus food from restaurants, hotels,
            events and other sources with organizations that
            can redistribute it efficiently.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">How It Works</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'A simple digital pipeline connecting surplus food to people in need.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="workflow">

        <div class="workflow-item">
            <div class="workflow-icon">🍽️</div>
            <div class="workflow-label">SURPLUS FOOD</div>
        </div>

        <div class="workflow-arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">🤖</div>
            <div class="workflow-label">AI ANALYSIS</div>
        </div>

        <div class="workflow-arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">🤝</div>
            <div class="workflow-label">NGO MATCHING</div>
        </div>

        <div class="workflow-arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">🚚</div>
            <div class="workflow-label">PICKUP</div>
        </div>

        <div class="workflow-arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">❤️</div>
            <div class="workflow-label">REDISTRIBUTION</div>
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    donations = get_donations()

    total_donations = len(donations)

    total_meals = sum(
        donation[2]
        for donation in donations
    )

    delivered = sum(
        1
        for donation in donations
        if donation[7] == "Delivered"
    )

    st.markdown(
        '<div class="section-title">Platform Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🍱</div>
            <div class="metric-label">Total Donations</div>
            <div class="metric-value">{total_donations}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🍽️</div>
            <div class="metric-label">Meals Rescued</div>
            <div class="metric-value">{total_meals}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🚚</div>
            <div class="metric-label">Completed Deliveries</div>
            <div class="metric-value">{delivered}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">🌱</div>
            <div class="metric-label">Mission</div>
            <div class="metric-value">ZERO WASTE</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    st.markdown(
        '<div class="section-title">Core Capabilities</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">
                Intelligent Analysis
            </div>
            <div class="feature-text">
                Analyze donation information and determine
                the urgency of pickup using intelligent
                decision logic.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤝</div>
            <div class="feature-title">
                Smart NGO Matching
            </div>
            <div class="feature-text">
                Recommend suitable receiving organizations
                based on availability, capacity and proximity.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">
                Impact Tracking
            </div>
            <div class="feature-text">
                Track donations, rescued meals and completed
                redistributions through a centralized dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    st.markdown("""
    <div class="info-card">
        <b>Prototype Notice:</b>
        This demonstration uses sample NGO information and
        prototype decision logic. Real NGO partnerships,
        advanced AI models and live routing would be integrated
        during deployment.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CREATE DONATION
# ============================================================

elif page == "🍱 Create Donation":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            DONOR PORTAL
        </div>

        <h1>Create a Food Donation</h1>

        <h2>
            Tell us about your surplus food.
        </h2>

        <p>
            Our intelligent engine will evaluate the donation
            and recommend an appropriate redistribution action.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Donation Details</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Provide accurate information to improve the recommendation.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        food_name = st.text_input(
            "🍱 Food Name",
            placeholder="e.g. Biryani, Rice, Meals"
        )

        quantity = st.number_input(
            "🍽️ Quantity / Meals",
            min_value=1,
            value=50,
            step=1
        )

        preparation_time = st.time_input(
            "⏰ Preparation Time"
        )

    with col2:

        storage_condition = st.selectbox(
            "❄️ Storage Condition",
            [
                "Refrigerated",
                "Room Temperature",
                "Frozen"
            ]
        )

        donor_location = st.text_input(
            "📍 Donor Location",
            placeholder="e.g. Hyderabad"
        )

        donor_type = st.selectbox(
            "🏢 Donor Type",
            [
                "Restaurant",
                "Hotel",
                "Caterer",
                "Event",
                "Hostel",
                "Supermarket",
                "Other"
            ]
        )

    st.markdown("")

    st.markdown("""
    <div class="info-card">
        <b>AI Decision Engine:</b>
        The prototype evaluates food type, quantity and storage
        conditions to estimate pickup urgency and identify a
        suitable receiving organization.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    if st.button(
        "🤖 ANALYZE & FIND MATCH",
        use_container_width=True
    ):

        if not food_name:
            st.warning("Please enter the food name.")

        elif not donor_location:
            st.warning("Please enter the donor location.")

        else:

            result = analyze_donation(
                food_name,
                quantity,
                preparation_time,
                storage_condition
            )

            ngo = recommend_ngo()

            add_donation(
                food_name,
                quantity,
                str(preparation_time),
                storage_condition,
                result["priority"],
                ngo["name"]
            )

            st.session_state["analysis"] = result
            st.session_state["ngo"] = ngo

            st.success(
                "Donation successfully analyzed and matched!"
            )

            st.balloons()


# ============================================================
# AI RECOMMENDATION
# ============================================================

elif page == "🤖 AI Recommendation":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            INTELLIGENT DECISION ENGINE
        </div>

        <h1>AI Recommendation</h1>

        <h2>
            From donation data to an actionable decision.
        </h2>

        <p>
            The prototype evaluates the donation and generates
            a pickup priority together with a recommended
            receiving organization.
        </p>

    </div>
    """, unsafe_allow_html=True)

    if "analysis" not in st.session_state:

        st.markdown("""
        <div class="info-card">
            <b>No analysis available.</b><br>
            Please create a donation first from the
            <b>Create Donation</b> section.
        </div>
        """, unsafe_allow_html=True)

    else:

        result = st.session_state["analysis"]
        ngo = st.session_state["ngo"]

        col1, col2 = st.columns(2)

        with col1:

            priority_class = (
                "priority-high"
                if result["priority"] == "HIGH"
                else
                "priority-medium"
                if result["priority"] == "MEDIUM"
                else
                "priority-low"
            )

            reasons_html = ""

            for reason in result["reasons"]:
                reasons_html += f"<p>✓ {reason}</p>"

            st.markdown(f"""
            <div class="ai-card">

                <div class="ai-label">
                    PICKUP PRIORITY
                </div>

                <div class="ai-value {priority_class}">
                    {result["priority"]}
                </div>

                <br>

                <div class="ai-label">
                    DECISION SCORE
                </div>

                <div class="ai-value">
                    {result["score"]}
                </div>

                <br>

                <div class="ai-label">
                    DECISION FACTORS
                </div>

                <div style="margin-top:10px; opacity:0.85;">
                    {reasons_html}
                </div>

            </div>
            """, unsafe_allow_html=True)

        with col2:

            st.markdown(f"""
            <div class="ngo-card">

                <div style="font-size:35px;">
                    🤝
                </div>

                <div class="ngo-name">
                    {ngo["name"]}
                </div>

                <div class="ngo-detail">
                    📍 <b>Distance:</b>
                    {ngo["distance"]} km
                </div>

                <div class="ngo-detail">
                    📦 <b>Capacity:</b>
                    {ngo["capacity"]}
                </div>

                <div class="ngo-detail">
                    ❤️ <b>Current Need:</b>
                    {ngo["need"]}
                </div>

                <br>

                <div class="info-card">
                    <b>Recommended Action</b><br>
                    Initiate pickup and redistribution.
                </div>

            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        st.markdown(
            '<div class="section-title">Decision Flow</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="workflow">

            <div class="workflow-item">
                <div class="workflow-icon">🍱</div>
                <div class="workflow-label">DONATION</div>
            </div>

            <div class="workflow-arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">🤖</div>
                <div class="workflow-label">ANALYZE</div>
            </div>

            <div class="workflow-arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">🔴</div>
                <div class="workflow-label">PRIORITIZE</div>
            </div>

            <div class="workflow-arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">🤝</div>
                <div class="workflow-label">MATCH NGO</div>
            </div>

            <div class="workflow-arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">🚚</div>
                <div class="workflow-label">PICKUP</div>
            </div>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        st.markdown("""
        <div class="info-card">
            <b>Prototype AI Note:</b>
            The current MVP uses a transparent rule-based decision
            engine to demonstrate intelligent prioritization.
            A trained machine-learning model can replace this
            engine as real operational data becomes available.
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# IMPACT DASHBOARD
# ============================================================

elif page == "📊 Impact Dashboard":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            IMPACT & OPERATIONS
        </div>

        <h1>Impact Dashboard</h1>

        <h2>
            Measure every rescued meal.
        </h2>

        <p>
            Monitor donations, deliveries and food rescued
            through the platform.
        </p>

    </div>
    """, unsafe_allow_html=True)

    donations = get_donations()

    total_meals = sum(
        donation[2]
        for donation in donations
        if donation[7] == "Delivered"
    )

    delivered = sum(
        1
        for donation in donations
        if donation[7] == "Delivered"
    )

    pending = sum(
        1
        for donation in donations
        if donation[7] != "Delivered"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🍽️</div>
            <div class="metric-label">Meals Rescued</div>
            <div class="metric-value">{total_meals}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">✅</div>
            <div class="metric-label">Delivered</div>
            <div class="metric-value">{delivered}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🚚</div>
            <div class="metric-label">Pending Pickup</div>
            <div class="metric-value">{pending}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">♻️</div>
            <div class="metric-label">Total Donations</div>
            <div class="metric-value">{len(donations)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    if donations:

        st.markdown(
            '<div class="section-title">Donation Operations</div>',
            unsafe_allow_html=True
        )

        df = pd.DataFrame(
            donations,
            columns=[
                "ID",
                "Food",
                "Quantity",
                "Preparation Time",
                "Storage",
                "Priority",
                "NGO",
                "Status"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("")

        col1, col2 = st.columns([2, 1])

        with col1:

            st.markdown(
                '<div class="section-title">'
                'Update Delivery Status'
                '</div>',
                unsafe_allow_html=True
            )

            donation_id = st.number_input(
                "Donation ID",
                min_value=1,
                step=1
            )

        with col2:

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                "✅ MARK AS DELIVERED",
                use_container_width=True
            ):

                mark_delivered(
                    donation_id
                )

                st.success(
                    "Donation successfully marked as delivered!"
                )

                st.rerun()

    else:

        st.markdown("""
        <div class="info-card">
            <b>No donations yet.</b><br>
            Create your first food donation to start
            tracking the platform's impact.
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    FOOD RESCUE AI 4.0 &nbsp;•&nbsp;
    AI-Powered Intelligent Food Waste Management &
    Redistribution System
    <br><br>
    MSME Innovation / Hackathon Prototype
</div>
""", unsafe_allow_html=True)
