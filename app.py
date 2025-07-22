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
        autore TEXT,
        tipo TEXT DEFAULT 'query'
    )
''')
conn.commit()

# Funzioni utili
def aggiungi_query(query, argomento, parole_chiave, note, opit, autore, tipo):
    c.execute('''
        INSERT INTO queries (id, query, argomento, parole_chiave, note, opit, data_creazione, autore, tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        query,
        argomento,
        ",".join(parole_chiave),
        note,
        opit,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        autore,
        tipo
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

def get_argomenti_conteggio(tipo):
    c.execute("SELECT argomento, COUNT(*) FROM queries WHERE tipo=? GROUP BY argomento ORDER BY COUNT(*) DESC", (tipo,))
    return c.fetchall()

def get_query_by_argomento(argomento):
    c.execute("SELECT * FROM queries WHERE argomento=?", (argomento,))
    return c.fetchall()

# UI Streamlit
st.set_page_config(page_title="DBA Query Repository")
st.title("📚 DBA Query Repository")

st.sidebar.title("Navigazione")

if st.sidebar.button("🏠 Home"):
    st.session_state['pagina_attiva'] = "🏠 Home"
if st.sidebar.button("➕ Aggiungi Query"):
    st.session_state['pagina_attiva'] = "➕ Aggiungi Query"
if st.sidebar.button("📜 Aggiungi Procedura"):
    st.session_state['pagina_attiva'] = "📜 Aggiungi Procedura"
if st.sidebar.button("🔍 Cerca"):
    st.session_state['pagina_attiva'] = "🔍 Cerca"

# Recupera la pagina selezionata
pagina = st.session_state.get('pagina_attiva', "🏠 Home")


if pagina == "🏠 Home":
    st.markdown("""
    ## 📚 Benvenuto nel repository query DBA
    - Conserva le query SQL utili
    - Organizzale per argomento e parole chiave
    - Aggiungi note e riferimento OPIT
    - Ricerca libera su tutto
    """)

    st.markdown("### 🔎 Indice Query")
    argomenti_query = get_argomenti_conteggio("query")
    if argomenti_query:
        for arg, count in argomenti_query:
            if st.button(f"📄 {arg} ({count} query)"):
                st.session_state['argomento_selezionato'] = arg
                st.session_state['tipo_selezionato'] = 'query'
                st.session_state['pagina_attiva'] = "🔍 Cerca"
    else:
        st.info("Nessuna query ancora inserita.")

    st.markdown("### 📜 Indice Procedure")
    argomenti_proc = get_argomenti_conteggio("procedura")
    if argomenti_proc:
        for arg, count in argomenti_proc:
            if st.button(f"🧾 {arg} ({count} procedure)"):
                st.session_state['argomento_selezionato'] = arg
                st.session_state['tipo_selezionato'] = 'procedura'
                st.session_state['pagina_attiva'] = "🔍 Cerca"
    else:
        st.info("Nessuna procedura ancora inserita.")

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
            aggiungi_query(query, argomento, parole_chiave.split(","), note, opit, autore, "query")
            st.success("✅ Query salvata correttamente")

elif pagina == "📜 Aggiungi Procedura":
    st.header("Aggiungi una nuova procedura")
    with st.form("aggiungi_proc_form"):
        query = st.text_area("Procedura SQL", height=200)
        argomento = st.text_input("Argomento procedura")
        parole_chiave = st.text_input("Parole chiave (separate da virgole)")
        note = st.text_area("Descrizione procedura")
        opit = st.text_input("OPIT o riferimento")
        autore = st.text_input("Tuo nome")
        submitted = st.form_submit_button("Salva procedura")
        if submitted and query:
            aggiungi_query(query, argomento, parole_chiave.split(","), note, opit, autore, "procedura")
            st.success("✅ Procedura salvata correttamente")

elif pagina == "🔍 Cerca":
    st.header("Cerca tra le query e le procedure")

    termine = st.text_input("Termine di ricerca")

    # Priorità alla selezione da homepage
    argomento_selezionato = st.session_state.get('argomento_selezionato', None)
    tipo_selezionato = st.session_state.get('tipo_selezionato', None)

    risultati = []
    if termine:
        risultati = cerca_query(termine)
    elif argomento_selezionato and tipo_selezionato:
        c.execute("SELECT * FROM queries WHERE argomento=? AND tipo=?", (argomento_selezionato, tipo_selezionato))
        risultati = c.fetchall()
        st.subheader(f"Visualizzazione per argomento: {argomento_selezionato} ({tipo_selezionato})")
        st.session_state.pop('argomento_selezionato')
        st.session_state.pop('tipo_selezionato')

    if risultati:
        for r in risultati:
            st.markdown(f"""
            ---
            **Argomento:** {r[2]}
            
            **Parole chiave:** {r[3]}
            
            **Note:** {r[4]}
            
            **OPIT:** {r[5]}  |  **Autore:** {r[7]}  |  **Data:** {r[6]}  |  **Tipo:** {r[8]}

            ```sql
            {r[1]}
            ```
            """)
    elif termine:
        st.info("Nessun risultato trovato.")