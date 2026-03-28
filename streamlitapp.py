import streamlit as st
import requests
import datetime
import os
import sys
from supabase import create_client, Client
import folium
import uuid
from streamlit_folium import st_folium
import extra_streamlit_components as stx
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv(override=True)

BASE_URL = os.getenv("Backend_url")
# BASE_URL = "http://localhost:8000"  

# -----------------
# PAGE CONFIG & CSS
# -----------------
st.set_page_config(
    page_title="🌍 Travel Planner Agentic Application",
    page_icon="🌍",
    layout="wide", # Wider layout gives us room to put a map next to the chat
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Modern Gradient Background & Colors */
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    color: #f8fafc;
}
[data-testid="stSidebar"] {
    background-color: #1e293b;
    border-right: 1px solid #334155;
    padding-top: 2rem;
}
div.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
    width: 100%;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    color: white;
}
.chat-user {
    background-color: #334155;
    padding: 15px;
    border-radius: 12px 12px 0 12px;
    margin-bottom: 10px;
    border: 1px solid #475569;
}
.chat-ai {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 12px 12px 12px 0;
    margin-bottom: 25px;
    border: 1px solid #3b82f6;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
}
</style>
""", unsafe_allow_html=True)

# -----------------
# SUPABASE SETUP
# -----------------
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("⚠️ SUPABASE_URL and SUPABASE_KEY missing in .env file! Please add them to enable authentication.")
    st.stop()
else:
    supabase: Client = create_client(supabase_url, supabase_key)

# -----------------
# AUTH STATE
# -----------------
# Initialize the UI Cookie Writer component
cookie_manager = stx.CookieManager()

if "user" not in st.session_state:
    st.session_state.user = None

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# Auto-Login Interceptor: Scan hard drive for surviving cookies!
if st.session_state.user is None:
    saved_jwt = cookie_manager.get("supabase_jwt")
    if saved_jwt:
        try:
            # Rehydrate the identity object from the cookie
            res = supabase.auth.get_user(saved_jwt)
            if res and res.user:
                st.session_state.user = res.user
                st.session_state.access_token = saved_jwt
                
                # Pull all chat threads for the user, ordered chronologically
                db_response = supabase.table("chat_history").select("id, messages").eq("user_id", res.user.id).order("updated_at", desc=True).limit(1).execute()
                if len(db_response.data) > 0:
                    st.session_state.current_chat_id = db_response.data[0].get("id")
                    st.session_state.messages = db_response.data[0].get("messages", [])
                else:
                    st.session_state.current_chat_id = str(uuid.uuid4())
                    st.session_state.messages = []
                st.rerun() # Magic Bypass!
        except Exception:
            pass # Invalid/Expired Cookie: Fallthrough to Login rendering

# Auth Guard: If not logged in, show only Login Screen
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🌍 Welcome to FlowTravel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Your intelligent Agentic Travel Planner</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        auth_tab = st.radio("Select Action", ["Login", "Sign Up"], horizontal=True)
        with st.form(key="auth_form"):
            email = st.text_input("Email", placeholder="you@domain.com")
            password = st.text_input("Password", type="password")
            submit_auth = st.form_submit_button(auth_tab)
            
            if submit_auth:
                try:
                    if auth_tab == "Login":
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        st.session_state.access_token = res.session.access_token
                        
                        # Write the permanent Cookie into the browser to survive F5
                        cookie_manager.set("supabase_jwt", res.session.access_token)
                        
                        # Enterprise Chat Backup Fetch
                        try:
                            # Pull chat history from the DB if it exists
                            db_response = supabase.table("chat_history").select("id, messages").eq("user_id", res.user.id).order("updated_at", desc=True).limit(1).execute()
                            if len(db_response.data) > 0:
                                st.session_state.current_chat_id = db_response.data[0].get("id")
                                st.session_state.messages = db_response.data[0].get("messages", [])
                            else:
                                st.session_state.current_chat_id = str(uuid.uuid4())
                                st.session_state.messages = []
                        except Exception as fetch_e:
                            st.session_state.current_chat_id = str(uuid.uuid4())
                            st.session_state.messages = []
                            st.warning(f"Could not load previous chats: {fetch_e}")
                            
                        st.rerun()
                    else:
                        res = supabase.auth.sign_up({"email": email, "password": password})
                        st.success("Account created successfully! You can now log in.")
                except Exception as e:
                    # Show cleaner error messages based on PyTrue exceptions
                    if "Invalid login credentials" in str(e):
                        st.error("Invalid login credentials. Please check your email and password.")
                    else:
                        st.error(f"Authentication Failed: {e}")
    st.stop() # Halt rendering the rest of the application

# -----------------
# MAIN APPLICATION
# -----------------
with st.sidebar:
    st.markdown(f"**👤 Profile:**<br><span style='font-size:12px;color:#94a3b8;'>{st.session_state.user.email}</span>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Start New Trip", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        if "last_query" in st.session_state:
            del st.session_state.last_query
        try:
            # Reserve physical blank Row
            supabase.table("chat_history").insert({"id": st.session_state.current_chat_id, "user_id": st.session_state.user.id, "title": "New Trip", "messages": []}).execute()
        except: pass
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 🗂️ Your Trips")
    
    # Query all threads
    try:
        threads_response = supabase.table("chat_history").select("id, title").eq("user_id", st.session_state.user.id).order("updated_at", desc=True).execute()
        threads = threads_response.data
        if len(threads) == 0:
            st.caption("No history found.")
        else:
            for t in threads:
                is_active = (st.session_state.get("current_chat_id") == t["id"])
                prefix = "🟢 " if is_active else "🗺️ "
                if st.button(f"{prefix} {t['title']}", key=t['id'], use_container_width=True):
                    # Multi-Thread Switcher
                    st.session_state.current_chat_id = t["id"]
                    if "last_query" in st.session_state:
                        del st.session_state.last_query
                    
                    chat_data = supabase.table("chat_history").select("messages").eq("id", t["id"]).execute()
                    if len(chat_data.data) > 0:
                        st.session_state.messages = chat_data.data[0].get("messages", [])
                    st.rerun()
    except Exception as e:
        st.caption("Unable to fetch threads.")
        
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        supabase.auth.sign_out()
        cookie_manager.delete("supabase_jwt") # Annihilate the cookie
        st.session_state.user = None
        st.rerun()
        
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("- Type your travel destination and budget.")
    st.markdown("- The AI will fetch real-time weather and places.")
    st.markdown("- View your interactive Map.")
    st.markdown("- Download your itinerary as a calendar link!")

st.title("🌍 Plan Your Next Adventure")

if "messages" not in st.session_state:
    st.session_state.messages = []

# View Strategy: Chat on the Left, Map on the Right
main_col, map_col = st.columns([1.5, 1])

with main_col:
    # 1. Render Chat History safely without destroying formatting
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg.startswith("User:"):
                text = msg.replace("User: ", "", 1)
                with st.chat_message("user", avatar="👤"):
                    st.markdown(text)
            elif msg.startswith("Assistant:"):
                text = msg.replace("Assistant: ", "", 1)
                with st.chat_message("assistant", avatar="🌍"):
                    st.markdown(text)

    # We reserve a spot for the calendar buttons so they appear cleanly below the chat stream
    calendar_container = st.container()

    # 2. Render Chat Input form
    with st.form(key="query_form", clear_on_submit=True):
        user_input = st.text_input("Where to?", placeholder="e.g. Plan a 3-day budget trip to Tokyo")
        submit_button = st.form_submit_button("Generate Itinerary ✈️")

    # 3. Handle Submit
    if submit_button and user_input.strip():
        # Save query to session state so the map component can try to geolocate it
        st.session_state.last_query = user_input
        
        try:
            st.session_state.messages.append(f"User: {user_input}")
            with st.spinner("🤖 AI is orchestrating your trip..."):
                payload = {"messages": st.session_state.messages}
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"} if "access_token" in st.session_state else {}
                response = requests.post(f"{BASE_URL}/query", json=payload, headers=headers)
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer returned.")
                st.session_state.messages.append(f"Assistant: {answer}")
                
                # ------ NEW: ENTERPRISE DB BACKUP UPSERT -------
                try:
                    # Snag dynamic title from first message robustly
                    current_title = "New Trip"
                    if len(st.session_state.messages) > 0:
                        first_user_msg = [m for m in st.session_state.messages if m.startswith("User:")]
                        if first_user_msg:
                            current_title = first_user_msg[0].replace("User: ", "")[:25] + "..."
                            
                    supabase.table("chat_history").upsert({
                        "id": st.session_state.current_chat_id,
                        "user_id": st.session_state.user.id,
                        "title": current_title,
                        "messages": st.session_state.messages
                    }, on_conflict="id").execute()
                except Exception as db_e:
                    st.toast(f"Silent DB Backup Failed: {db_e}")
                # -----------------------------------------------
                
                # Re-run immediately to render the Assistant's message AND trigger the map draw
                st.rerun() 
            else:
                st.error(" Bot failed to respond: " + response.text)
        except Exception as e:
            st.error(f"The response failed due to {e}")

# -----------------
# DYNAMIC MAP (Right Column)
# -----------------

@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_location(query):
    # Use blazing-fast Groq to dynamically trim the sentence into an exact city name
    llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
    sys_prompt = f"Extract only the destination city from this trip query. Do not say anything else. Return ONLY the city name string. Query: '{query}'"
    map_city = llm.invoke([HumanMessage(content=sys_prompt)]).content.strip(" '\"\n.,")
    
    geolocator = Nominatim(user_agent="ai_travel_planner_map")
    return geolocator.geocode(map_city, timeout=4)


with map_col:
    st.subheader("🗺️ Destination Map")
    if "last_query" in st.session_state:
        with st.spinner("Locating..."):
            try:
                location = get_cached_location(st.session_state.last_query)
                if location:
                    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=11)
                    folium.Marker(
                        [location.latitude, location.longitude], 
                        popup=location.address, 
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(m)
                    st_folium(m, width=400, height=500)
                else:
                    st.info("I couldn't pinpoint the exact city from your message. Try mentioning a specific city name!")
            except Exception as e:
                st.warning("Map failed to load. (Geocoding API limits reached).")
    else:
        st.info("Send a destination query to see the map!")

# -----------------
# CALENDAR UTILITY (Rendered at end, displayed inside main_col)
# -----------------
with calendar_container:
    if st.session_state.messages and st.session_state.messages[-1].startswith("Assistant:"):
        last_answer = st.session_state.messages[-1].replace("Assistant: ", "", 1)
        st.write("---")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("📅 Generate Calendar (.ics) from Plan"):
                with st.spinner("Formatting Calendar for the latest plan..."):
                    try:
                        cal_payload = {"itinerary": last_answer}
                        headers = {"Authorization": f"Bearer {st.session_state.access_token}"} if "access_token" in st.session_state else {}
                        cal_response = requests.post(f"{BASE_URL}/generate_calendar", json=cal_payload, headers=headers)
                        if cal_response.status_code == 200:
                            st.session_state.ics_data = cal_response.json().get("ics", "")
                        else:
                            st.error(f"Backend Error: {cal_response.text}")
                    except Exception as e:
                        st.error(f"Error reaching server: {e}")
        with c2:
            if "ics_data" in st.session_state:
                st.download_button(
                    label="⬇️ Download itinerary.ics",
                    data=st.session_state.ics_data,
                    file_name="travel_itinerary.ics",
                    mime="text/calendar",
                    type="primary"
                )
