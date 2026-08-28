import streamlit as st
import pandas as pd
# Wir nutzen eine kleine Erweiterung, um auf den Speicher des Browsers zuzugreifen
from streamlit_local_storage import LocalStorage

st.title("⏰ Testumgebung")
st.set_page_config(page_title="Testumgebung", layout="wide")
# --- GEHEIMER BESUCHER-ZÄHLER (NUR FÜR DICH) ---
import requests
try:
    counter_url = "https://kvdb.io" + "hell_clock_tracker_v2"
    
    # 1. Aktuellen Stand aus der Cloud holen
    current_count_resp = requests.get(counter_url)
    if current_count_resp.status_code == 200 and current_count_resp.text.isdigit():
        current_count = int(current_count_resp.text)
    else:
        current_count = 0  
        
    # Wir holen uns das Passwort ganz dezent aus der Seitenleiste
    # Normalerweise leer, für dich tippst du einfach dein geheimes Wort ein
    st.sidebar.markdown("---")
    admin_password = st.sidebar.text_input("🔑 Admin-Bereich:", type="password", key="dev_admin_gate")
    
    # Wenn das Passwort NICHT stimmt, ist es ein normaler Gast -> +1 hochzählen!
    if admin_password != "Shelbygt500!Ginaundlisa89!":
        requests.post(counter_url, data=str(current_count + 1))
    else:
        # Wenn du das richtige Passwort eingibst, ploppt die Statistik auf!
        st.sidebar.metric(label="📈 Gesamte Aufrufe (Gäste)", value=f"{current_count}")
except Exception as e:
    current_count = 0

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
saved_rolls = local_storage.getItem("Hell_Clock_Rolls") or {}

# Filter in der Seitenleiste
st.sidebar.header("Filter")
sizes = df["Size"].unique()
selected_size = st.sidebar.multiselect("Nach Relikt-Größe filtern:", sizes, default=sizes)
filtered_df = df[df["Size"].isin(selected_size)]

# --- APPMESSE & ANZEIGE ---
st.write(f"Zeige {len(filtered_df)} Relikte an:")

# Listen-Änderungen überwachen
# --- SPEICHER-FUNKTIONEN FÜR STREAMLIT EVENTS ---
def save_check_callback(relic_name, key_name):
    # Holt den aktuellen Zustand der Checkbox direkt aus dem Session State
    current_val = st.session_state[key_name]
    saved_checks[relic_name] = current_val
    local_storage.setItem("hell_clock_checks", saved_checks)

def save_roll_callback(relic_name, key_name):
    # Holt den aktuellen Wert des Nummernfelds direkt aus dem Session State
    current_val = st.session_state[key_name]
    st.session_state[f"roll_val_{relic_name}"] = current_val
    saved_rolls[relic_name] = current_val
    local_storage.setItem("Hell_Clock_Rolls", saved_rolls)

# --- SCHLEIFE FÜR DIE RELIKTE ---
for index, row in filtered_df.iterrows():
    name = row['Name']
    col1, col2, col3, col4 = st.columns(4)
    
    default_check = saved_checks.get(name, False)
    default_roll = float(saved_rolls.get(name, 0.0))
    
    # Eindeutige Keys für den Session State generieren
    cb_key = f"c_{name}_{index}"
    num_key = f"r_{name}_{index}"
    
    with col1:
        # Wir nutzen on_change! Sobald geklickt wird, springt er in die obere Funktion
        st.checkbox(
            "", 
            value=default_check, 
            key=cb_key, 
            on_change=save_check_callback, 
            args=(name, cb_key)
        )
        
    with col2:
        st.markdown(f"**{name}** ({row['Size']})")
        
    with col3:
        st.write(f"Min: {row['Min']} / Max: {row['Max']} {row['Unit']}")
        
    with col4:
        # Auch hier nutzen wir on_change für die Rolls
        st.number_input(
            "Dein Roll:", 
            value=float(st.session_state.get(f"roll_val_{name}", default_roll)), 
            key=num_key, 
            step=0.1,
            on_change=save_roll_callback,
            args=(name, num_key)
        )

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
