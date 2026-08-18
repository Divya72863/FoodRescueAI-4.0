import streamlit as st
import pandas as pd

from ai_engine import analyze_donation
from ngo_data import recommend_ngo
from database import (
    init_database,
    add_donation,
    get_donations,
    mark_delivered
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Food Rescue AI 4.0",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_database()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* ---------------- GLOBAL ---------------- */

.stApp {
    background-color: #F7FAF8;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}


/* ---------------- SIDEBAR ---------------- */

section[data-testid="stSidebar"] {
    background-color: #0B3D2E;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-brand {
    padding: 20px 5px 25px 5px;
    text-align: center;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    color: white;
}

.sidebar-subtitle {
    font-size: 12px;
    color: #D5E8DE;
    margin-top: 5px;
}


/* ---------------- HERO ---------------- */

.hero {
    background: linear-gradient(
        135deg,
        #0B3D2E 0%,
        #176B4D 55%,
        #2E8B57 100%
    );

    padding: 40px;
    border-radius: 22px;
    margin-bottom: 30px;
    color: white;

    box-shadow:
        0 10px 30px rgba(11, 61, 46, 0.18);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 19px;
    margin-top: 8px;
    opacity: 0.95;
}

.hero-description {
    font-size: 14px;
    margin-top: 18px;
    max-width: 800px;
    line-height: 1.6;
    opacity: 0.85;
}


/* ---------------- SECTION TITLES ---------------- */

.section-title {
    font-size: 27px;
    font-weight: 750;
    color: #0B3D2E;
    margin-top: 15px;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #6B7972;
    font-size: 14px;
    margin-bottom: 22px;
}


/* ---------------- METRIC CARDS ---------------- */

.metric-card {
    background: white;
    padding: 24px;
    border-radius: 17px;

    border: 1px solid #E0EAE4;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.04);
}

.metric-label {
    color: #718078;
    font-size: 13px;
}

.metric-value {
    color: #0B3D2E;
    font-size: 30px;
    font-weight: 750;
    margin-top: 5px;
}


/* ---------------- GENERAL CARDS ---------------- */

.card {
    background: white;
    padding: 25px;
    border-radius: 18px;

    border: 1px solid #E1EAE5;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.04);

    margin-bottom: 18px;
}

.card-title {
    color: #0B3D2E;
    font-size: 19px;
    font-weight: 700;
}

.card-text {
    color: #66756D;
    font-size: 14px;
    line-height: 1.7;
}


/* ---------------- WORKFLOW ---------------- */

.workflow {
    background: white;

    padding: 22px 12px;

    border-radius: 16px;

    border: 1px solid #E2EBE5;

    text-align: center;

    min-height: 120px;

    box-shadow:
        0 4px 14px rgba(0, 0, 0, 0.03);
}

.workflow-title {
    color: #0B3D2E;
    font-weight: 700;
    font-size: 14px;
}

.workflow-text {
    color: #748078;
    font-size: 11px;
    margin-top: 8px;
    line-height: 1.4;
}


/* ---------------- PRIORITY ---------------- */

.priority-high {
    background: #FFF0F0;

    border: 1px solid #F5C6C6;

    color: #B42318;

    padding: 18px;

    border-radius: 14px;

    text-align: center;

    font-size: 20px;

    font-weight: 750;
}

.priority-medium {
    background: #FFF8E8;

    border: 1px solid #F0D694;

    color: #A15C00;

    padding: 18px;

    border-radius: 14px;

    text-align: center;

    font-size: 20px;

    font-weight: 750;
}

.priority-low {
    background: #ECF8F0;

    border: 1px solid #B9DFC4;

    color: #16743D;

    padding: 18px;

    border-radius: 14px;

    text-align: center;

    font-size: 20px;

    font-weight: 750;
}


/* ---------------- NGO CARD ---------------- */

.ngo-card {
    background: linear-gradient(
        135deg,
        #F0FAF4,
        #FFFFFF
    );

    border: 1px solid #CDE7D6;

    padding: 25px;

    border-radius: 18px;

    min-height: 190px;
}

.ngo-name {
    font-size: 21px;
    font-weight: 750;
    color: #0B3D2E;
    margin-bottom: 15px;
}

.ngo-detail {
    color: #617169;
    font-size: 14px;
    margin-top: 9px;
}


/* ---------------- INFO BOX ---------------- */

.info-box {
    background: #EAF6EF;

    border-left: 5px solid #238B57;

    padding: 18px;

    border-radius: 10px;

    color: #24553A;

    line-height: 1.6;
}


/* ---------------- FOOTER ---------------- */

.footer {
    text-align: center;

    color: #829088;

    font-size: 12px;

    padding: 30px 0 10px 0;
}


/* ---------------- BUTTONS ---------------- */

.stButton > button {

    border-radius: 10px;

    font-weight: 650;

    min-height: 45px;

}


/* ---------------- INPUTS ---------------- */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {

    border-radius: 10px;

}


/* ---------------- DATAFRAME ---------------- */

[data-testid="stDataFrame"] {

    border-radius: 12px;

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("""
<div class="sidebar-brand">

<div class="sidebar-title">
Food Rescue AI 4.0
</div>

<div class="sidebar-subtitle">
Intelligent Food Redistribution
</div>

</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "New Donation",
        "Track Donations",
        "AI & Technology"
    ]
)

st.sidebar.divider()

st.sidebar.markdown(
    "**Prototype**\n\n"
    "AI-powered coordination for surplus food rescue."
)


# ============================================================
# GET DONATION DATA
# ============================================================

donations = get_donations()


# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
FOOD RESCUE AI 4.0
</div>

<div class="hero-subtitle">
AI-Powered Food Rescue & Redistribution Platform
</div>

<div class="hero-description">
Connecting surplus food with organizations in need through
intelligent prioritization, smart NGO matching and delivery tracking.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">Impact Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Monitor rescued food, donations and delivery activity.'
        '</div>',
        unsafe_allow_html=True
    )

    # Calculate metrics

    total_meals = sum(
        donation[2]
        for donation in donations
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

    total_donations = len(donations)

    # Metric cards

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Meals Rescued", total_meals),
        ("Deliveries", delivered),
        ("Total Donations", total_donations),
        ("Pending Pickup", pending)
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4],
        metrics
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        {label}
                    </div>

                    <div class="metric-value">
                        {value:,}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # Workflow

    st.markdown(
        '<div class="section-title">How the Platform Works</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'From surplus food to successful delivery.'
        '</div>',
        unsafe_allow_html=True
    )

    workflow = [
        ("Donate", "Enter surplus food details"),
        ("AI Analyze", "Estimate pickup priority"),
        ("Smart Match", "Recommend suitable NGO"),
        ("Route", "Plan efficient pickup"),
        ("Track", "Monitor delivery status"),
        ("Impact", "Measure rescued food")
    ]

    cols = st.columns(6)

    for col, (title, text) in zip(
        cols,
        workflow
    ):

        with col:

            st.markdown(
                f"""
                <div class="workflow">

                    <div class="workflow-title">
                        {title}
                    </div>

                    <div class="workflow-text">
                        {text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # Recent donations

    st.markdown(
        '<div class="section-title">Recent Donations</div>',
        unsafe_allow_html=True
    )

    if donations:

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

    else:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    No Donations Yet
                </div>

                <div class="card-text">
                    Create your first donation from the
                    New Donation section to see the system
                    in action.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    st.markdown(
        """
        <div class="info-box">

        <b>Our Mission</b><br><br>

        Food should reach people, not landfills.
        Food Rescue AI 4.0 uses intelligent coordination
        to help surplus food reach organizations that need it.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# NEW DONATION
# ============================================================

elif page == "New Donation":

    st.markdown(
        '<div class="section-title">Create a Food Donation</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Enter surplus food details and analyze the donation.'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1.35, 1],
        gap="large"
    )

    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    with left:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    Donation Details
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        food_name = st.text_input(
            "Food Name",
            placeholder="Example: Biryani"
        )

        quantity = st.number_input(
            "Quantity / Number of Meals",
            min_value=1,
            max_value=10000,
            value=50
        )

        preparation_time = st.number_input(
            "Hours Since Preparation",
            min_value=0,
            max_value=48,
            value=2
        )

        storage_condition = st.selectbox(
            "Storage Condition",
            [
                "Refrigerated",
                "Room Temperature",
                "Insulated Container"
            ]
        )

        donor_location = st.text_input(
            "Donor Location",
            value="Hyderabad"
        )

        analyze_button = st.button(
            "Analyze Donation",
            use_container_width=True
        )

    # --------------------------------------------------------
    # EXPLANATION CARD
    # --------------------------------------------------------

    with right:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    AI Decision Factors
                </div>

                <br>

                <div class="card-text">

                    <b>Quantity</b><br>
                    Larger donations can receive higher priority.

                    <br><br>

                    <b>Storage Condition</b><br>
                    Storage conditions influence pickup urgency.

                    <br><br>

                    <b>Food Type</b><br>
                    Prepared food may require timely redistribution.

                    <br><br>

                    <b>Preparation Time</b><br>
                    Recently prepared food can receive increased priority.

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # ANALYSIS
    # ========================================================

    if analyze_button:

        if not food_name.strip():

            st.error(
                "Please enter the food name."
            )

        else:

            analysis = analyze_donation(
                food_name,
                quantity,
                preparation_time,
                storage_condition
            )

            recommended_ngo, alternatives = (
                recommend_ngo(quantity)
            )

            st.session_state["analysis"] = analysis
            st.session_state["ngo"] = recommended_ngo
            st.session_state["alternatives"] = alternatives

    # ========================================================
    # DISPLAY ANALYSIS
    # ========================================================

    if "analysis" in st.session_state:

        analysis = st.session_state["analysis"]

        recommended_ngo = st.session_state["ngo"]

        alternatives = st.session_state["alternatives"]

        st.divider()

        st.markdown(
            '<div class="section-title">'
            'AI Analysis Result'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Explainable prototype decision engine'
            '</div>',
            unsafe_allow_html=True
        )

        # Score cards

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "AI Priority",
                analysis["priority"]
            )

        with c2:

            st.metric(
                "Decision Score",
                analysis["score"]
            )

        with c3:

            st.metric(
                "Recommended NGO",
                recommended_ngo["name"]
            )

        # Priority display

        if analysis["priority"] == "HIGH":

            st.markdown(
                """
                <div class="priority-high">

                    HIGH PRIORITY

                    <br>

                    <span style="font-size:14px;">
                    Arrange pickup immediately
                    </span>

                </div>
                """,
                unsafe_allow_html=True
            )

        elif analysis["priority"] == "MEDIUM":

            st.markdown(
                """
                <div class="priority-medium">

                    MEDIUM PRIORITY

                    <br>

                    <span style="font-size:14px;">
                    Arrange pickup soon
                    </span>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="priority-low">

                    LOW PRIORITY

                    <br>

                    <span style="font-size:14px;">
                    Pickup can be scheduled
                    </span>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        # Reason and NGO

        c1, c2 = st.columns(
            2,
            gap="large"
        )

        with c1:

            st.markdown(
                """
                <div class="card">

                    <div class="card-title">
                        Why This Priority?
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            for reason in analysis["reasons"]:

                st.write(
                    "• " + reason
                )

            st.info(
                analysis["recommendation"]
            )

        with c2:

            st.markdown(
                f"""
                <div class="ngo-card">

                    <div class="ngo-name">
                        Recommended NGO
                    </div>

                    <div class="ngo-name">
                        {recommended_ngo["name"]}
                    </div>

                    <div class="ngo-detail">
                        Distance:
                        <b>{recommended_ngo["distance"]} km</b>
                    </div>

                    <div class="ngo-detail">
                        Current Need:
                        <b>{recommended_ngo["need"]}</b>
                    </div>

                    <div class="ngo-detail">
                        Capacity:
                        <b>{recommended_ngo["capacity"]}</b>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        # Alternatives

        with st.expander(
            "View Alternative NGO Matches"
        ):

            for ngo in alternatives:

                st.write(
                    f"**{ngo['name']}**  |  "
                    f"{ngo['distance']} km  |  "
                    f"Need: {ngo['need']}  |  "
                    f"Capacity: {ngo['capacity']}"
                )

        st.write("")

        # Confirm

        if st.button(
            "Confirm Donation & Assign NGO",
            use_container_width=True
        ):

            add_donation(
                food_name,
                quantity,
                preparation_time,
                storage_condition,
                analysis["priority"],
                recommended_ngo["name"]
            )

            st.success(
                "Donation created successfully. "
                "NGO assigned and pickup is pending."
            )

            # Clear analysis

            for key in [
                "analysis",
                "ngo",
                "alternatives"
            ]:

                if key in st.session_state:

                    del st.session_state[key]


# ============================================================
# TRACK DONATIONS
# ============================================================

elif page == "Track Donations":

    st.markdown(
        '<div class="section-title">Donation Tracking</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Monitor donation status from pickup to delivery.'
        '</div>',
        unsafe_allow_html=True
    )

    donations = get_donations()

    if donations:

        pending = sum(
            1
            for donation in donations
            if donation[7] != "Delivered"
        )

        delivered = sum(
            1
            for donation in donations
            if donation[7] == "Delivered"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Pending Pickup",
                pending
            )

        with c2:

            st.metric(
                "Delivered",
                delivered
            )

        st.write("")

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

        st.divider()

        st.markdown(
            '<div class="section-title">'
            'Update Delivery Status'
            '</div>',
            unsafe_allow_html=True
        )

        donation_ids = [
            donation[0]
            for donation in donations
        ]

        selected_id = st.selectbox(
            "Select Donation",
            donation_ids
        )

        selected_donation = next(
            (
                donation
                for donation in donations
                if donation[0] == selected_id
            ),
            None
        )

        if selected_donation:

            st.info(
                f"Food: {selected_donation[1]} | "
                f"Quantity: {selected_donation[2]} | "
                f"NGO: {selected_donation[6]} | "
                f"Status: {selected_donation[7]}"
            )

        if st.button(
            "Mark as Delivered",
            use_container_width=True
        ):

            mark_delivered(
                selected_id
            )

            st.success(
                f"Donation #{selected_id} marked as delivered."
            )

            st.rerun()

    else:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    No Donations Available
                </div>

                <div class="card-text">
                    Create a donation from the New Donation
                    section to begin tracking.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# AI & TECHNOLOGY
# ============================================================

elif page == "AI & Technology":

    st.markdown(
        '<div class="section-title">'
        'AI & Technology'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Technology components planned for the Food Rescue AI platform.'
        '</div>',
        unsafe_allow_html=True
    )

    # Technology features

    features = [
        (
            "Computer Vision",
            "Identify food categories from uploaded images."
        ),
        (
            "Pickup Priority",
            "Estimate donation urgency using food and storage information."
        ),
        (
            "Smart NGO Matching",
            "Recommend suitable recipient organizations."
        ),
        (
            "Route Optimization",
            "Identify efficient pickup and delivery routes."
        ),
        (
            "Predictive Analytics",
            "Analyze historical donation patterns."
        )
    ]

    cols = st.columns(5)

    for col, (title, description) in zip(
        cols,
        features
    ):

        with col:

            st.markdown(
                f"""
                <div class="workflow">

                    <div class="workflow-title">
                        {title}
                    </div>

                    <div class="workflow-text">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # Prototype note

    st.markdown(
        """
        <div class="info-box">

        <b>Prototype Note</b><br><br>

        The current prototype uses an explainable
        rule-based decision engine to demonstrate
        the intelligent decision workflow.

        In a production implementation, the decision
        engine can be enhanced with trained machine
        learning models using real-world food donation data.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # Technology stack

    st.markdown(
        '<div class="section-title">'
        'Technology Stack'
        '</div>',
        unsafe_allow_html=True
    )

    tech = pd.DataFrame({
        "Layer": [
            "Frontend",
            "Backend",
            "Database",
            "AI / ML",
            "Computer Vision",
            "Maps",
            "Cloud"
        ],

        "Technology": [
            "Streamlit / React / Flutter",
            "Python / FastAPI",
            "SQLite / Firebase / MongoDB",
            "Scikit-learn / TensorFlow / PyTorch",
            "OpenCV",
            "Google Maps API / OpenStreetMap",
            "Firebase / Google Cloud"
        ]
    })

    st.dataframe(
        tech,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        FOOD RESCUE AI 4.0 • Prototype

    </div>
    """,
    unsafe_allow_html=True
)
