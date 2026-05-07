import streamlit as st
import pandas as pd
import numpy as np
import graphviz
from scipy.optimize import linear_sum_assignment

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI
# ==============================================================================
st.set_page_config(page_title="Algoritmul Ungar", layout="wide", page_icon="🧩")

st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin-top: 10px; font-style: italic;}
    
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    
    .validation-box { background-color: #fff4ea; border-left: 5px solid #e65c00; padding: 15px; margin-top: 20px; color: #333; }
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Helvetica', sans-serif; font-size: 18px; }
    .matrix-table td { border: 1px solid #cc5200; width: 45px; height: 45px; text-align: center; vertical-align: middle; }
    
    .legend-box { display: flex; justify-content: center; gap: 20px; margin-bottom: 15px; font-size: 15px; }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .color-box { width: 20px; height: 20px; border: 1px solid #ccc; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# ALGORITMI MATEMATICI: ACOPERIREA ZEROURILOR (TEOREMA LUI KŐNIG)
# ==============================================================================
def minim_linii_acoperire(mat):
    """Aplică Teorema lui Kőnig pentru determinarea acoperirii minime a zerourilor."""
    n = mat.shape[0]
    
    bool_mat = np.where(mat == 0, 0, 1)
    row_ind, col_ind = linear_sum_assignment(bool_mat)
    
    matches =[(r, c) for r, c in zip(row_ind, col_ind) if mat[r, c] == 0]
    
    matched_rows = set([r for r, c in matches])
    unmatched_rows = set(range(n)) - matched_rows
    
    visited_rows = set(unmatched_rows)
    visited_cols = set()
    queue = list(unmatched_rows)
    
    while queue:
        r = queue.pop(0)
        for c in range(n):
            if mat[r, c] == 0 and c not in visited_cols:
                visited_cols.add(c)
                r_matched =[mr for mr, mc in matches if mc == c]
                if r_matched:
                    mr = r_matched[0]
                    if mr not in visited_rows:
                        visited_rows.add(mr)
                        queue.append(mr)
                        
    covered_rows = set(range(n)) - visited_rows
    covered_cols = visited_cols
    
    return list(covered_rows), list(covered_cols), matches

# ==============================================================================
# MODULUL DE REPREZENTARE GRAFICĂ ȘI VIZUALĂ
# ==============================================================================
def deseneaza_graf_bipartit(mat_originala, assignment):
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', splines='false', bgcolor='transparent')
    graf.attr('node', shape='circle', style='filled', fillcolor='#f8f9fa', color='#e65c00', fontcolor='#e65c00', fontname='Helvetica', penwidth='2')
    
    n = mat_originala.shape[0]
    
    with graf.subgraph(name='cluster_X') as c:
        c.attr(color='transparent')
        for i in range(n):
            c.node(f"x{i+1}", f"x{i+1}")
            
    with graf.subgraph(name='cluster_Y') as c:
        c.attr(color='transparent')
        for j in range(n):
            c.node(f"y{j+1}", f"y{j+1}")
            
    for r, c in assignment:
        cost = int(mat_originala[r, c])
        graf.edge(f"x{r+1}", f"y{c+1}", label=str(cost), color='#e65c00', penwidth='3', fontcolor='#cc5200', fontsize='14', fontname='Helvetica-bold')
        
    return graf

def genereaza_html_matrice(mat, cov_r=None, cov_c=None):
    if cov_r is None: cov_r =[]
    if cov_c is None: cov_c =[]
    
    n = mat.shape[0]
    
    html = '''
    <div class="legend-box">
        <div class="legend-item"><div class="color-box" style="background-color:#ffffff;"></div> T₁ (Neacoperit)</div>
        <div class="legend-item"><div class="color-box" style="background-color:#ffe8cc;"></div> T₂ (Acoperit 1 dată)</div>
        <div class="legend-item"><div class="color-box" style="background-color:#ffc299;"></div> T₃ (Intersecție/Dublu)</div>
    </div>
    <table class="matrix-table">
    '''
    
    for i in range(n):
        html += "<tr>"
        for j in range(n):
            val = int(mat[i, j])
            is_zero = (val == 0)
            
            bg_color = "#ffffff"
            if i in cov_r and j in cov_c:
                bg_color = "#ffc299" # T3
            elif i in cov_r or j in cov_c:
                bg_color = "#ffe8cc" # T2
                
            color = "#cc5200" if is_zero else "#333333"
            fw = "bold" if is_zero else "normal"
            
            html += f"<td style='background-color:{bg_color}; color:{color}; font-weight:{fw};'>{val}</td>"
        html += "</tr>"
    html += "</table>"
    return html

# ==============================================================================
# INTERFAȚA APLICAȚIEI (STREAMLIT)
# ==============================================================================
st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Probleme de afectare: Algoritmul Ungar (Kuhn-Munkres)</p>
    </div>
    
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

col_tabel, col_explicatii = st.columns([1, 1])

with col_tabel:
    st.markdown("#### Matricea Costurilor ($C$)")
    st.write("Datele inițiale reprezintă costurile. Exemplul implicit reflectă rezolvarea din curs care obține costul final de $166$.")
    
    if "matrice_ungar" not in st.session_state:
        # Datele exacte din notițele scrise de mână (soluție = 166)
        date_initiale = [[55, 23, 83, 61, 66, 22],[99, 81, 14, 77, 61, 55],[59, 39, 58, 49, 24, 54],[36, 10, 37, 62, 28, 33],[73, 51, 51, 24, 26, 55],[72, 54, 78, 91, 89, 96]
        ]
        cols = [f"y_{i+1}" for i in range(6)]
        idx =[f"x_{i+1}" for i in range(6)]
        st.session_state.matrice_ungar = pd.DataFrame(date_initiale, columns=cols, index=idx)

    df_mat = st.data_editor(st.session_state.matrice_ungar, use_container_width=True)

with col_explicatii:
    st.markdown('''
        <div class="validation-box" style="margin-top: 0;">
            <b>Obiectiv:</b> Determinarea unui cuplaj maxim de valoare optimă (minimă) în graful simplu bipartit.<br><br>
            <b>Model matematic:</b>
            <br>Fie <i>X</i> resursele și <i>Y</i> sarcinile. Căutăm să minimizăm costul total:
            $$ V(W_{max}) = \sum_{(x_i, y_j) \in W_{max}} c_{ij} $$
        </div>
    ''', unsafe_allow_html=True)

if st.button("Execută Algoritmul Ungar", type="primary", use_container_width=True):
    st.divider()
    
    mat_orig = df_mat.values.copy()
    mat = mat_orig.copy()
    n = mat.shape[0]
    
    sum_min_l = 0
    sum_min_c = 0
    istoric_sigma =[]
    str_min_l_calc = ""
    str_min_c_calc = ""
    
    st.markdown("### Etapele Analitice ale Algoritmului")
    
    # --------------------------------------------------------------------------
    # PAS 1: Crearea de zerouri (scăderea minimului pe linii și coloane)
    # --------------------------------------------------------------------------
    with st.expander("PASUL 1: Reducerea Matricei (Crearea Zerourilor)", expanded=True):
        col_m1, col_m2 = st.columns([1.2, 1])
        
        min_l = mat.min(axis=1, keepdims=True)
        mat = mat - min_l
        sum_min_l = int(min_l.sum())
        str_min_l_calc = " + ".join([str(int(v)) for v in min_l.flatten()])
        
        min_c = mat.min(axis=0, keepdims=True)
        mat = mat - min_c
        sum_min_c = int(min_c.sum())
        str_min_c_calc = " + ".join([str(int(v)) for v in min_c.flatten()])
        
        with col_m1:
            st.write("**A. Scăderea pe Linii ($MIN(L)$):** Se identifică și se extrage minimul de pe fiecare linie.")
            st.latex(r"\sum MIN(L) = " + str_min_l_calc + f" = {sum_min_l}")
            
            st.write("**B. Scăderea pe Coloane ($MIN(C)$):** Pentru matricea rezultată, se scade minimul fiecărei coloane.")
            st.latex(r"\sum MIN(C) = " + str_min_c_calc + f" = {sum_min_c}")
            
        with col_m2:
            st.markdown(genereaza_html_matrice(mat), unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # PAS 2 & 3: Iterare (Acoperire și Deplasare)
    # --------------------------------------------------------------------------
    iteratie = 1
    while True:
        cov_r, cov_c, assignment = minim_linii_acoperire(mat)
        m_lines = len(cov_r) + len(cov_c)
        
        if m_lines == n:
            with st.expander(f"Iterația {iteratie} - Testul de optimalitate", expanded=True):
                col_i1, col_i2 = st.columns([1.2, 1])
                with col_i1:
                    st.success(f"**STOP Algoritm!**")
                    st.write(f"Numărul minim de linii pentru a acoperi toate zerourile este $m = {m_lines}$.")
                    st.latex(r"m = n = " + str(n) + r" \implies \text{Soluție optimă (Cuplaj Maxim)}")
                with col_i2:
                    st.markdown(genereaza_html_matrice(mat, cov_r, cov_c), unsafe_allow_html=True)
            break
            
        else:
            with st.expander(f"Iterația {iteratie} - Deplasarea zerourilor ($m < n$)", expanded=False):
                col_i1, col_i2 = st.columns([1.2, 1])
                with col_i1:
                    st.warning(f"**Se impune o deplasare!** Numărul de linii $m = {m_lines} < {n}$.")
                    
                    st.latex(r"T_1 = \text{elemente netăiate}")
                    st.latex(r"T_2 = \text{elemente tăiate o singură dată}")
                    st.latex(r"T_3 = \text{elemente dublu tăiate (intersecții)}")
                    
                    uncovered =[]
                    for i in range(n):
                        for j in range(n):
                            if i not in cov_r and j not in cov_c:
                                uncovered.append(mat[i, j])
                                
                    sigma_val = min(uncovered)
                    st.latex(r"\Sigma_{" + str(iteratie) + r"} = \min(T_1) = " + str(int(sigma_val)))
                    
                    istoric_sigma.append((sigma_val, m_lines))
                    
                    st.write("Aplicăm deplasarea:")
                    st.latex(r"T_1 \leftarrow T_1 - \Sigma_{" + str(iteratie) + r"}")
                    st.latex(r"T_3 \leftarrow T_3 + \Sigma_{" + str(iteratie) + r"}")
                    
                with col_i2:
                    st.markdown(genereaza_html_matrice(mat, cov_r, cov_c), unsafe_allow_html=True)
                    
                for i in range(n):
                    for j in range(n):
                        if i not in cov_r and j not in cov_c:
                            mat[i, j] -= sigma_val
                        if i in cov_r and j in cov_c:
                            mat[i, j] += sigma_val
                            
        iteratie += 1
        if iteratie > 20: break 

    # --------------------------------------------------------------------------
    # SOLUȚIA FINALĂ ȘI GRAFUL
    # --------------------------------------------------------------------------
    st.divider()
    st.markdown("### 🏆 Soluția Finală și Graful Bipartit")
    
    col_rez1, col_rez2 = st.columns([1.2, 1])
    
    assignment.sort(key=lambda x: x[0])
    cost_total = 0
    str_costuri =[]
    for r, c in assignment:
        val = mat_orig[r, c]
        cost_total += val
        str_costuri.append(str(int(val)))
        
    with col_rez1:
        st.markdown('''
            <div class="validation-box" style="margin-top: 0; background-color: #f8f9fa;">
                <h4 style="color:#e65c00; margin-top:0;">Cuplajul Maxim ($W_{max}$)</h4>
            </div>
        ''', unsafe_allow_html=True)
        
        str_cuplaje = ", ".join([f"(x_{r+1}, y_{c+1})" for r, c in assignment])
        st.latex(r"W_{max} = \{ " + str_cuplaje + r" \}")
        st.latex(r"V(W_{max}) = " + " + ".join(str_costuri) + f" = {int(cost_total)}")

    with col_rez2:
        st.graphviz_chart(deseneaza_graf_bipartit(mat_orig, assignment), use_container_width=True)

    # --------------------------------------------------------------------------
    # VALIDAREA SOLUȚIEI PE BAZA TEOREMEI (Validarea pe parcurs și de final)
    # --------------------------------------------------------------------------
    st.divider()
    st.markdown("### ✅ Validarea Analitică a Soluției")
    st.write("Pentru validarea corectitudinii algoritmului, reconstruim costul global folosind minimele extrase în parcurgeri:")
    
    st.latex(r"V(W_{max}) = \sum MIN(L) + \sum MIN(C) + \sum_{k} \Sigma_k(n - m_k)")
    
    # Construim șirul ecuației cu paranteze la fel ca în notițele scrise
    termeni_formule =[f"({str_min_l_calc})", f"({str_min_c_calc})"]
    calc_sigmas = 0
    
    if istoric_sigma:
        for sig, m_val in istoric_sigma:
            termeni_formule.append(f"{int(sig)}({n} - {m_val})")
            calc_sigmas += sig * (n - m_val)
            
    str_formula_completa = " + ".join(termeni_formule)
    val_total = sum_min_l + sum_min_c + calc_sigmas
    
    st.latex(r"V(W_{max}) = " + str_formula_completa)
    st.latex(r"V(W_{max}) = " + f"{sum_min_l} + {sum_min_c}" + (f" + {int(calc_sigmas)}" if calc_sigmas > 0 else "") + f" = {int(val_total)} \quad \checkmark")
    
    if int(val_total) == int(cost_total):
        st.success(f"**Verificare reușită!** Demonstrația analitică confirmă rezultatul obținut pe graful bipartit.")
