import streamlit as st
import sqlite3
import uuid
from datetime import datetime

# DB Setup
conn = sqlite3.connect("db/queries.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS queries (
        id TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        argomento TEXT,
        parole_chiave TEXT,
        note TEXT,
        opit TEXT,
        data_creazione TEXT,
        autore TEXT
    )
''')
conn.commit()

# Funzioni utili
def aggiungi_query(query, argomento, parole_chiave, note, opit, autore):
    c.execute('''
        INSERT INTO queries (id, query, argomento, parole_chiave, note, opit, data_creazione, autore)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        query,
        argomento,
        ",".join(parole_chiave),
        note,
        opit,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        autore
    ))
    conn.commit()

def cerca_query(termine):
    query = f"""
        SELECT * FROM queries
        WHERE query LIKE ? OR argomento LIKE ? OR parole_chiave LIKE ? OR note LIKE ? OR opit LIKE ? OR autore LIKE ?
    """
    wildcard = f"%{termine}%"
    c.execute(query, (wildcard,) * 6)
    return c.fetchall()

def get_argomenti_conteggio():
    c.execute("SELECT argomento, COUNT(*) FROM queries GROUP BY argomento ORDER BY COUNT(*) DESC")
    return c.fetchall()

# UI Streamlit
st.set_page_config(page_title="DBA Query Repository")
st.title("📚 DBA Query Repository")

st.sidebar.title("Navigazione")
pagina = st.sidebar.radio("Vai a:", ["🏠 Home", "➕ Aggiungi Query", "🔍 Cerca"], label_visibility="collapsed")

if pagina == "🏠 Home":
    st.markdown("""
    ## 📚 Benvenuto nel repository query DBA Spindox
    - Conserva le query SQL utili
    - Organizzale per argomento e parole chiave
    - Aggiungi note e riferimento OPIT
    - Ricerca libera su tutto
    """)

    st.markdown("### 📌 Indice automatico per argomento")
    argomenti = get_argomenti_conteggio()
    if argomenti:
        for arg, count in argomenti:
            st.markdown(f"- **{arg}** ({count} query)")
    else:
        st.info("Nessuna query ancora inserita.")

elif pagina == "➕ Aggiungi Query":
    st.header("Aggiungi una nuova query")
    with st.form("aggiungi_form"):
        query = st.text_area("Query SQL", height=150)
        argomento = st.text_input("Argomento")
        parole_chiave = st.text_input("Parole chiave (separate da virgole)")
        note = st.text_area("Note esplicative")
        opit = st.text_input("OPIT o riferimento")
        autore = st.text_input("Tuo nome")
        submitted = st.form_submit_button("Salva")
        if submitted and query:
            aggiungi_query(query, argomento, parole_chiave.split(","), note, opit, autore)
            st.success("✅ Query salvata correttamente")

elif pagina == "🔍 Cerca":
    st.header("Cerca tra le query")
    termine = st.text_input("Termine di ricerca")
    if termine:
        risultati = cerca_query(termine)
        if risultati:
            for r in risultati:
                st.markdown(f"""
                ---
                **Argomento:** {r[2]}
                
                **Parole chiave:** {r[3]}
                
                **Note:** {r[4]}
                
                **OPIT:** {r[5]}  |  **Autore:** {r[7]}  |  **Data:** {r[6]}

                ```sql
                {r[1]}
                ```
                """)
        else:
            st.info("Nessun risultato trovato.")
