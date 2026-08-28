import streamlit as st
import pandas as pd
# Wir nutzen eine kleine Erweiterung, um auf den Speicher des Browsers zuzugreifen
from streamlit_local_storage import LocalStorage
import requests
# Das MUSS auf Platz 1 stehen für das Widescreen!
st.set_page_config(page_title="HellClock Relic Tracker", layout="wide")
st.title("⏰ Relic Tracker")
# --- GEHEIMER BESUCHER-ZÄHLER (MIT RERUN-SCHUTZ) ---
COUNTER_FILE = "besucher_zaehler.txt"

# "counter_checked" sorgt dafür, dass pro Tab-Öffnung NUR EINMAL gezählt wird!
if "counter_checked" not in st.session_state:
    try:
        try:
            with open(COUNTER_FILE, "r") as f:
                count = int(f.read().strip())
        except:
            count = 0
        
        # Nur hochzählen, wenn du NICHT der Admin bist!
        if st.session_state.get("dev_admin_gate") != "xoogar99":
            with open(COUNTER_FILE, "w") as f:
                f.write(str(count + 1))
            st.session_state["current_count"] = count + 1
        else:
            st.session_state["current_count"] = count
    except:
        st.session_state["current_count"] = 0
    
    # Schutzschild aktivieren: Für diesen Tab-Besuch wird nicht mehr gezählt!
    st.session_state["counter_checked"] = True
else:
    # Bei jedem weiteren automatischen Refresh lesen wir einfach nur den aktuellen Stand aus
    try:
        with open(COUNTER_FILE, "r") as f:
            st.session_state["current_count"] = int(f.read().strip())
    except:
        pass

# Wert für den Admin-Bereich unten bereitstellen
current_count = st.session_state.get("current_count", 0)
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
# --- GEHEIMER BESUCHER-ZÄHLER (ANZEIGE) ---
# Das Passwortfeld erscheint ganz unten in der Sidebar
admin_password = st.sidebar.text_input("🔑 Admin-Bereich:", type="password", key="dev_admin_gate")

# Wenn du das richtige Passwort eingibst, ploppt die Statistik auf!
if admin_password == "Shelbygt500!Ginaundlisa89!":
    st.sidebar.metric(label="📈 Gesamte Aufrufe (Gäste)", value=f"{current_count}")

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
