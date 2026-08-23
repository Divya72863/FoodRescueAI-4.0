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
    background: #07120f;
    color: #f8fafc;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #0b1f1a;
    border-right: 1px solid #18372f;
}

section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

.brand {
    text-align: center;
    padding: 20px 5px 30px;
}

.brand-icon {
    font-size: 45px;
}

.brand-title {
    font-size: 20px;
    font-weight: 800;
    margin-top: 8px;
}

.brand-subtitle {
    color: #8ca59d !important;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 5px;
}


/* ---------- HERO ---------- */

.hero {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            #0b2b23 0%,
            #0d4535 45%,
            #087f63 100%
        );

    border: 1px solid #216654;
    border-radius: 28px;

    padding: 48px;

    margin-bottom: 30px;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.25);
}

.hero:after {
    content: "♻️";
    position: absolute;
    right: 50px;
    top: 25px;
    font-size: 130px;
    opacity: 0.08;
}

.badge {
    display: inline-block;

    background: rgba(255,255,255,0.12);

    border: 1px solid rgba(255,255,255,0.15);

    padding: 7px 14px;

    border-radius: 30px;

    font-size: 11px;

    letter-spacing: 1px;

    color: #a7f3d0;
}

.hero h1 {
    font-size: 48px;

    font-weight: 850;

    margin: 15px 0 5px;

    color: white;
}

.hero h2 {
    font-size: 20px;

    font-weight: 400;

    color: #c7e8df;

    margin-bottom: 18px;
}

.hero p {
    max-width: 750px;

    color: #b8d5cd;

    line-height: 1.7;

    font-size: 14px;
}


/* ---------- HEADINGS ---------- */

.section-title {
    color: white;

    font-size: 25px;

    font-weight: 800;

    margin-top: 30px;

    margin-bottom: 5px;
}

.section-subtitle {
    color: #7f9c93;

    font-size: 13px;

    margin-bottom: 20px;
}


/* ---------- CARDS ---------- */

.card {
    background: #0d211c;

    border: 1px solid #1a3c32;

    border-radius: 20px;

    padding: 24px;

    margin-bottom: 15px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.15);
}

.card:hover {
    border-color: #2d7763;
}


/* ---------- METRICS ---------- */

.metric {
    background:
        linear-gradient(
            145deg,
            #0d211c,
            #102b24
        );

    border: 1px solid #1a3c32;

    border-radius: 20px;

    padding: 23px;

    min-height: 135px;
}

.metric-icon {
    font-size: 25px;
}

.metric-label {
    color: #78978e;

    font-size: 12px;

    margin-top: 10px;
}

.metric-value {
    color: white;

    font-size: 29px;

    font-weight: 850;

    margin-top: 3px;
}


/* ---------- FEATURE ---------- */

.feature {
    background: #0d211c;

    border: 1px solid #1a3c32;

    border-radius: 20px;

    padding: 27px;

    min-height: 185px;
}

.feature-icon {
    font-size: 32px;
}

.feature-title {
    color: white;

    font-weight: 750;

    font-size: 17px;

    margin: 12px 0 8px;
}

.feature-text {
    color: #829c94;

    font-size: 13px;

    line-height: 1.7;
}


/* ---------- WORKFLOW ---------- */

.workflow {
    background: #0d211c;

    border: 1px solid #1a3c32;

    border-radius: 20px;

    padding: 25px;

    display: flex;

    justify-content: space-between;

    align-items: center;
}

.workflow-item {
    text-align: center;
}

.workflow-icon {
    font-size: 28px;
}

.workflow-text {
    color: #91aaa2;

    font-size: 11px;

    margin-top: 7px;

    font-weight: 700;
}

.arrow {
    color: #34d399;

    font-size: 22px;
}


/* ---------- AI RESULT ---------- */

.ai-result {
    background:
        linear-gradient(
            145deg,
            #0d2d24,
            #0c4737
        );

    border: 1px solid #24765d;

    border-radius: 24px;

    padding: 30px;

    min-height: 390px;
}

.ai-small {
    color: #8bb9ab;

    font-size: 11px;

    text-transform: uppercase;

    letter-spacing: 1.5px;
}

.ai-big {
    color: #6ee7b7;

    font-size: 42px;

    font-weight: 900;

    margin: 5px 0 15px;
}


/* ---------- NGO ---------- */

.ngo-result {
    background: #0d211c;

    border: 1px solid #1a3c32;

    border-radius: 24px;

    padding: 30px;

    min-height: 390px;
}

.ngo-name {
    color: white;

    font-size: 23px;

    font-weight: 850;

    margin: 12px 0 20px;
}

.detail {
    color: #91aaa2;

    font-size: 13px;

    padding: 7px 0;

    border-bottom: 1px solid #18352d;
}

.detail b {
    color: #d8e7e2;
}


/* ---------- INFO ---------- */

.info {
    background: #0d2922;

    border-left: 4px solid #34d399;

    border-radius: 12px;

    padding: 17px;

    color: #9db9b0;

    font-size: 13px;

    line-height: 1.7;
}


/* ---------- BUTTON ---------- */

.stButton > button {
    background: linear-gradient(
        90deg,
        #10b981,
        #059669
    );

    color: white;

    border: none;

    border-radius: 12px;

    font-weight: 800;

    min-height: 48px;
}

.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #34d399,
        #10b981
    );

    color: white;

    border: none;
}


/* ---------- INPUTS ---------- */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: #0d211c;

    border-color: #24463c;

    border-radius: 10px;
}

input {
    color: white !important;
}


/* ---------- DATAFRAME ---------- */

[data-testid="stDataFrame"] {
    border: 1px solid #1a3c32;
    border-radius: 15px;
}


/* ---------- FOOTER ---------- */

.footer {
    text-align: center;

    color: #506b63;

    font-size: 11px;

    margin-top: 60px;

    padding-top: 20px;

    border-top: 1px solid #16352d;
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
    <div class="brand">

        <div class="brand-icon">
            🍱
        </div>

        <div class="brand-title">
            FOOD RESCUE AI
        </div>

        <div class="brand-subtitle">
            Intelligent Food Waste Management
            & Redistribution System
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Home",
            "🍱 Donate Food",
            "🤖 AI Matching",
            "📊 Impact"
        ]
    )

    st.markdown("---")

    st.markdown("""
    <div style="
        color:#78978e;
        font-size:11px;
        line-height:1.6;
        text-align:center;
    ">
        MSME Innovation Prototype<br><br>
        <b style="color:#34d399;">
        Turning surplus into impact.
        </b>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.markdown("""
    <div class="hero">

        <span class="badge">
            AI-POWERED FOOD REDISTRIBUTION
        </span>

        <h1>
            Food Rescue AI 4.0
        </h1>

        <h2>
            Turning surplus food into meaningful impact.
        </h2>

        <p>
            Food exists. People need it.
            The missing link is intelligent coordination.
            Food Rescue AI connects surplus food donors
            with organizations capable of redistributing
            it quickly and efficiently.
        </p>

    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------

    donations = get_donations()

    total_donations = len(donations)

    total_meals = sum(
        d[2] for d in donations
    )

    delivered = sum(
        1 for d in donations
        if d[7] == "Delivered"
    )


    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">🍱</div>

            <div class="metric-label">
                DONATIONS
            </div>

            <div class="metric-value">
                {total_donations}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">🍽️</div>

            <div class="metric-label">
                MEALS RESCUED
            </div>

            <div class="metric-value">
                {total_meals}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">🚚</div>

            <div class="metric-label">
                DELIVERIES
            </div>

            <div class="metric-value">
                {delivered}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="metric">

            <div class="metric-icon">♻️</div>

            <div class="metric-label">
                MISSION
            </div>

            <div class="metric-value">
                ZERO WASTE
            </div>

        </div>
        """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">The Rescue Network</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'One intelligent flow from surplus food to redistribution.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="workflow">

        <div class="workflow-item">
            <div class="workflow-icon">🍽️</div>
            <div class="workflow-text">SURPLUS</div>
        </div>

        <div class="arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">🤖</div>
            <div class="workflow-text">AI ANALYSIS</div>
        </div>

        <div class="arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">🧠</div>
            <div class="workflow-text">SMART MATCH</div>
        </div>

        <div class="arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">🚚</div>
            <div class="workflow-text">PICKUP</div>
        </div>

        <div class="arrow">→</div>

        <div class="workflow-item">
            <div class="workflow-icon">❤️</div>
            <div class="workflow-text">IMPACT</div>
        </div>

    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">What Makes It Intelligent?</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature">

            <div class="feature-icon">⚡</div>

            <div class="feature-title">
                Priority Intelligence
            </div>

            <div class="feature-text">
                Evaluate preparation time, quantity,
                storage conditions and food type to
                identify which donations need faster action.
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature">

            <div class="feature-icon">🎯</div>

            <div class="feature-title">
                Smart NGO Matching
            </div>

            <div class="feature-text">
                Combine distance, receiving capacity,
                current need and donation urgency
                to recommend a suitable NGO.
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature">

            <div class="feature-icon">📈</div>

            <div class="feature-title">
                Impact Tracking
            </div>

            <div class="feature-text">
                Track rescued meals, completed deliveries
                and donation activity through one
                centralized platform.
            </div>

        </div>
        """, unsafe_allow_html=True)


    st.markdown("")

    st.markdown("""
    <div class="info">

        💡 <b>Prototype:</b>
        This MVP demonstrates the intelligent
        coordination workflow using sample NGO data.
        Real partnerships, live maps and trained ML
        models can be integrated during deployment.

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# DONATE FOOD
# ============================================================

elif page == "🍱 Donate Food":

    st.markdown("""
    <div class="hero">

        <span class="badge">
            DONOR PORTAL
        </span>

        <h1>
            Rescue Food
        </h1>

        <h2>
            Every meal deserves a destination.
        </h2>

        <p>
            Enter the surplus food details below.
            Our intelligent engine will analyze the
            donation and find the most suitable NGO match.
        </p>

    </div>
    """, unsafe_allow_html=True)


    st.markdown(
        '<div class="section-title">Donation Information</div>',
        unsafe_allow_html=True
    )


    left, right = st.columns(2)


    with left:

        food_name = st.text_input(
            "🍱 Food Name",
            placeholder="Example: Biryani"
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


    with right:

        storage_condition = st.selectbox(
            "❄️ Storage Condition",
            [
                "Refrigerated",
                "Room Temperature",
                "Frozen"
            ]
        )

        donor_location = st.selectbox(
            "📍 Donor Location",
            [
                "Hyderabad",
                "Secunderabad",
                "Kukatpally",
                "Madhapur",
                "Gachibowli",
                "Begumpet"
            ]
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
    <div class="card">

        <div style="
            color:#34d399;
            font-weight:800;
            font-size:15px;
        ">
            🤖 Intelligent Decision Engine
        </div>

        <div style="
            color:#829c94;
            font-size:13px;
            line-height:1.7;
            margin-top:8px;
        ">
            Your donation will be evaluated using
            food characteristics, quantity, preparation
            time and storage conditions. The resulting
            priority will then guide NGO matching.
        </div>

    </div>
    """, unsafe_allow_html=True)


    if st.button(
        "🚀 ANALYZE DONATION & FIND NGO",
        use_container_width=True
    ):

        if not food_name.strip():

            st.error(
                "Please enter the food name first."
            )

        else:

            # AI analysis

            result = analyze_donation(
                food_name,
                quantity,
                preparation_time,
                storage_condition
            )


            # NGO matching

            ngo, matches = recommend_ngo(
                donor_location=donor_location,
                quantity=quantity,
                priority=result["priority"]
            )


            # Database

            add_donation(
                food_name,
                quantity,
                str(preparation_time),
                storage_condition,
                result["priority"],
                ngo["name"]
            )


            # Save results

            st.session_state["analysis"] = result

            st.session_state["ngo"] = ngo

            st.session_state["matches"] = matches

            st.session_state["donor_location"] = donor_location

            st.session_state["donor_type"] = donor_type


            st.success(
                "🎉 Donation analyzed successfully!"
            )

            st.info(
                "Go to 'AI Matching' to see the complete recommendation."
            )


# ============================================================
# AI MATCHING
# ============================================================

elif page == "🤖 AI Matching":

    st.markdown("""
    <div class="hero">

        <span class="badge">
            AI DECISION ENGINE
        </span>

        <h1>
            Intelligent Matching
        </h1>

        <h2>
            The right food. The right NGO. The right time.
        </h2>

        <p>
            Food Rescue AI evaluates donation urgency and
            NGO suitability to recommend an actionable
            redistribution path.
        </p>

    </div>
    """, unsafe_allow_html=True)


    if "analysis" not in st.session_state:

        st.markdown("""
        <div class="info">

            🍱 No donation has been analyzed yet.<br><br>

            Go to <b>Donate Food</b> and create a donation
            to see the AI recommendation.

        </div>
        """, unsafe_allow_html=True)

    else:

        result = st.session_state["analysis"]

        ngo = st.session_state["ngo"]

        matches = st.session_state["matches"]

        donor_location = st.session_state["donor_location"]


        # ----------------------------------------------------
        # RESULT CARDS
        # ----------------------------------------------------

        c1, c2 = st.columns(2)


        with c1:

            st.markdown(f"""
            <div class="ai-result">

                <div class="ai-small">
                    AI PICKUP PRIORITY
                </div>

                <div class="ai-big">
                    {result["priority"]}
                </div>

                <div class="ai-small">
                    DECISION SCORE
                </div>

                <div style="
                    font-size:30px;
                    font-weight:800;
                    color:white;
                    margin:5px 0 20px;
                ">
                    {result["score"]}
                </div>

                <div class="ai-small">
                    HOURS SINCE PREPARATION
                </div>

                <div style="
                    color:#d1fae5;
                    font-size:22px;
                    font-weight:800;
                    margin-top:5px;
                ">
                    {result.get("hours_since_preparation", 0)}
                    hours
                </div>

                <br>

                <div class="ai-small">
                    WHY?
                </div>

            </div>
            """, unsafe_allow_html=True)

            for reason in result["reasons"]:
                st.markdown(
                    f"✓ {reason}"
                )


        with c2:

            st.markdown(f"""
            <div class="ngo-result">

                <div style="font-size:42px;">
                    🏆
                </div>

                <div class="ngo-name">
                    {ngo["name"]}
                </div>

                <div class="detail">
                    📍 <b>Donor:</b>
                    {donor_location}
                </div>

                <div class="detail">
                    🚗 <b>Distance:</b>
                    {ngo["distance"]} km
                </div>

                <div class="detail">
                    📦 <b>Capacity:</b>
                    {ngo["capacity"]} meals
                </div>

                <div class="detail">
                    ❤️ <b>Current Need:</b>
                    {ngo["need"]}
                </div>

                <div class="detail">
                    🎯 <b>Match Score:</b>
                    {ngo["match_score"]}/100
                </div>

                <br>

                <div class="info">

                    <b>Recommended Action</b><br>

                    Prioritize pickup and redistribution
                    through this NGO.

                </div>

            </div>
            """, unsafe_allow_html=True)


        # ----------------------------------------------------
        # MATCH TABLE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            '🎯 NGO Match Ranking'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Candidate organizations ranked by intelligent match score.'
            '</div>',
            unsafe_allow_html=True
        )


        df = pd.DataFrame(matches)

        df = df[
            [
                "name",
                "distance",
                "capacity",
                "need",
                "match_score"
            ]
        ]

        df.columns = [
            "NGO",
            "Distance (km)",
            "Capacity",
            "Need",
            "Match Score"
        ]


        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # DECISION PIPELINE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            'How the Decision Was Made'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="workflow">

            <div class="workflow-item">
                <div class="workflow-icon">🍱</div>
                <div class="workflow-text">DONATION</div>
            </div>

            <div class="arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">⏱️</div>
                <div class="workflow-text">URGENCY</div>
            </div>

            <div class="arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">📍</div>
                <div class="workflow-text">DISTANCE</div>
            </div>

            <div class="arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">📦</div>
                <div class="workflow-text">CAPACITY</div>
            </div>

            <div class="arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">❤️</div>
                <div class="workflow-text">NEED</div>
            </div>

            <div class="arrow">→</div>

            <div class="workflow-item">
                <div class="workflow-icon">🏆</div>
                <div class="workflow-text">BEST MATCH</div>
            </div>

        </div>
        """, unsafe_allow_html=True)


        st.markdown("")

        st.markdown("""
        <div class="info">

            <b>Prototype AI:</b>
            The current MVP uses a transparent
            multi-factor scoring engine.
            Future versions can use historical
            redistribution data to train machine-learning
            models for predictive matching and demand forecasting.

        </div>
        """, unsafe_allow_html=True)


# ============================================================
# IMPACT
# ============================================================

elif page == "📊 Impact":

    st.markdown("""
    <div class="hero">

        <span class="badge">
            IMPACT DASHBOARD
        </span>

        <h1>
            Rescue Impact
        </h1>

        <h2>
            Every rescued meal counts.
        </h2>

        <p>
            Track food donations and completed
            redistributions through the platform.
        </p>

    </div>
    """, unsafe_allow_html=True)


    donations = get_donations()


    total = len(donations)

    delivered = sum(
        1 for d in donations
        if d[7] == "Delivered"
    )

    pending = total - delivered

    rescued = sum(
        d[2]
        for d in donations
        if d[7] == "Delivered"
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">🍱</div>

            <div class="metric-label">
                TOTAL DONATIONS
            </div>

            <div class="metric-value">
                {total}
            </div>

        </div>
        """, unsafe_allow_html=True)


    with c2:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">🍽️</div>

            <div class="metric-label">
                MEALS RESCUED
            </div>

            <div class="metric-value">
                {rescued}
            </div>

        </div>
        """, unsafe_allow_html=True)


    with c3:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">✅</div>

            <div class="metric-label">
                DELIVERED
            </div>

            <div class="metric-value">
                {delivered}
            </div>

        </div>
        """, unsafe_allow_html=True)


    with c4:
        st.markdown(f"""
        <div class="metric">

            <div class="metric-icon">⏳</div>

            <div class="metric-label">
                PENDING
            </div>

            <div class="metric-value">
                {pending}
            </div>

        </div>
        """, unsafe_allow_html=True)


    st.markdown("")


    if donations:

        st.markdown(
            '<div class="section-title">'
            'Donation Activity'
            '</div>',
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


        st.markdown(
            '<div class="section-title">'
            'Update Delivery'
            '</div>',
            unsafe_allow_html=True
        )


        col1, col2 = st.columns([3, 1])


        with col1:

            donation_id = st.number_input(
                "Donation ID",
                min_value=1,
                step=1
            )


        with col2:

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                "✅ DELIVERED",
                use_container_width=True
            ):

                mark_delivered(
                    donation_id
                )

                st.success(
                    "Donation marked as delivered!"
                )

                st.rerun()


    else:

        st.markdown("""
        <div class="info">

            🍱 No donations have been created yet.

            <br><br>

            Create your first donation to start
            building your impact dashboard.

        </div>
        """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">

    🍱 <b>FOOD RESCUE AI 4.0</b>

    <br>

    AI-Powered Intelligent Food Waste Management
    & Redistribution System

    <br><br>

    MSME Innovation Prototype
    •
    Proposed features are clearly distinguished
    from implemented MVP functionality.

</div>
""", unsafe_allow_html=True)
