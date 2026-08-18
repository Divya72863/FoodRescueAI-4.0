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


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Food Rescue AI 4.0",
    page_icon="🍱",
    layout="wide"
)


# -----------------------------
# DATABASE
# -----------------------------

create_database()


# -----------------------------
# HEADER
# -----------------------------

st.title("🍱 Food Rescue AI 4.0")

st.subheader(
    "AI-Powered Intelligent Food Waste Management & Redistribution System"
)

st.write(
    "Connecting surplus food with organizations that can redistribute it."
)

st.divider()


# -----------------------------
# SIDEBAR
# -----------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🍱 Create Donation",
        "🤖 AI Recommendation",
        "📊 Impact Dashboard"
    ]
)


# -----------------------------
# DASHBOARD
# -----------------------------

if page == "🏠 Dashboard":

    st.header("Food Rescue Dashboard")

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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Donations",
            total_donations
        )

    with col2:
        st.metric(
            "Meals Rescued",
            total_meals
        )

    with col3:
        st.metric(
            "Completed Deliveries",
            delivered
        )

    st.divider()

    st.info(
        "💡 Demo system: NGO information and recommendations "
        "are prototype data and do not represent actual partnerships."
    )


# -----------------------------
# CREATE DONATION
# -----------------------------

elif page == "🍱 Create Donation":

    st.header("🍱 Create Food Donation")

    food_name = st.text_input(
        "Food Name",
        placeholder="Example: Biryani"
    )

    quantity = st.number_input(
        "Quantity / Meals",
        min_value=1,
        value=50
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

    donor_location = st.text_input(
        "Donor Location",
        placeholder="Example: Hyderabad"
    )

    st.write("")

    if st.button(
        "🤖 Analyze Donation",
        use_container_width=True
    ):

        if not food_name:
            st.warning(
                "Please enter the food name."
            )

        elif not donor_location:
            st.warning(
                "Please enter the donor location."
            )

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
                "Donation analyzed successfully!"
            )

            st.rerun()


# -----------------------------
# AI RECOMMENDATION
# -----------------------------

elif page == "🤖 AI Recommendation":

    st.header("🤖 AI Donation Analysis")

    if "analysis" not in st.session_state:

        st.info(
            "Create a donation first to generate an AI recommendation."
        )

    else:

        result = st.session_state["analysis"]
        ngo = st.session_state["ngo"]

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("AI Analysis")

            st.metric(
                "Pickup Priority",
                result["priority"]
            )

            st.metric(
                "Decision Score",
                result["score"]
            )

            st.write("### Reasoning")

            for reason in result["reasons"]:
                st.write("•", reason)

        with col2:

            st.subheader("🤝 Recommended NGO")

            st.write(
                f"### {ngo['name']}"
            )

            st.write(
                f"📍 Distance: {ngo['distance']} km"
            )

            st.write(
                f"📦 Capacity: {ngo['capacity']}"
            )

            st.write(
                f"❤️ Current Need: {ngo['need']}"
            )

            st.success(
                "Recommended for pickup"
            )


# -----------------------------
# IMPACT DASHBOARD
# -----------------------------

elif page == "📊 Impact Dashboard":

    st.header("📊 Impact Dashboard")

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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Meals Rescued",
            total_meals
        )

    with col2:
        st.metric(
            "Deliveries",
            delivered
        )

    with col3:
        st.metric(
            "Donations",
            len(donations)
        )

    st.divider()

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
            use_container_width=True
        )

        st.subheader("Update Delivery Status")

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
            "No donations have been created yet."
        )
