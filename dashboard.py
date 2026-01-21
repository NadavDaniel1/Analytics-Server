import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
import certifi
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- 1. Page Config ---
st.set_page_config(page_title="Admin Portal", layout="wide") # Wide layout for better data visualization

# --- 2. Authentication Mechanism ---
if 'authenticated' not in st.session_state: 
    st.session_state.authenticated = False

def check_password():
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    if st.sidebar.button("Login"):
        if password == "1234": # this password should be securely managed in a real app
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.sidebar.error("Wrong password")

if not st.session_state.authenticated:
    st.title("🔒 Admin Portal Login")
    check_password()
    st.stop()

st.sidebar.success("Logged in as Admin ✅")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.title("🛠️ Analytics Admin Portal")

# --- 3. MongoDB Connection ---
# Fetch the URI securely from the environment variables
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    st.error("❌ Error: MONGO_URI not found in .env file!")
    st.stop()
    
ca = certifi.where() # Get the CA file for TLS connection

@st.cache_resource # Cache the connection to avoid reconnecting on every interaction
def init_connection():
    return MongoClient(MONGO_URI, tlsCAFile=ca)

client = init_connection() # Initialize MongoDB Client

def get_data():
    try:
        db = client["analytics_db"]
        data = list(db["events"].find())
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        
        # Convert timestamp to real datetime object
        if 'time' in df.columns:
            df['datetime'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = get_data()

# --- 4. Management Buttons (CRUD) ---
st.subheader("Manage Data") 
col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ DELETE ALL EVENTS (Reset DB)", type="primary"):
        db = client["analytics_db"]
        result = db["events"].delete_many({})
        st.success(f"Deleted {result.deleted_count} events.") # Show number of deleted events
        st.cache_resource.clear()
        st.rerun()

if st.button('🔄 Refresh Data'):
    st.rerun()

# --- 5. Dashboard & Charts ---
if not df.empty:
    st.markdown("---")
    
    # Identify column name (handles both 'event' and 'eventName')
    field_name = 'event' if 'event' in df.columns else 'eventName'

    # Key Metrics (KPIs)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Events", len(df))
    m2.metric("Unique Users", len(df['id'].unique()) if 'id' in df.columns else 0)
    m3.metric("Top Event", df[field_name].mode()[0] if field_name in df.columns else "N/A")

    st.markdown("---")

    # Chart Layout
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Event Distribution (Pie)")
        if field_name in df.columns:
            event_counts = df[field_name].value_counts().reset_index()
            event_counts.columns = ['Event Name', 'Count']
            fig_pie = px.pie(event_counts, values='Count', names='Event Name', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("Events Over Time (Line Chart)") 
        # 1️⃣ The new Line Chart requested
        if 'datetime' in df.columns and field_name in df.columns:
            # Create a copy to avoid modifying original data
            df_line = df.copy()
            df_line.set_index('datetime', inplace=True)
            
            # Group by minute (1min) and event type - counting events per minute
            events_over_time = df_line.groupby([pd.Grouper(freq='1min'), field_name]).size().reset_index(name='count')
            
            # Plot Line Chart
            fig_line = px.line(
                events_over_time, 
                x='datetime', 
                y='count', 
                color=field_name, 
                markers=True, # Add markers for visibility even with few data points
                title="Event Volume per Minute"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No timestamp data for line chart.")

    # Data Table
    st.markdown("---")
    st.subheader("📝 Raw Data Logs")
    display_df = df.drop(columns=['_id'], errors='ignore')
    cols = []
    if 'datetime' in display_df.columns: cols.append('datetime')
    if field_name in display_df.columns: cols.append(field_name)
    cols.extend([c for c in display_df.columns if c not in cols])
    st.dataframe(display_df[cols], use_container_width=True)

else:
    st.info("No data found. Waiting for events...")