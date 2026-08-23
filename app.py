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
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

create_database()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍱 Food Rescue AI 4.0")

st.sidebar.write(
    "AI-Powered Intelligent Food Waste "
    "Management & Redistribution System"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🍱 Create Donation",
        "🤖 AI Recommendation",
        "📊 Impact Dashboard"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.title("🍱 Food Rescue AI 4.0")

    st.subheader(
        "AI-Powered Intelligent Food Waste "
        "Management & Redistribution System"
    )

    st.write(
        "Connecting surplus food with organizations "
        "that can redistribute it."
    )

    st.divider()

    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    st.subheader("🔄 How It Works")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.write("🍽️")
        st.write("Surplus Food")

    with col2:
        st.write("→")

    with col3:
        st.write("🤖")
        st.write("AI Analysis")

    with col4:
        st.write("→")

    with col5:
        st.write("🤝")
        st.write("NGO Matching")

    st.divider()

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

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

    pending = total_donations - delivered

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🍱 Total Donations",
            total_donations
        )

    with col2:
        st.metric(
            "🍽️ Meals Rescued",
            total_meals
        )

    with col3:
        st.metric(
            "🚚 Deliveries",
            delivered
        )

    with col4:
        st.metric(
            "⏳ Pending",
            pending
        )

    st.divider()

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    st.subheader("🚀 Core Features")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("### 🤖 AI Priority Analysis")

        st.write(
            "Analyze preparation time, quantity, "
            "storage condition and food type to "
            "determine pickup priority."
        )

    with col2:

        st.markdown("### 🤝 Intelligent NGO Matching")

        st.write(
            "Match donations with suitable NGOs "
            "using distance, capacity and current need."
        )

    with col3:

        st.markdown("### 📊 Impact Tracking")

        st.write(
            "Track donations, rescued meals and "
            "completed deliveries."
        )


# ============================================================
# CREATE DONATION
# ============================================================

elif page == "🍱 Create Donation":

    st.title("🍱 Create Food Donation")

    st.write(
        "Enter the surplus food information below."
    )

    st.divider()

    # --------------------------------------------------------
    # DONATION FORM
    # --------------------------------------------------------

    food_name = st.text_input(
        "Food Name",
        placeholder="Example: Biryani"
    )

    quantity = st.number_input(
        "Quantity / Meals",
        min_value=1,
        value=50,
        step=1
    )

    preparation_time = st.time_input(
        "Preparation Time"
    )

    storage_condition = st.selectbox(
        "Storage Condition",
        [
            "Refrigerated",
            "Room Temperature",
            "Frozen"
        ]
    )

    donor_location = st.selectbox(
        "Donor Location",
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
        "Donor Type",
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

    st.divider()

    # --------------------------------------------------------
    # ANALYZE DONATION
    # --------------------------------------------------------

    if st.button(
        "🤖 Analyze Donation & Find NGO",
        use_container_width=True
    ):

        if not food_name.strip():

            st.error(
                "Please enter the food name."
            )

        else:

            # AI ANALYSIS

            result = analyze_donation(
                food_name,
                quantity,
                preparation_time,
                storage_condition
            )

            # NGO MATCHING

            ngo, all_matches = recommend_ngo(
                donor_location=donor_location,
                quantity=quantity,
                priority=result["priority"]
            )

            # SAVE DONATION

            add_donation(
                food_name,
                quantity,
                str(preparation_time),
                storage_condition,
                result["priority"],
                ngo["name"]
            )

            # SAVE RESULTS

            st.session_state["analysis"] = result

            st.session_state["ngo"] = ngo

            st.session_state["all_matches"] = all_matches

            st.session_state["donor_location"] = donor_location

            st.session_state["donor_type"] = donor_type

            st.success(
                "✅ Donation successfully analyzed!"
            )

            st.info(
                "Go to 'AI Recommendation' "
                "to view the complete result."
            )


# ============================================================
# AI RECOMMENDATION
# ============================================================

elif page == "🤖 AI Recommendation":

    st.title("🤖 AI Recommendation")

    st.write(
        "Intelligent analysis of the donation "
        "and NGO matching result."
    )

    st.divider()

    # --------------------------------------------------------
    # CHECK IF ANALYSIS EXISTS
    # --------------------------------------------------------

    if "analysis" not in st.session_state:

        st.warning(
            "No donation has been analyzed yet."
        )

        st.info(
            "Go to 'Create Donation' and analyze "
            "a food donation first."
        )

    else:

        result = st.session_state["analysis"]

        ngo = st.session_state["ngo"]

        all_matches = st.session_state.get(
            "all_matches",
            []
        )

        donor_location = st.session_state.get(
            "donor_location",
            "Hyderabad"
        )

        # ----------------------------------------------------
        # AI RESULT
        # ----------------------------------------------------

        st.subheader("🧠 AI Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Pickup Priority",
                result["priority"]
            )

        with col2:

            st.metric(
                "Decision Score",
                result["score"]
            )

        with col3:

            st.metric(
                "Hours Since Preparation",
                result.get(
                    "hours_since_preparation",
                    0
                )
            )

        st.divider()

        # ----------------------------------------------------
        # DECISION REASONS
        # ----------------------------------------------------

        st.subheader(
            "📋 Decision Factors"
        )

        for reason in result["reasons"]:

            st.write(
                "✓",
                reason
            )

        st.divider()

        # ----------------------------------------------------
        # NGO RECOMMENDATION
        # ----------------------------------------------------

        st.subheader(
            "🤝 Recommended NGO"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**NGO:**",
                ngo["name"]
            )

            st.write(
                "**Location:**",
                ngo["location"]
            )

            st.write(
                "**Distance:**",
                f'{ngo["distance"]} km'
            )

        with col2:

            st.write(
                "**Capacity:**",
                f'{ngo["capacity"]} meals'
            )

            st.write(
                "**Current Need:**",
                ngo["need"]
            )

            st.write(
                "**Match Score:**",
                f'{ngo["match_score"]}/100'
            )

        st.divider()

        # ----------------------------------------------------
        # MATCH RANKING
        # ----------------------------------------------------

        st.subheader(
            "🎯 NGO Match Ranking"
        )

        if all_matches:

            match_df = pd.DataFrame(
                all_matches
            )

            match_df = match_df[
                [
                    "name",
                    "distance",
                    "capacity",
                    "need",
                    "match_score"
                ]
            ]

            match_df.columns = [
                "NGO",
                "Distance (km)",
                "Capacity",
                "Need",
                "Match Score"
            ]

            st.dataframe(
                match_df,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # ----------------------------------------------------
        # DECISION FLOW
        # ----------------------------------------------------

        st.subheader(
            "🔄 Decision Flow"
        )

        st.write(
            "🍱 Donation"
            " → "
            "🤖 AI Analysis"
            " → "
            "🚨 Priority"
            " → "
            "🤝 NGO Matching"
            " → "
            "🚚 Pickup"
        )

        st.divider()

        st.info(
            "Prototype Note: The current MVP uses "
            "a transparent scoring-based intelligent "
            "decision engine. Future versions can "
            "integrate machine-learning models using "
            "historical redistribution data."
        )


# ============================================================
# IMPACT DASHBOARD
# ============================================================

elif page == "📊 Impact Dashboard":

    st.title("📊 Impact Dashboard")

    st.write(
        "Track food donations and redistribution activity."
    )

    st.divider()

    donations = get_donations()

    total_donations = len(donations)

    delivered = sum(
        1
        for donation in donations
        if donation[7] == "Delivered"
    )

    pending = total_donations - delivered

    rescued_meals = sum(
        donation[2]
        for donation in donations
        if donation[7] == "Delivered"
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🍱 Donations",
            total_donations
        )

    with col2:

        st.metric(
            "🍽️ Meals Rescued",
            rescued_meals
        )

    with col3:

        st.metric(
            "✅ Delivered",
            delivered
        )

    with col4:

        st.metric(
            "⏳ Pending",
            pending
        )

    st.divider()

    # --------------------------------------------------------
    # DONATION TABLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Donation Records"
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

        st.divider()

        # ----------------------------------------------------
        # UPDATE DELIVERY
        # ----------------------------------------------------

        st.subheader(
            "🚚 Update Delivery Status"
        )

        donation_id = st.number_input(
            "Donation ID",
            min_value=1,
            step=1
        )

        if st.button(
            "✅ Mark as Delivered"
        ):

            mark_delivered(
                donation_id
            )

            st.success(
                "Donation marked as delivered!"
            )

            st.rerun()

    else:

        st.info(
            "No donations available yet. "
            "Create a donation to begin."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🍱 Food Rescue AI 4.0 | "
    "AI-Powered Intelligent Food Waste Management "
    "& Redistribution System"
)
