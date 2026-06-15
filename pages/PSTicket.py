import streamlit as st
import pandas as pd
import re
from datetime import datetime
 
def run():
        
    def count_shift(dates):
        t = []
        for a in dates:
            temp = a.split()
            # time.append(temp[1].split(':'))
            t.append(temp[1])
        return t
    
    def check_timezone(time):
        time_zone = {
            'apac':"6:30",
            'emea':"14:30",
            'us1':"22:30",
            'us2':"00:00"
        }
            
        timezone = {k: datetime.strptime(v, "%H:%M").time() for k,v in time_zone.items()}
    
        if time >= timezone["apac"] and time < timezone["emea"]:
            return "apac"
        elif time >= timezone["emea"] and time < timezone["us1"]:
            return "emea"
        elif (time >= timezone["us2"] and time < timezone["apac"]) or time >= timezone["us1"]:
            return "us"
    
    # ---------- PAGE CONFIG ----------
    st.set_page_config(page_title="ITSMTicket Counter", layout="wide")
    
    st.title("PureService Ticket Counter")
    st.markdown("Upload multiple Excel files to count the tickets in PureService")
    
    # ---------- SESSION STATE ----------
    if "data" not in st.session_state:
        st.session_state.data = None
    
    # ---------- SIDEBAR ----------
    st.sidebar.title("📊 PureService Ticket Counter")
    #st.sidebar.write("🎯 Target Customers:")
    # st.sidebar.write(target_customers)
    
    page = st.sidebar.radio("Navigation", ["📤 Upload", "📊 Dashboard", "ℹ️ About"])
    
    # Upload
    if page == "📤 Upload":
        st.header("📤 Upload Excel Files")
    
        files = st.file_uploader(
            "Choose Excel files",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True
        )
    
        all_dfs = []
        for file in files:
            try:
                df = pd.read_csv(file)
    
                all_dfs.append(df.loc[:, ["Subject", "Company", "Created date"]])
    
    
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
    
            if not all_dfs:
                st.error("No valid files uploaded.")
            else:
                # combine all the files
                combined_df = pd.concat(all_dfs, ignore_index=True)
    
                # initializing the variables and dictionaries
                dates = combined_df["Created date"]
                customers_df = combined_df.loc[:, ["Company","Created date"]]
                time = []
                apac = dict()
                emea = dict()
                us = dict()
                customers = dict()
    
                # counts the number of tickets per customer
                for i in customers_df["Company"]:
                    if i in customers.keys():
                        customers[i] += 1
                    else:
                        customers[i] = 1
    
    
                # counts the number of tickets per shift
                time = count_shift(dates)
    
                counter = {
                    'apac':0,
                    'emea':0,
                    'us':0
                }
            
                for i in time:
                    time_obj = datetime.strptime(i, "%H:%M").time()
                    if check_timezone(time_obj) == "apac":
                        counter["apac"] +=1
                    elif check_timezone(time_obj) == "emea":
                        counter["emea"] +=1
                    elif check_timezone(time_obj) == "us":
                        counter["us"] +=1
    
                # counts the number of tickets per customer and per shift
                n = count_shift(customers_df["Created date"])
                # print(n)
                for j in range(len(n)):
                    t = datetime.strptime(n[j], "%H:%M").time()
                    company = customers_df.loc[j, "Company"]
                    if check_timezone(t) == "apac":
                        if company in apac.keys():
                            apac[company] += 1
                        else:
                            apac[company] = 1
                    elif check_timezone(t) == "emea":
                        if company in emea.keys():
                            emea[company] += 1
                        else:
                            emea[company] = 1
                    elif check_timezone(t) == "us":
                        if company in us.keys():
                            us[company] += 1
                        else:
                            us[company] = 1
    
                
                print(counter)
                sorted_customers = dict(sorted(customers.items(), key=lambda item: str(item[0])))
                sorted_apac = dict(sorted(apac.items(), key=lambda item: str(item[0])))
                sorted_emea = dict(sorted(emea.items(), key=lambda item: str(item[0])))
                sorted_us = dict(sorted(us.items(), key=lambda item: str(item[0])))
            
                # print(sorted_customers)
                # print("APAC")
                # print(apac)
                # print("EMEA")
                # print(emea)
                # print("US")
                # print(us)
    
    
                # 💾SAVE TO SESSION
                st.session_state.data = {
                    "ticket_shift" : counter,
                    "sorted_customer": sorted_customers,
                    "apac_customers" : sorted_apac,
                    "emea_customers" : sorted_emea,
                    "us_customers" : sorted_us
                }
    
                st.success("✅ Files uploaded and combined successfully :> !")
    
    if page == "📊 Dashboard":
        if st.session_state.data is None:
            st.write("No data. Upload files")
        else:
            # ticket_per_shift = st.session_state.data["ticket_shift"]
            # print(ticket_per_shift)
            # shift_df = pd.DataFrame.from_dict(ticket_per_shift, orient="index")
            # st.write(shift_df)
            # # st.write(shift_df)
            table_titles = [
                "Tickets per Shift", "Tickets per Customer", "Tickets in APAC",
                "Tickets in EMEA", "Tickets in US"
            ]
            num = 0
            for i in st.session_state.data:
                st.header(table_titles[num])
                temp = st.session_state.data[i]
                temp_df = pd.DataFrame.from_dict(temp, orient="index")
                st.write(temp_df)
                num += 1
                # st.write(shift_df)
                # st.write(st.session_state.data[i])