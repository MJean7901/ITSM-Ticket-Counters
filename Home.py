import streamlit as st

st.set_page_config(
    page_title="Service Desk Toolkit",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Service Desk Toolkit")
st.write("Select an application below:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎫 ITSM Ticket Counter")
    st.write("Count and analyze ITSM tickets from uploaded reports.")
    if st.button("Open ITSM Counter"):
        st.session_state.page = "itsm"

with col2:
    st.subheader("🚨 PureService Alert Counter")
    st.write("Analyze and summarize PureService alerts.")
    if st.button("Open Alert Counter"):
        st.session_state.page = "alert"

# Initialize state
if "page" not in st.session_state:
    st.session_state.page = None

# Load selected app
if st.session_state.page == "itsm":
    import PSTicket
    itsm_app.run()

elif st.session_state.page == "alert":
    import Ticket
    alert_app.run()