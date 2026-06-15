import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

def run():

    # ---------- PAGE CONFIG ----------
    st.set_page_config(page_title="ITSM Ticket Counter", layout="wide")

    # ---------- LOGIN FUNCTION ----------
    def login():
        st.title("🔐 Login Page")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_button = st.button("Login")

        if login_button:
            if username == "admin" and password == "password":
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")


    # ---------- SESSION STATE ----------
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "data" not in st.session_state:
        st.session_state.data = None

    # ---------- SHOW LOGIN PAGE FIRST ----------
    if not st.session_state.logged_in:
        login()
        st.stop()

    # ---------- MAIN APP ----------
    st.title("ITSM Ticket Counter")
    st.markdown("Upload multiple Excel files to count tickets for selected customers.")

    # ---------- TARGET CUSTOMERS ----------
    from rapidfuzz import process

    # ---------- CUSTOMER ALIASES ----------
    customer_mapping = {
        "Georgia Pacific": [
            "Georgia Pacific",
            "Georgia-Pacific",
            "Georgia",
            "Georgia Pacific LLC",
            "GP"
        ],
        "Victaulic": [
            "Victaulic",
            "Victaulic Inc",
            "Victaulic (EasyVista)"
        ],
        "Sandvik": [
            "Sandvik",
            "Sandvik Mining",
            "Sandvik Ltd"
        ],
        "Wittur": [
            "Wittur",
            "Wittur Group"
        ],
        "Jacquet Brossard": [
            "Jacquet Brossard",
            "Jacquet",
            "Brossard"
        ],
        "Solvinity": [
            "Solvinity",
            "Solvinity (Stork)",
            "Stork"
        ],
        "Bega Cheese": [
            "Bega Cheese",
            "Bega"
        ],
        "Guardian": [
            "Guardian",
            "Guardian Industries"
        ],
        "CL International": [
            "CL International",
            "CLI"
        ],
        "Kongsberg": [
            "Kongsberg",
            "Kongsberg Gruppen"
        ]
    }

    # Build alias lookup table
    alias_lookup = {}
    for standard_name, aliases in customer_mapping.items():
        for alias in aliases:
            alias_lookup[alias.lower()] = standard_name

    all_aliases = list(alias_lookup.keys())

    def normalize_customer(customer_name):
        if pd.isna(customer_name):
            return None

        customer_name = str(customer_name).strip().lower()

        # Exact or partial alias match
        for alias, standard_name in alias_lookup.items():
            if alias in customer_name:
                return standard_name

        # Fuzzy matching
        match = process.extractOne(
            customer_name,
            all_aliases,
            score_cutoff=80
        )

        if match:
            matched_alias = match[0]
            return alias_lookup[matched_alias]

        return None

    # ---------- SIDEBAR ----------
    st.sidebar.title("📊 ITSM Counter")

    # Logout Button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.write(list(customer_mapping.keys()))

    page = st.sidebar.radio(
        "Navigation",
        ["📤 Upload", "📊 Dashboard", "ℹ️ About"]
    )

    # ==============================
    # 📤 UPLOAD PAGE
    # ==============================
    if page == "📤 Upload":

        st.header("📤 Upload Excel Files")

        files = st.file_uploader(
            "Choose Excel files",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True
        )

        if files:

            all_dfs = []

            for file in files:
                try:
                    xls = pd.ExcelFile(file)

                    # Find sheet containing customer column
                    selected_sheet = None

                    for sheet in xls.sheet_names:
                        temp_df = pd.read_excel(
                            xls,
                            sheet_name=sheet,
                            nrows=5
                        )

                        cols = [
                            c.lower()
                            for c in temp_df.columns.astype(str)
                        ]

                        if any("customer" in c for c in cols):
                            selected_sheet = sheet
                            break

                    if selected_sheet is None:
                        st.warning(
                            f"⚠️ No valid sheet found in {file.name}"
                        )
                        continue

                    # Read selected sheet
                    df = pd.read_excel(
                        xls,
                        sheet_name=selected_sheet
                    )

                    df.columns = (
                        df.columns.astype(str).str.strip()
                    )

                    if 'Customer Name' not in df.columns:
                        st.warning(
                            f"⚠️ 'Customer Name' not found in {file.name}"
                        )
                        continue

                    df['Customer Name'] = (
                        df['Customer Name']
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    all_dfs.append(df)

                    st.success(
                        f"✅ Loaded '{selected_sheet}' from {file.name}"
                    )

                except Exception as e:
                    st.error(
                        f"❌ Error processing {file.name}: {e}"
                    )

            # AFTER LOOP
            if not all_dfs:
                st.error("No valid files uploaded.")

            else:
                # Combine all files
                combined_df = pd.concat(
                    all_dfs,
                    ignore_index=True
                )

                # # Filter target customers
                # pattern = '|'.join(
                #     map(re.escape, target_customers)
                # )

                # filtered_df = combined_df[
                #     combined_df['Customer Name']
                #     .str.contains(
                #         pattern,
                #         case=False,
                #         na=False
                #     )
                # ]

                # # Count tickets
                # counts = (
                #     filtered_df['Customer Name']
                #     .value_counts()
                #     .reset_index()
                # )

                # counts.columns = [
                #     'Customer',
                #     'Ticket Count'
                # ]
                
                # Filter target customers

                # ---------- NORMALIZE CUSTOMER NAMES ----------
                combined_df['Normalized Customer'] = (
                    combined_df['Customer Name']
                    .fillna("")
                    .astype(str)
                    .apply(normalize_customer)
                )

                # Keep only mapped customers
                filtered_df = combined_df[
                    combined_df['Normalized Customer'].notna()
                ].copy()

                # Count normalized customers
                counts = (
                    filtered_df['Normalized Customer']
                    .value_counts()
                    .reset_index()
                )

                counts.columns = [
                    "Customer",
                    "Ticket Count"
                ]

                # Save to session
                st.session_state.data = {
                    "raw": combined_df,
                    "filtered": filtered_df,
                    "counts": counts
                }

                st.success(
                    "✅ Files uploaded and combined successfully!"
                )

    # ==============================
    # 📊 DASHBOARD PAGE
    # ==============================
    elif page == "📊 Dashboard":

        st.header("📊 Ticket Analytics Dashboard")

        if st.session_state.data is None:
            st.warning("⚠️ Please upload files first.")

        else:
            data = st.session_state.data
            df = data["raw"]
            filtered_df = data["filtered"]
            counts = data["counts"]

            # Metrics
            col1, col2, col3 = st.columns(3)

            col1.metric("Total Tickets", len(df))

            col2.metric(
                "Tracked Customers",
                counts.shape[0]
            )
            st.markdown("---")

    # ---------- MONTHLY TICKET TREND BY SHIFT & CUSTOMER ----------
        if (
            'Shift' in filtered_df.columns and
            'Date' in filtered_df.columns
        ):
            st.subheader("🌍 Monthly Ticket Trend by Shift & Customer")

            trend_df = filtered_df.copy()

            # Clean Shift column
            trend_df['Shift'] = (
                trend_df['Shift']
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )

            trend_df['Shift'] = trend_df['Shift'].replace({
                "AMER": "US",
                "AMERICAS": "US",
                "NORTH AMERICA": "US"
            })

            # Convert Date
            trend_df['Date'] = pd.to_datetime(trend_df['Date'], errors='coerce')
            trend_df = trend_df.dropna(subset=['Date'])

            # Keep only APAC / EMEA / US
            trend_df = trend_df[trend_df['Shift'].isin(['APAC', 'EMEA', 'US'])]

            # Create Month-Year field
            trend_df['Month'] = trend_df['Date'].dt.strftime('%Y-%m')

            # Normalize Customer Name for matching
            trend_df['Customer Name'] = trend_df['Customer Name'].str.strip()

            # --- Shift filter ---
            shift_options = ['APAC', 'EMEA', 'US']
            selected_shift = st.selectbox("Filter by Shift", options=["All"] + shift_options)

            if selected_shift != "All":
                trend_df = trend_df[trend_df['Shift'] == selected_shift]

            # --- Customer filter ---
            customer_options = sorted(
                trend_df['Normalized Customer']
                .dropna()
                .unique()
                .tolist()
            )
            selected_customers = st.multiselect(
                "Filter by Customer",
                options=customer_options,
                default=customer_options[:5] if len(customer_options) >= 5 else customer_options
            )

            if selected_customers:
                trend_df = trend_df[
                    trend_df['Normalized Customer']
                    .isin(selected_customers)
                ]

            # Group by Month + Shift + Customer
            trend_counts = (
                trend_df
                .groupby(['Month', 'Shift', 'Normalized Customer'])
                .size()
                .reset_index(name='Ticket Count')
            )

            # Create a combined label: "APAC - Georgia Pacific"
            trend_counts['Shift_Customer'] = (
                trend_counts['Shift'] +
                " — " +
                trend_counts['Normalized Customer']
            )

            # Pivot for line chart
            pivot_df = (
                trend_counts
                .pivot_table(
                    index='Month',
                    columns='Shift_Customer',
                    values='Ticket Count',
                    aggfunc='sum'
                )
                .fillna(0)
                .sort_index()
            )

            # Show data table
            st.dataframe(pivot_df, use_container_width=True)

            # Draw line chart
            fig, ax = plt.subplots(figsize=(12, 6))

            # Color map per shift
            shift_colors = {
                'APAC': 'green',
                'EMEA': 'steelblue',
                'US':   '#B8860B'
            }

            for col in pivot_df.columns:
                shift_label = col.split(" — ")[0]
                color = shift_colors.get(shift_label, 'gray')
                ax.plot(
                    pivot_df.index,
                    pivot_df[col],
                    marker='o',
                    linewidth=2,
                    label=col,
                    color=color,
                    alpha=0.75
                )

            ax.set_xlabel("Month")
            ax.set_ylabel("Number of Tickets")
            ax.set_title("Monthly Ticket Trend by Shift & Customer")
            ax.legend(
                title="Shift — Customer",
                bbox_to_anchor=(1.05, 1),
                loc='upper left',
                fontsize=8
            )
            #hhk
            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig)

            col3.metric(
                "Top Customer",
                counts.iloc[0]['Customer']
                if not counts.empty else "N/A"
            )

            st.markdown("---")

            # Table + Chart
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📋 Ticket Summary")
                st.dataframe(
                    counts,
                    use_container_width=True
                )

            with col2:
                st.subheader("📈 Ticket Distribution")

                if not counts.empty:
                    fig, ax = plt.subplots()

                    ax.bar(
                        counts['Customer'],
                        counts['Ticket Count']
                    )

                    plt.xticks(rotation=45)

                    st.pyplot(fig)

                else:
                    st.info("No data available.")

            st.markdown("---")

            # Top customers
            st.subheader("🏆 Top Customers")

            top5 = counts.head(5)

            for _, row in top5.iterrows():
                st.info(
                    f"{row['Customer']} — "
                    f"{row['Ticket Count']} tickets"
                )

            # Download button
            st.download_button(
                "⬇ Download Report",
                counts.to_csv(index=False),
                "ticket_summary.csv",
                "text/csv"
            )

    # ==============================
    # ℹ️ ABOUT PAGE
    # ==============================
    elif page == "ℹ️ About":

        st.header("ℹ️ About")

        st.markdown("""
        This app allows you to:

        - Upload multiple Excel files 📂
        - Combine ticket data 🔗
        - Filter specific customers 🎯
        - Count total tickets 📊
        - Visualize results 📈

        Built for IT Service Desk analytics.
        """)