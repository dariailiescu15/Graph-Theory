import streamlit as st
import numpy as np
import pandas as pd
import graphviz
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI CSS
# ==============================================================================
st.set_page_config(page_title="Waze ML: Algoritmul Ford + AI", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    .title-box { background-color: #e6f7ff; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; }
    .title-text { color: #005c99; font-size: 45px; font-weight: 900; margin: 0; }
    </style>
""", unsafe_allow_html=True)

def fmt(val):
    if pd.isna(val) or val is None: return ""
    if val == float('inf'): return "\infty"
    if isinstance(val, (np.floating, float, int)):
        return str(int(val)) if float(val).is_integer() else f"{val:.2f}"
    return str(val)

# ==============================================================================
# MACHINE LEARNING: REȚEAUA NEURONALĂ (PREDICȚIA TRAFICULUI)
# ==============================================================================
@st.cache_resource
def antreneaza_model_ml():
    """
    Simulăm antrenarea unei Rețele Neuronale pe date istorice (Waze).
    Modelul învață cum afectează vremea, hazardul și traficul timpul de sosire.
    """
    # Generăm date sintetice de antrenament
    np.random.seed(42)
    n_samples = 1000
    
    # Features:[Cost_Baza, Vreme_Rea (0-1), Hazard (0-1), Nivel_Trafic (0-3)]
    X = np.random.rand(n_samples, 4)
    X[:, 0] = X[:, 0] * 20 + 1 # Cost baza între 1 și 21
    X[:, 1] = np.round(X[:, 1]) # Vreme: 0 (Senin), 1 (Ploaie/Zăpadă)
    X[:, 2] = np.random.choice([0, 1], p=[0.9, 0.1], size=n_samples) # Hazard (Accident - 10% șanse)
    X[:, 3] = np.random.choice([0, 1, 2, 3], size=n_samples) # Trafic (0=Liber, 3=Blocat)

    # Label (y) = Timpul real de parcurgere. Funcția logică pe care modelul trebuie să o învețe:
    # Timp = Baza + (Trafic * 3) + (Vreme_Rea * 5) + (Hazard * 15) + zgomot
    y = X[:, 0] + (X[:, 3] * 3) + (X[:, 1] * 5) + (X[:, 2] * 15) + np.random.randn(n_samples) * 1.5

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Definim Rețeaua Neuronală (2 straturi ascunse a câte 16 și 8 neuroni)
    nn_model = MLPRegressor(hidden_layer_sizes=(16, 8), activation='relu', max_iter=1000, random_state=42)
    nn_model.fit(X_scaled, y)
    
    return nn_model, scaler

model_ai, scaler = antreneaza_model_ml()

def aplica_predictie_ml(df, vreme, hazard, nivel_trafic):
    """
    Actualizează costurile din tabel folosind Rețeaua Neuronală
    """
    df_ai = df.copy()
    costuri_baza = df_ai['Cost f(x_i, x_j)'].values
    
    # Construim input-ul pentru rețeaua neuronală pe baza condițiilor curente
    vreme_val = 1 if vreme != "Senin" else 0
    hazard_val = 1 if hazard else 0
    
    X_curent = np.column_stack((
        costuri_baza,
        np.full(len(df_ai), vreme_val),
        np.full(len(df_ai), hazard_val),
        np.full(len(df_ai), nivel_trafic)
    ))
    
    X_scaled = scaler.transform(X_curent)
    costuri_predise = model_ai.predict(X_scaled)
    
    # Asigurăm că nu avem costuri negative sau mai mici decât baza
    costuri_predise = np.maximum(costuri_predise, costuri_baza)
    df_ai['Cost_AI (Dinamizat)'] = np.round(costuri_predise, 1)
    
    return df_ai

# ==============================================================================
# ALGORITMUL FORD (Nemodificat logic, dar va rula pe noile costuri AI)
# ==============================================================================
def executa_algoritmul_ford(arce_df, nod_start, coloana_cost='Cost_AI (Dinamizat)'):
    noduri = sorted(list(set(arce_df['Nod Start (x_i)']).union(set(arce_df['Nod Destinație (x_j)']))))
    lambdas = {n: float('inf') for n in noduri}
    lambdas[nod_start] = 0
    
    istoric =[{'iteratie': 0, 'lambdas': lambdas.copy(), 'modificari': {}}]
    iteratie = 1
    
    while iteratie < len(noduri) + 5:
        modificat = False
        modificari_iteratie = {}
        lambdas_curente = lambdas.copy()
        
        for _, rand in arce_df.iterrows():
            i, j, f_ij = rand['Nod Start (x_i)'], rand['Nod Destinație (x_j)'], rand[coloana_cost]
            if lambdas_curente[i] != float('inf') and lambdas_curente[j] - lambdas_curente[i] > f_ij:
                lambdas_curente[j] = lambdas_curente[i] + f_ij
                modificat = True
                modificari_iteratie[j] = lambdas_curente[j]
        
        lambdas = lambdas_curente.copy()
        istoric.append({'iteratie': iteratie, 'lambdas': lambdas.copy(), 'modificari': modificari_iteratie})
        if not modificat: break
        iteratie += 1
        
    return noduri, istoric

def reconstituie_drum_ford(istoric_lambdas, arce_df, nod_start, nod_destinatie, coloana_cost='Cost_AI (Dinamizat)'):
    lambdas = istoric_lambdas[-1]['lambdas']
    if lambdas[nod_destinatie] == float('inf'): return None, "Nu există drum."
        
    drum = [nod_destinatie]
    curent = nod_destinatie
    while curent != nod_start:
        gasit = False
        for _, rand in arce_df.iterrows():
            i, j, f_ij = rand['Nod Start (x_i)'], rand['Nod Destinație (x_j)'], rand[coloana_cost]
            if j == curent and abs(lambdas[j] - lambdas[i] - f_ij) < 1e-5:
                drum.append(i)
                curent = i
                gasit = True
                break
        if not gasit: break
    return drum[::-1], lambdas[nod_destinatie]

# GRAFICA (adaptată să citească 'Cost_AI')
def deseneaza_graf(arce_df, drum_optim=None, coloana_cost='Cost_AI (Dinamizat)'):
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', bgcolor='transparent')
    graf.attr('node', shape='circle', style='filled', fillcolor='#ccebff', color='#005c99', fontcolor='#004466')
    
    noduri = set(arce_df['Nod Start (x_i)']).union(set(arce_df['Nod Destinație (x_j)']))
    for n in noduri: graf.node(str(int(n)), f"x{int(n)}")
        
    for _, rand in arce_df.iterrows():
        i, j = str(int(rand['Nod Start (x_i)'])), str(int(rand['Nod Destinație (x_j)']))
        f_ij = fmt(rand[coloana_cost])
        
        e_in_drum_optim = drum_optim and any(str(int(drum_optim[k])) == i and str(int(drum_optim[k+1])) == j for k in range(len(drum_optim)-1))
        if e_in_drum_optim:
            graf.edge(i, j, label=f_ij, color='#cc0000', penwidth='3.5', fontcolor='#cc0000')
        else:
            graf.edge(i, j, label=f_ij, color='#cccccc', penwidth='1.5')
    return graf

# ==============================================================================
# INTERFAȚA UTILIZATOR (UI)
# ==============================================================================
st.markdown('''
    <div class="title-box">
        <p class="title-text">🤖 Waze AI: Navigație Dinamică</p>
        <p style="color: #005c99;">Algoritmul Ford combinat cu Rețele Neuronale (ML)</p>
    </div>
''', unsafe_allow_html=True)

# 1. PARAMETRII DE CONTEXT (Waze Features)
st.markdown("### 🌦️ Parametrii de Context (Real-Time)")
col1, col2, col3 = st.columns(3)
with col1:
    vreme_selectata = st.selectbox("Starea Vremii:",["Senin", "Ploaie/Zăpadă puternică"])
with col2:
    nivel_trafic = st.slider("Nivel Trafic (0=Liber, 3=Aglomerat):", 0, 3, 0)
with col3:
    hazard_activ = st.checkbox("⚠️ Raportează Accident pe Traseu")

# 2. DATELE DE BAZĂ
if "tabel_arce" not in st.session_state:
    st.session_state.tabel_arce = pd.DataFrame([
        [1, 2, 10],[1, 9, 10],[2, 3, 15],[3, 4, 12],[4, 1, 7],[4, 6, 8],
        [4, 9, 9],[5, 1, 6],[5, 6, 20],[6, 7, 17],[6, 8, 13],[7, 1, 4],[7, 2, 6],[8, 9, 11],[9, 5, 5],[9, 6, 4]
    ], columns=["Nod Start (x_i)", "Nod Destinație (x_j)", "Cost f(x_i, x_j)"])

# Aplicăm predicția rețelei neuronale pentru a recalcula costurile
df_curent = aplica_predictie_ml(st.session_state.tabel_arce, vreme_selectata, hazard_activ, nivel_trafic)

col_tabel, col_graf = st.columns([1, 1])
with col_tabel:
    st.markdown("#### 1. Datele Străzilor (Dinamizat de AI)")
    st.dataframe(df_curent, use_container_width=True)

noduri_disponibile = sorted(list(set(df_curent['Nod Start (x_i)']).union(set(df_curent['Nod Destinație (x_j)']))))
with col_graf:
    st.markdown("#### 📍 Configurare Rută")
    nod_start = st.selectbox("Locația ta ($x_s$)", noduri_disponibile, index=0)
    nod_dest = st.selectbox("Destinația ($x_t$)", noduri_disponibile, index=len(noduri_disponibile)-1)

if st.button("🚀 Găsește Drumul cu Ford AI", type="primary", use_container_width=True):
    # Rulăm Ford pe coloana generată de Rețeaua Neuronală
    noduri, istoric = executa_algoritmul_ford(df_curent, nod_start, coloana_cost='Cost_AI (Dinamizat)')
    drum, cost_total = reconstituie_drum_ford(istoric, df_curent, nod_start, nod_dest, coloana_cost='Cost_AI (Dinamizat)')
    
    st.divider()
    st.success(f"**Timp estimat de sosire (ETA): {cost_total:.1f} minute**")
    
    graf_final = deseneaza_graf(df_curent, drum_optim=drum, coloana_cost='Cost_AI (Dinamizat)')
    st.graphviz_chart(graf_final, use_container_width=True)
    
    # Explicație pentru utilizator
    st.info("""
    **Ce s-a întâmplat sub capotă?**
    1. Rețeaua Neuronală (`MLPRegressor`) a analizat distanța de bază a fiecărei străzi, nivelul traficului și starea vremii setată de tine.
    2. A generat coloana nouă `Cost_AI (Dinamizat)`. Vei observa că dacă plouă sau este trafic, muchiile au costuri mai mari.
    3. Algoritmul Ford a calculat drumul matematic perfect pe baza *acestor noi costuri prezise*, exact cum rutează Waze șoferii ocolind aglomerația.
    """)
