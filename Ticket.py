import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ITSMTicket Counter", layout="wide")

st.title("ITSM Ticket Counter")
st.markdown("Upload multiple Excel files to count tickets for selected customers.")

# ---------- TARGET CUSTOMERS ----------
target_customers = [
    "Georgia Pacific",
    "Victaulic",
    "Sandvik",
    "Wittur",
    "Jacquet Brossard",
    "Solvinity",
    "Bega Cheese",
    "Guardian",
    "CL International",
    "Kongsberg"
]

# ---------- SESSION STATE ----------
if "data" not in st.session_state:
    st.session_state.data = None

# ---------- SIDEBAR ----------
st.sidebar.title("📊 ITSM Counter")
#st.sidebar.write("🎯 Target Customers:")
st.sidebar.write(target_customers)

page = st.sidebar.radio("Navigation", ["📤 Upload", "📊 Dashboard", "ℹ️ About"])

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
    print(files)
    if files != []:
            
        #try:
            # all_dfs = []

            # for file in files:
            #     #with pd.ExcelFile("QM Summary Report March 2026.xlsx") as xls:
            #     #file.seek(0)  # Reset file pointer to the beginning
            #     #df = pd.read_excel(xls, file)
            #     df = pd.read_excel(file, sheet_name=4)

            #     #df = pd.read_excel(file, sheet_name="Coverage")  # read with no header
            #     #sheetnames = pd.read_excel(file, sheet_name=None).keys()
            #     #print(f"Sheet names in {file.name}: {sheetnames}")
            #     #print(df.head(10))  # see the first 10 rows raw
            #     #print(file.type)
            #     #df.columns = df.columns.astype(str).str.strip()
            #     #df.columns = df.columns.astype(str).str.strip()
            #     df.columns = df.columns.str.strip()
            #     print(df.columns) 
            #     print(df.dtypes)      
                
            #     if 'Customer Name' not in df.columns:
                    
            #         st.warning(f"⚠️ 'Customer Name' column not found in {file.name}")
                    
            #         continue
            #     # df['Customer Name'] = df['Customer Name'].astype(object).fillna("").astype(str).str.replace('old', 'new').str.strip()
            #     # #df['Customer Name'] = df['Customer Name'].fillna("").astype(str).str.replace('old', 'new').str.strip()
            #     # #df['Customer Name'] = df['Customer Name'].fillna("").astype(str).str.replace('old', 'new').strip() 
            #     df['Customer Name'] = df['Customer Name'].fillna("").astype(str).str.strip()    
            #     all_dfs.append(df)

            # if not all_dfs:
            #     st.error("No valid files uploaded.")
            # else:
            #     #  COMBINE ALL FILES
            #     combined_df = pd.concat(all_dfs, ignore_index=True)

            #     #  FILTER TARGET CUSTOMERS (partial match)
            #     #pattern = '|'.join(target_customers)
                
            #     pattern = '|'.join(map(re.escape, target_customers))
                
            #     filtered_df = combined_df[
            #         combined_df['Customer Name'].str.contains(pattern, case=False, na=False)
            #     ]

            #     # 📊 COUNT TICKETS
            #     counts = filtered_df['Customer Name'].value_counts().reset_index()
            #     counts.columns = ['Customer', 'Ticket Count']

            #     # 💾SAVE TO SESSION
            #     st.session_state.data = {
            #         "raw": combined_df,
            #         "filtered": filtered_df,
            #         "counts": counts
            #     }

            #     st.success("✅ Files uploaded and combined successfully :> !")

            #     print(all_dfs)
        import re

        all_dfs = []

        for file in files:
            try:
                xls = pd.ExcelFile(file)

                # 🔍 Look for a sheet that contains "Customer"
                selected_sheet = None

                for sheet in xls.sheet_names:
                    temp_df = pd.read_excel(xls, sheet_name=sheet, nrows=5)

                    cols = [c.lower() for c in temp_df.columns.astype(str)]

                    if any("customer" in c for c in cols):
                        selected_sheet = sheet
                        break

                if selected_sheet is None:
                    st.warning(f"⚠️ No valid sheet found in {file.name}")
                    continue

                # ✅ Read the correct sheet
                df = pd.read_excel(xls, sheet_name=selected_sheet)

                df.columns = df.columns.astype(str).str.strip()

                if 'Customer Name' not in df.columns:
                    st.warning(f"⚠️ 'Customer Name' not found in {file.name}")
                    continue

                df['Customer Name'] = df['Customer Name'].fillna("").astype(str).str.strip()

                all_dfs.append(df)

                st.success(f"✅ Loaded '{selected_sheet}' from {file.name}")

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

            if not all_dfs:
                st.error("No valid files uploaded.")
            else:
                #  COMBINE ALL FILES
                combined_df = pd.concat(all_dfs, ignore_index=True)

                #  FILTER TARGET CUSTOMERS (partial match)
                #pattern = '|'.join(target_customers)
                
                pattern = '|'.join(map(re.escape, target_customers))
                
                filtered_df = combined_df[
                    combined_df['Customer Name'].str.contains(pattern, case=False, na=False)
                ]

                # 📊 COUNT TICKETS
                counts = filtered_df['Customer Name'].value_counts().reset_index()
                counts.columns = ['Customer', 'Ticket Count']

                # 💾SAVE TO SESSION
                st.session_state.data = {
                    "raw": combined_df,
                    "filtered": filtered_df,
                    "counts": counts
                }

                st.success("✅ Files uploaded and combined successfully :> !")

                print(all_dfs)

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
        counts = data["counts"]

        # ---------- METRICS ----------
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Tickets", len(df))
        col2.metric("Tracked Customers", counts.shape[0])
        col3.metric(
            "Top Customer",
            counts.iloc[0]['Customer'] if not counts.empty else "N/A"
        )

        st.markdown("---")

        # ---------- TABLE + CHART ----------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Ticket Summary")
            st.dataframe(counts, use_container_width=True)

        with col2:
            st.subheader("📈 Ticket Distribution")

            if not counts.empty:
                fig, ax = plt.subplots()
                ax.bar(counts['Customer'], counts['Ticket Count'])
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.info("No data available.")

        st.markdown("---")

        # ---------- TOP CUSTOMERS ----------
        st.subheader("op Customers")

        top5 = counts.head(5)

        for _, row in top5.iterrows():
            st.info(f"{row['Customer']} — {row['Ticket Count']} tickets")

        # ---------- DOWNLOAD ----------
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