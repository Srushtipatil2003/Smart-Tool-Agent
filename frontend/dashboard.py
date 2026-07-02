# frontend/dashboard.py
import streamlit as st
import requests
import pandas as pd

# =====================================================================
# SYSTEM PAGE SETTINGS & LOGO UI
# =====================================================================
st.set_page_config(page_title="Smart City Toll Dashboard", page_icon="🚦", layout="wide")

st.title("Smart City Automated Toll Enforcement Portal")
st.subheader("Connected Vehicle Telemetry Core Scanner & Billing Interface")
st.markdown("---")

# =====================================================================
# SIDEBAR CONTROLLER PANEL
# =====================================================================
st.sidebar.header("Toll Station Controls")
vehicle_id = st.sidebar.text_input("Scan Vehicle License Plate ID:", value="MH-12-NX-4567")

st.sidebar.markdown("""
### Operator Guidance:
1. Input the vehicle registration ID scanned at the gate.
2. Upload the extracted internal `.csv` telemetry log file.
3. Click **Process Invoice** to initiate the AI reasoning loop.
""")

# =====================================================================
# MAIN WORKSPACE APPLICATION CONTENT
# =====================================================================
# Initialize a layout splitting the landing zone into two equal horizontal view columns
col1, col2 = st.columns(2)

with col1:
    st.header("Step 1: Extract Telemetry Data")
    uploaded_file = st.file_uploader("Upload Onboard Recorder Log (.csv)", type=["csv"])

    if uploaded_file is not None:
        st.success("File uploaded successfully into scanner memory buffers.")
        # Render a preview data matrix panel table right on screen for the operator to verify
        df_preview = pd.read_csv(uploaded_file)
        st.dataframe(df_preview, use_container_width=True)
        # Rewind the file position marker pointer back to zero so requests can read it cleanly next
        uploaded_file.seek(0)

with col2:
    st.header("Step 2: AI Toll Inspector Slip")

    # Render a disable lock switch parameter button until a file is actually present to evaluate
    if uploaded_file is not None:
        if st.button("Process Toll & Run Deductions", type="primary"):
            with st.spinner("Agent evaluating laws, processing logs, and running calculations..."):
                try:
                    # 1. Package the binary file contents into a standard HTTP upload stream wrapper
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    params = {"vehicle_id": vehicle_id}

                    # 2. Make an absolute network API link call request over to our live FastAPI server port
                    backend_api_url = "http://localhost:8000/process-toll/"
                    api_response = requests.post(backend_api_url, params=params, files=files)

                    if api_response.status_code == 200:
                        data = api_response.json()

                        if data.get("status") == "success":

                            st.success("Toll processing workflow completed successfully!")

                            # Render out the raw markdown string text report passed back word-for-word from Gemini
                            st.markdown("Official Toll Audit Log Report:")
                            st.info(data.get("report"))
                        else:
                            st.error(f"Backend Engine Refusal: {data.get('message')}")
                    else:
                        st.error(f"HTTP Connection Failure Code: {api_response.status_code}")

                except Exception as e:
                    st.error(f"Could not connect to the FastAPI backend API service. Is it offline? Detail: {e}")
    else:
        st.info("Awaiting sensor telemetry log upload data from the left input deck panel.")
