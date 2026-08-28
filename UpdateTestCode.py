import streamlit as st
import pandas as pd
from streamlit_local_storage import LocalStorage

# --- SEITEN-KONFIGURATION ---
# Das MUSS zwingend die allererste Streamlit-Zeile sein!
st.set_page_config(page_title="Hell Clock Tracker", layout="wide")

st.title("⏰ Hell Clock – Relic Completionist Tool v0.1")

# --- VERBINDUNG ZUM GOOGLE SHEET ---
sheet_id = "1LnwXHeQUr75nDb2VmbTSOBAP1bzl7x7Qul-PGvdHyLU"
csv_url = "https://google.com"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url, skiprows=3)
    return df.dropna(subset=['Name'])

try:
    df = load_data()
except Exception as e:
    st.error(f"Fehler beim Laden der Daten: {e}")
    st.stop()

# Speicher initialisieren
local_storage = LocalStorage()

# --- DATEN AUS DEM BROWSER-SPEICHER LADEN ---
saved_data = local_storage.getItem("hell_clock_data") or {}
saved_checks = saved_data.get("checks", {})
saved_rolls = saved_data.get("rolls", {})

# --- FILTER IN DER SEITENLEISTE ---
st.sidebar.header("Filter")
sizes = df["Size"].unique()

# HIER: Wir fügen einen eindeutigen KEY hinzu, um den DuplicateID-Fehler zu killen!
selected_size = st.sidebar.multiselect(
    "Nach Relikt-Größe filtern:", 
    sizes, 
    default=sizes,
    key="relic_size_filter_widget" 
)
filtered_df = df[df["Size"].isin(selected_size)]

# --- ANZEIGE ---
st.write(f"Zeige {len(filtered_df)} Relikte an:")

changes_made = False

# --- SCHLEIFE FÜR DIE RELIKTE ---
for index, row in filtered_df.iterrows():
    name = row['Name']
    col1, col2, col3, col4 = st.columns(4)
    
    default_check = saved_checks.get(name, False)
    default_roll = float(saved_rolls.get(name, 0.0))
    
    with col1:
        checked = st.checkbox("", value=default_check, key=f"c_{name}_{index}")
        if checked != default_check:
            saved_checks[name] = checked
            changes_made = True
        
    with col2:
        st.markdown(f"**{name}** ({row['Size']})")
        
    with col3:
        st.write(f"Min: {row['Min']} / Max: {row['Max']} {row['Unit']}")
        
    with col4:
        user_roll = st.number_input(
            "Dein Roll:", 
            value=float(st.session_state.get(f"roll_val_{name}", default_roll)), 
            key=f"r_{name}_{index}", 
            step=0.1
        )
        
        if user_roll != default_roll:
            st.session_state[f"roll_val_{name}"] = user_roll
            saved_rolls[name] = user_roll
            changes_made = True

# --- DATEN IM BROWSER SPEICHERN ---
if changes_made:
    local_storage.setItem("hell_clock_data", {"checks": saved_checks, "rolls": saved_rolls})

# --- SIDEBAR SOCIALS ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="background-color: #9146FF; padding: 12px; border-radius: 8px; text-align: center; margin-top: 10px;">
        <a href="https://www.twitch.tv/xoogar" target="_blank" style="color: white; text-decoration: none; font-weight: bold; font-size: 15px; display: block;">
            🎮 Visit me on Twitch: xoogar
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
