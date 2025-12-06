"""
Frontend application for TubeTranscript.

This Streamlit app provides a user interface to interact with the TubeTranscript backend API.
It allows users to input a YouTube URL, view available languages, and fetch transcripts.
"""

import streamlit as st
import requests
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="TubeTranscript PoC", page_icon="📺")

st.title("📺 TubeTranscript Clone")
st.markdown("Extraction de sous-titres via **Microservices**.")

# --- State Initialization ---
if 'available_languages' not in st.session_state:
    st.session_state.available_languages = {"fr": "Français (Défaut)", "en": "Anglais (Défaut)"}

# --- UI Layout & Logic ---

# URL Input
url_input = st.text_input("URL YouTube ou ID", placeholder="https://www.youtube.com/watch?v=...")

# Automatic Language Fetching
if url_input and url_input != st.session_state.get('last_fetched_url'):
    with st.spinner("Récupération des langues..."):
        try:
            response = requests.post(f"{BACKEND_URL}/languages", json={"video_url_or_id": url_input})
            if response.status_code == 200:
                data = response.json()
                new_langs = {}
                
                # Process manual transcripts
                for l in data.get('manual_transcripts', []):
                    label = f"👤 {l['language_name']}"
                    new_langs[l['language_code']] = label
                    
                # Process generated transcripts
                for l in data.get('generated_transcripts', []):
                    label = f"🤖 {l['language_name']} (Auto)"
                    new_langs[l['language_code']] = label
                    
                st.session_state.available_languages = new_langs
                st.session_state.last_fetched_url = url_input
                st.success(f"{len(new_langs)} langues trouvées !")
            else:
                st.error("Erreur lors de la récupération des langues.")
        except Exception as e:
            st.error(f"Erreur de connexion: {e}")

# Language Selection
lang_options = list(st.session_state.available_languages.keys())
lang_labels = [st.session_state.available_languages[k] for k in lang_options]

selected_label = st.selectbox("Langue", lang_labels)
selected_code = next((k for k, v in st.session_state.available_languages.items() if v == selected_label), "fr")

show_timestamps = st.checkbox("Inclure les timestamps")

# Transcript Extraction
if st.button("Extraire le texte", type="primary"):
    if url_input:
        with st.spinner('Appel API en cours...'):
            try:
                payload = {"video_url_or_id": url_input, "lang": selected_code}
                response = requests.post(f"{BACKEND_URL}/transcript", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    
                    final_text = data['text']
                    if show_timestamps and 'segments' in data:
                        lines = []
                        for seg in data['segments']:
                            start_time = int(seg['start'])
                            minutes = start_time // 60
                            seconds = start_time % 60
                            timestamp = f"[{minutes:02d}:{seconds:02d}]"
                            lines.append(f"{timestamp} {seg['text']}")
                        final_text = "\n".join(lines)

                    st.success(f"Succès ! (ID: {data['video_id']})")
                    st.text_area("Transcript", value=final_text, height=300)
                    st.download_button("Télécharger .txt", final_text, file_name=f"transcript_{data['video_id']}.txt")
                else:
                    st.error(f"Erreur HTTP {response.status_code}")
                    st.warning("Réponse brute du serveur (pour debug):")
                    st.code(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("Impossible de contacter le backend. Vérifiez que les conteneurs Docker tournent.")