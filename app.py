import streamlit as st
import pandas as pd
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Hell Clock Tracker", layout="wide")
st.title("⏰ Hell Clock – Relic Completionist Tool")
st.markdown("---")

# --- VERBINDUNG ZUM GOOGLE SHEET ---
csv_url = "https://google.com"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url, skiprows=3)
    # Leere Zeilen ohne Namen löschen
    df = df.dropna(subset=[df.columns[1]])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Fehler beim Laden der Daten: {e}")
    st.stop()

# --- LOCAL STORAGE INITIALISIERUNG ---
local_storage = LocalStorage()

saved_checks = local_storage.getItem("hell_clock_checks") or {}
saved_rolls = local_storage.getItem("Hell_Clock_Rolls") or {}

# Synchronisiere die geladenen Rolls sofort in den Streamlit Session State
for k, v in saved_rolls.items():
    state_key = f"state_r_{k}"
    if state_key not in st.session_state:
        st.session_state[state_key] = float(v) if v is not None else 0.0

# --- SEITENLEISTE / FILTER ---
st.sidebar.header("🛡️ Filter-Optionen")
unique_sizes = sorted(list(df.iloc[:, 5].dropna().unique())) if df.shape[1] > 5 else []

if unique_sizes:
    selected_size = st.sidebar.selectbox("Nach Größe filtern:", ["Alle"] + unique_sizes)
else:
    selected_size = "Alle"

# Daten filtern
if selected_size != "Alle" and df.shape[1] > 5:
    filtered_df = df[df.iloc[:, 5] == selected_size]
else:
    filtered_df = df

st.markdown(f"**Zeige {len(filtered_df)} Relikte an:**")

# --- LISTE ANZEIGEN ---
for index, row in filtered_df.iterrows():
    name = str(row.iloc[1])
    min_val = row.iloc[2]
    max_val = row.iloc[3]
    unit = str(row.iloc[4]) if pd.notna(row.iloc[4]) else ""
    
    # Zustand laden
    default_check = saved_checks.get(name, False)
    state_key = f"state_r_{name}"
    
    # Sicherstellen, dass der Key im Session State existiert
    if state_key not in st.session_state:
        st.session_state[state_key] = float(saved_rolls.get(name, 0.0))

    # Container für visuelles Highlight
    is_checked = st.session_state.get(f"c_{name}_{index}", default_check)
    
    # Zeilen-Layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        checked = st.checkbox("", value=default_check, key=f"c_{name}_{index}")
        if checked != default_check:
            saved_checks[name] = checked
            local_storage.setItem("hell_clock_checks", saved_checks)
            st.rerun()
            
    with col2:
        if checked:
            st.markdown(f"**🔵 {name}**")
        else:
            st.markdown(name)
            
    with col3:
        st.write(f"Min: {min_val} / Max: {max_val} {unit}")
        
    with col4:
        # On_Change Funktion speichert direkt und sauber ab
        user_roll = st.number_input(
            "Dein Roll:", 
            min_value=0.0, 
            max_value=10000.0, 
            step=0.1, 
            key=state_key
        )
        
        # Prüfen ob Wert geupdatet wurde
        current_saved_value = float(saved_rolls.get(name, 0.0))
        if user_roll != current_saved_value:
            saved_rolls[name] = user_roll
            local_storage.setItem("Hell_Clock_Rolls", saved_rolls)
            st.rerun()

        # Max Roll Check
        if checked and user_roll == float(max_val):
            st.success("🎉 MAX ROLL!")
        elif checked and user_roll < float(max_val):
            st.error("🟥 ALARM (NOT MAX)")

    st.markdown("---")
