import streamlit as st
import numpy as np
import pandas as pd
import graphviz

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI CSS
# ==============================================================================
st.set_page_config(page_title="Algoritmul Ford", layout="wide", page_icon="🗺️")

st.markdown("""
    <style>
    /* Definirea temei cromatice (portocaliu pastel) pentru un aspect profesional */
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 55px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

def fmt(val):
    """
    Formatarea valorilor numerice pentru afișarea în interfață și în ecuațiile LaTeX.
    Înlătură zecimalele inutile și tratează cazurile de infinit matematic.
    """
    if pd.isna(val) or val is None: return ""
    if val == float('inf'): return "\infty"
    if isinstance(val, (np.floating, float, int)):
        return str(int(val)) if float(val).is_integer() else f"{val:.2f}"
    return str(val)

# ==============================================================================
# REPREZENTAREA GRAFICĂ (GRAPHVIZ)
# ==============================================================================
def deseneaza_graf(arce_df, drum_optim=None):
    """
    Generează reprezentarea vizuală a grafului pe baza tabelului de date.
    Dacă un drum optim este furnizat, arcele componente vor fi evidențiate.
    """
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', bgcolor='transparent') # Orientare de la stânga la dreapta
    
    # Stilul vizual al vârfurilor (nodurilor)
    graf.attr('node', shape='circle', style='filled', fillcolor='#ffecd9', color='#e65c00', fontcolor='#cc5200', fontname='Helvetica', penwidth='2')
    
    # Adăugarea vârfurilor unice în graf
    noduri = set(arce_df['Nod Start (x_i)']).union(set(arce_df['Nod Destinație (x_j)']))
    for n in noduri:
        graf.node(str(int(n)), f"x{int(n)}")
        
    # Construirea și stilizarea arcelor
    for _, rand in arce_df.iterrows():
        i = str(int(rand['Nod Start (x_i)']))
        j = str(int(rand['Nod Destinație (x_j)']))
        f_ij = fmt(rand['Cost f(x_i, x_j)'])
        
        # Verificăm apartenența arcului la drumul de valoare minimă
        e_in_drum_optim = False
        if drum_optim:
            for k in range(len(drum_optim)-1):
                if str(int(drum_optim[k])) == i and str(int(drum_optim[k+1])) == j:
                    e_in_drum_optim = True
                    break
        
        # Evidențierea arcelor de pe traseul optim
        if e_in_drum_optim:
            graf.edge(i, j, label=f_ij, color='#e65c00', penwidth='3.5', fontcolor='#e65c00', fontsize='14', fontname='Helvetica-bold')
        else:
            graf.edge(i, j, label=f_ij, color='#cccccc', penwidth='1.5', fontcolor='#888888', fontsize='12', fontname='Helvetica')
            
    return graf

# ==============================================================================
# LOGICA MATEMATICĂ: ALGORITMUL FORD
# ==============================================================================
def executa_algoritmul_ford(arce_df, nod_start):
    """
    Execută Algoritmul Ford pentru determinarea drumului de valoare minimă,
    salvând starea sistemului (etichetele lambda) la fiecare iterație.
    """
    noduri = set(arce_df['Nod Start (x_i)']).union(set(arce_df['Nod Destinație (x_j)']))
    noduri = sorted(list(noduri))
    
    # Iterația I_0: Inițializarea valorilor
    lambdas = {n: float('inf') for n in noduri}
    lambdas[nod_start] = 0
    
    istoric =[]
    istoric.append({
        'iteratie': 0,
        'lambdas': lambdas.copy(),
        'modificari': {}
    })
    
    iteratie = 1
    max_iter = len(noduri) + 5 # Limită de siguranță pentru evitarea buclelor infinite
    
    while iteratie < max_iter:
        modificat = False
        modificari_iteratie = {}
        lambdas_curente = lambdas.copy()
        
        # Evaluarea tuturor arcelor din graf
        for _, rand in arce_df.iterrows():
            i = rand['Nod Start (x_i)']
            j = rand['Nod Destinație (x_j)']
            f_ij = rand['Cost f(x_i, x_j)']
            
            # Condiția de actualizare (relaxarea arcelor)
            if lambdas_curente[i] != float('inf') and lambdas_curente[j] - lambdas_curente[i] > f_ij:
                lambdas_curente[j] = lambdas_curente[i] + f_ij
                modificat = True
                modificari_iteratie[j] = lambdas_curente[j]
        
        lambdas = lambdas_curente.copy()
        istoric.append({
            'iteratie': iteratie,
            'lambdas': lambdas.copy(),
            'modificari': modificari_iteratie
        })
        
        # Condiția de oprire: stabilizarea rețelei (nicio valoare nu s-a mai modificat)
        if not modificat:
            break
        iteratie += 1
        
    return noduri, istoric

def reconstituie_drum_ford(istoric_lambdas, arce_df, nod_start, nod_destinatie):
    """
    Reconstituie drumul de valoare minimă parcurgând graful de la destinație
    spre sursă, verificând condiția de egalitate pe etichetele finale.
    """
    lambdas = istoric_lambdas[-1]['lambdas']
    
    if lambdas[nod_destinatie] == float('inf'):
        return None, "Nu există drum de la sursă la destinație."
        
    drum = [nod_destinatie]
    curent = nod_destinatie
    
    while curent != nod_start:
        gasit = False
        for _, rand in arce_df.iterrows():
            i = rand['Nod Start (x_i)']
            j = rand['Nod Destinație (x_j)']
            f_ij = rand['Cost f(x_i, x_j)']
            
            # Identificarea arcului ce respectă condiția de optim
            if j == curent and abs(lambdas[j] - lambdas[i] - f_ij) < 1e-9:
                drum.append(i)
                curent = i
                gasit = True
                break
        
        if not gasit:
            break # Măsură de siguranță
            
    return drum[::-1], lambdas[nod_destinatie] # Returnează drumul în ordine directă și valoarea sa

# ==============================================================================
# INTERFAȚA CU UTILIZATORUL (STREAMLIT)
# ==============================================================================
st.markdown('''
    <div class="title-box">
        <p class="title-text">🗺️ Teoria Grafurilor 🚗<br>📍 Algoritmul FORD 🚦</p>
    </div>
''', unsafe_allow_html=True)

st.markdown('''
    <div class="authors-box">
        <div class="authors-title">Facultatea de Științe Aplicate</div>
        <div class="authors-names">
            Dedu Anișoara-Nicoleta, 1333a<br>
            Dumitrescu Andreea Mihaela, 1333a<br>
            Iliescu Daria-Gabriela, 1333a<br>
            Lungu Ionela-Diana, 1333a
        </div>
    </div>
''', unsafe_allow_html=True)

# Secționarea interfeței pentru introducerea datelor și vizualizarea grafului
col_tabel, col_graf = st.columns([1, 1])

with col_tabel:
    st.markdown("<h3 style='color: #e65c00;'>📝 1. Datele Grafului</h3>", unsafe_allow_html=True)
    st.write("Definiți mulțimea arcelor $U$ și funcția de valoare $f(x_i, x_j)$. Tabelul este dinamic.")

    # Încărcarea datelor implicite (conform modelului prezentat la curs)
    if "tabel_arce" not in st.session_state:
        date_initiale = [[1, 2, 10],[1, 9, 10],[2, 3, 15],[3, 4, 12],[4, 1, 7],[4, 6, 8],[4, 9, 9],[5, 1, 6],[5, 6, 20],[6, 7, 17],[6, 8, 13],[7, 1, 4],[7, 2, 6],[8, 9, 11],[9, 5, 5],[9, 6, 4]
        ]
        df_initial = pd.DataFrame(date_initiale, columns=["Nod Start (x_i)", "Nod Destinație (x_j)", "Cost f(x_i, x_j)"])
        st.session_state.tabel_arce = df_initial

    edited_df = st.data_editor(
        st.session_state.tabel_arce, 
        num_rows="dynamic",
        use_container_width=True,
        key="editor_arce"
    )

with col_graf:
    st.markdown("<h3 style='color: #e65c00;'>🌍 Reprezentarea Vizuală a Grafului</h3>", unsafe_allow_html=True)
    graf_initial = deseneaza_graf(edited_df)
    st.graphviz_chart(graf_initial, use_container_width=True)

# Selectarea vârfurilor de început și sfârșit pentru algoritm
noduri_disponibile = sorted(list(set(edited_df['Nod Start (x_i)']).union(set(edited_df['Nod Destinație (x_j)']))))
if len(noduri_disponibile) > 0:
    st.markdown("### 📍 Configurare Traseu")
    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        nod_start = st.selectbox("Vârful de start ($x_s$)", noduri_disponibile, index=0)
    with c2:
        nod_dest = st.selectbox("Vârful terminal ($x_t$)", noduri_disponibile, index=len(noduri_disponibile)-1 if len(noduri_disponibile)>5 else 0)

# Declanșarea procedurii de calcul
if st.button("🚀 Calculează Drumul Minim", type="primary", use_container_width=True):
    st.divider()
    
    # --------------------------------------------------------------------------
    # AFIȘAREA ITERAȚIILOR
    # --------------------------------------------------------------------------
    st.markdown("<h3 style='color: #e65c00;'>⚙️ 2. Algoritmul FORD (Etape de rezolvare)</h3>", unsafe_allow_html=True)
    
    noduri, istoric = executa_algoritmul_ford(edited_df, nod_start)
    
    st.markdown(r"#### 🟢 Iterația $I_0$")
    st.write(f"Se atribuie fiecărui vârf $x_i \in X$ o valoare $\lambda_i$ astfel încât $\lambda_{{{nod_start}}} = 0$, iar restul sunt $\infty$.")
    
    l0_text = ", ".join([rf"\lambda_{{{n}}} = {fmt(istoric[0]['lambdas'][n])}" for n in noduri])
    st.latex(l0_text)
    
    for pas in istoric[1:]:
        st.markdown(r"---")
        st.markdown(rf"#### 🟡 Iterația $I_{{{pas['iteratie']}}}$")
        
        if len(pas['modificari']) == 0:
            st.success(rf"**Testul de optimalitate (TO):** Nu s-a efectuat nicio modificare la parcurgerea listei de arce. Procesul converge. $\Rightarrow$ **STOP**.")
            st.latex(r"I_{STOP} \Rightarrow \text{Reprezintă soluția problemei.}")
        else:
            st.write("Se parcurge lista arcelor și se evaluează condiția de ajustare: $\lambda_j - \lambda_i > f(x_i, x_j)$. Au avut loc următoarele modificări:")
            
            modificari_latex =[]
            for nod_modificat, valoare_noua in pas['modificari'].items():
                modificari_latex.append(rf"\lambda'_{{{nod_modificat}}} = {fmt(valoare_noua)}")
            st.latex(r" \quad ; \quad ".join(modificari_latex))
            
            st_text = ", ".join([rf"\lambda_{{{n}}} = {fmt(pas['lambdas'][n])}" for n in noduri])
            st.latex(r"\text{Status curent: } " + st_text)

    # --------------------------------------------------------------------------
    # RECONSTITUIREA ȘI CONCLUZIA MATEMATICĂ
    # --------------------------------------------------------------------------
    st.divider()
    st.markdown("<h3 style='color: #e65c00;'>🛤️ 3. Soluția Problemei (Reconstituirea drumului)</h3>", unsafe_allow_html=True)
    
    drum, cost_total = reconstituie_drum_ford(istoric, edited_df, nod_start, nod_dest)
    
    if drum is None:
        st.error(cost_total)
    else:
        st.write(rf"Se reconstituie drumul optim procedând invers, de la destinație ($x_{{{nod_dest}}}$) spre sursă ($x_{{{nod_start}}}$), verificând pe arce condiția matematică de apartenență la drumul minim:")
        st.latex(r"\lambda_j - \lambda_i = f(x_i, x_j)")
        
        # Prezentarea demonstrației analitice pentru traseul determinat
        for k in range(len(drum)-1, 0, -1):
            i = drum[k-1]
            j = drum[k]
            f_ij = edited_df[(edited_df['Nod Start (x_i)'] == i) & (edited_df['Nod Destinație (x_j)'] == j)]['Cost f(x_i, x_j)'].values[0]
            st.latex(rf"\lambda_{{{j}}} - \lambda_{{{i}}} = {fmt(istoric[-1]['lambdas'][j])} - {fmt(istoric[-1]['lambdas'][i])} = {fmt(f_ij)} = f(x_{{{i}}}, x_{{{j}}})")
        
        traseu_str = " \\rightarrow ".join([f"x_{{{n}}}" for n in drum])
        
        st.latex(r"\textbf{Drumul de valoare minimă } \mu^* \textbf{ este:}")
        st.latex(rf"\mu^* =[ {traseu_str} ]")
        st.latex(rf"f(\mu^*) = \lambda_{{{nod_dest}}} = {fmt(cost_total)} \text{{ (valoarea optimă a drumului)}}")
        
        # ----------------------------------------------------------------------
        # AFIȘAREA GRAFULUI FINAL (CU TRASEUL EVIDENȚIAT)
        # ----------------------------------------------------------------------
        st.markdown("<h3 style='color: #e65c00; margin-top: 30px;'>🎯 Evidențierea Traseului Optim pe Graf</h3>", unsafe_allow_html=True)
        graf_final = deseneaza_graf(edited_df, drum_optim=drum)
        st.graphviz_chart(graf_final, use_container_width=True)
