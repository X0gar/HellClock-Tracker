import streamlit as st
import pandas as pd
# Wir nutzen eine kleine Erweiterung, um auf den Speicher des Browsers zuzugreifen
from streamlit_local_storage import LocalStorage

st.title("⏰ Hell Clock – Relic Completionist Tool v0.1")
st.set_page_config(page_title="Hell Clock Tracker", layout="wide")
# --- VERBINDUNG ZUM GOOGLE SHEET ---
sheet_id = "1LnwXHeQUr75nDb2VmbTSOBAP1bzl7x7Qul-PGvdHyLU"
csv_url = "https://docs.google.com/spreadsheets/d/1LnwXHeQUr75nDb2VmbTSOBAP1bzl7x7Qul-PGvdHyLU/export?format=csv&gid=1242009671#gid=1242009671"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url, skiprows=3)
    return df.dropna(subset=['Name'])

try:
    df = load_data()
except Exception as e:
    st.error(f"Fehler beim Laden der Daten: {e}")
    st.stop()

local_storage = LocalStorage()

# --- DATEN AUS DEM BROWSER-SPEICHER LADEŇ ---
# Wir holen uns die alten Haken und Rolls des Spielers aus seinem Browser
saved_checks = local_storage.getItem("hell_clock_checks") or {}
saved_rolls = local_storage.getItem("hell_clock_rolls") or {}

# Filter in der Seitenleiste
st.sidebar.header("Filter")
sizes = df["Size"].unique()
selected_size = st.sidebar.multiselect("Nach Relikt-Größe filtern:", sizes, default=sizes)
filtered_df = df[df["Size"].isin(selected_size)]

# --- APPMESSE & ANZEIGE ---
st.write(f"Zeige {len(filtered_df)} Relikte an:")

# Listen-Änderungen überwachen
changes_made = False

for index, row in filtered_df.iterrows():
    name = row['Name']
    col1, col2, col3, col4 = st.columns(4)
    
    # Standardwerte aus dem Speicher laden (falls vorhanden)
    default_check = saved_checks.get(name, False)
    default_roll = float(saved_rolls.get(name, 0.0))
    
    with col1:
        # Checkbox mit dem geladenen Wert anzeigen
        checked = st.checkbox("", value=default_check, key=f"c_{name}_{index}")
        if checked != default_check:
            saved_checks[name] = checked
            changes_made = True
        
    with col2:
        st.markdown(f"**{name}** ({row['Size']})")
        
    with col3:
        st.write(f"Min: {row['Min']} / Max: {row['Max']} {row['Unit']}")
        
    with col4:
        # Zahlenfeld mit dem geladenen Wert anzeigen
        user_roll = st.number_input(
            "Dein Roll:", 
            value=float(st.session_state.get(f"roll_val_{name}", saved_rolls.get(name, 0.0))), 
            key=f"r_{name}_{index}", 
            step=0.1
        )
        
        # Sobald sich die Zahl ändert, brennen wir sie direkt in den State
        if user_roll != float(saved_rolls.get(name, 0.0)):
            st.session_state[f"roll_val_{name}"] = user_roll
            saved_rolls[name] = user_roll
            local_storage.setItem("Hell_Clock_Rolls", saved_rolls)

# --- DATEN IM BROWSER SPEICHERN ---
# Wenn der Spieler was geändert hat, schreiben wir es sofort zurück in den Browser
if changes_made:
    local_storage.setItem("hell_clock_checks", saved_checks)
    local_storage.setItem("hell_clock_rolls", saved_rolls)
# --- SIDEBAR SOCIALS ---
# --- SIDEBAR SOCIALS & ART ---
st.sidebar.markdown("---")

# Sicherer Twitch-Button direkt zu deinem Kanal
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
