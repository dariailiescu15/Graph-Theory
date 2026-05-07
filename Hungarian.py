import streamlit as st
import pandas as pd
import numpy as np
import graphviz
from scipy.optimize import linear_sum_assignment

# ==============================================================================
# 1. IDENTITATE VIZUALĂ (TITLU ȘI AUTORI)
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
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Helvetica', sans-serif; font-size: 18px; }
    .matrix-table td { border: 1px solid #cc5200; width: 45px; height: 45px; text-align: center; vertical-align: middle; }
    .t1 { background-color: #ffffff; } /* Neacoperite */
    .t2 { background-color: #ffe8cc; } /* Acoperite o dată (Tăieturi) */
    .t3 { background-color: #ffc299; border: 2px solid #e65c00 !important; } /* Intersecții */
    </style>
""", unsafe_allow_html=True)

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

# ==============================================================================
# 2. FUNCȚII DE CALCUL (ALGORITMUL DETALIAT)
# ==============================================================================

def procedura_marcaj(mat):
    """
    Simulează procedura de marcaj lateral cu '*' pentru a determina suportul minim.
    Conform Pasului 4 din curs.
    """
    n = mat.shape[0]
    # Găsim un cuplaj (zerouri independente)
    row_ind, col_ind = linear_sum_assignment(mat != 0)
    indep_zeros = [(r, c) for r, c in zip(row_ind, col_ind) if mat[r, c] == 0]
    
    matched_rows = {r for r, c in indep_zeros}
    # 1. Marcăm liniile care nu au niciun '0' incadrat (pătrat)
    marked_rows = set(range(n)) - matched_rows
    marked_cols = set()
    
    changed = True
    while changed:
        changed = False
        # 2. Marcăm coloanele care conțin '0' barat (X) în liniile marcate
        for r in list(marked_rows):
            for c in range(n):
                if mat[r, c] == 0 and (r, c) not in indep_zeros and c not in marked_cols:
                    marked_cols.add(c)
                    changed = True
        # 3. Marcăm liniile care au '0' incadrat în coloanele marcate
        for r, c in indep_zeros:
            if c in marked_cols and r not in marked_rows:
                marked_rows.add(r)
                changed = True
                
    # Tăieturile (Suportul minim): Liniile nemarcate + Coloanele marcate
    cov_rows = [i for i in range(n) if i not in marked_rows]
    cov_cols = list(marked_cols)
    return cov_rows, cov_cols, indep_zeros

def format_matrix_html(mat, r_cov, c_cov):
    """Generează tabelul colorat conform T1, T2, T3 din curs."""
    html = '<table class="matrix-table">'
    for i in range(mat.shape[0]):
        html += "<tr>"
        for j in range(mat.shape[1]):
            is_r = i in r_cov
            is_c = j in c_cov
            cls = "t1"
            if is_r and is_c: cls = "t3"
            elif is_r or is_c: cls = "t2"
            
            val = int(mat[i, j])
            style = "color:red; font-weight:bold;" if val == 0 else ""
            html += f'<td class="{cls}" style="{style}">{val}</td>'
        html += "</tr>"
    return html + "</table>"

# ==============================================================================
# 3. INTERFAȚĂ ȘI INPUT
# ==============================================================================

col_m, col_cfg = st.columns([2, 1])

with col_cfg:
    st.subheader("⚙️ Setări")
    tip = st.selectbox("Tipul problemei:", ["Minimizare (Vmin)", "Maximizare (Vmax)"])
    st.write("---")
    st.info("**Legendă:**\n- Alb: T1 (Netăiate)\n- Galben: T2 (Tăiate)\n- Portocaliu: T3 (Intersecții)")

with col_m:
    st.subheader("📊 Matricea Costurilor ($C$)")
    if "data_ungar" not in st.session_state:
        # Datele din curs (Pag 8)
        c_curs = [[4,3,6,2,6,8],[5,4,8,3,8,9],[5,6,8,2,8,7],[4,5,7,2,7,8],[4,6,6,3,6,7],[6,6,8,3,8,9]]
        st.session_state.data_ungar = pd.DataFrame(c_curs)
    
    mat_input = st.data_editor(st.session_state.data_ungar, use_container_width=True)

# ==============================================================================
# 4. EXECUȚIE ALGORITM
# ==============================================================================

if st.button("Execută Algoritmul Ungar", type="primary", use_container_width=True):
    orig = mat_input.values.copy()
    mat = orig.astype(float)
    n = mat.shape[0]
    
    st.markdown("### PAS 1: Matricea inițială și reducerile")
    
    # Tratare Maximizare conform cursului
    if tip == "Maximizare (Vmax)":
        val_maxima = np.max(mat)
        st.write(f"Problema este de maximizare. Scădem fiecare element din valoarea maximă: **{int(val_maxima)}**")
        mat = val_maxima - mat
        st.markdown(format_matrix_html(mat, [], []), unsafe_allow_html=True)

    # Scădere minime pe linii (MIN L)
    min_l = mat.min(axis=1, keepdims=True)
    mat -= min_l
    # Scădere minime pe coloane (MIN C)
    min_c = mat.min(axis=0, keepdims=True)
    mat -= min_c
    
    st.write("**Matricea după crearea de zerouri (Linii și Coloane):**")
    st.markdown(format_matrix_html(mat, [], []), unsafe_allow_html=True)
    st.latex(r"\sum MIN(L) = " + str(int(np.sum(min_l))) + r", \quad \sum MIN(C) = " + str(int(np.sum(min_c))))

    # Iterații începând cu I0
    iter_idx = 0
    sigmas = []
    
    while iter_idx < 10:
        r_cov, c_cov, cuplaj = procedura_marcaj(mat)
        m = len(r_cov) + len(c_cov)
        
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write(f"Număr tăieturi: **m = {m}**")
            if m == n:
                st.success(f"**STOP!** $m = n = {n}$. Avem cuplaj maxim.")
                break
            else:
                st.warning(f"$m < n$ ({m} < {n}) $\implies$ Se trece la $I_{iter_idx+1}$")
                
        with col2:
            st.markdown(format_matrix_html(mat, r_cov, c_cov), unsafe_allow_html=True)
        
        # Determinare Sigma din elementele netăiate (T1)
        t1_elements = []
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov:
                    t1_elements.append(mat[r, c])
        
        sigma = min(t1_elements)
        sigmas.append((sigma, m))
        st.latex(r"\Sigma_{" + str(iter_idx) + r"} = \min(T_1) = " + str(int(sigma)))
        
        # Deplasarea zerourilor
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= sigma  # Scădem din T1
                if r in r_cov and c in c_cov: mat[r, c] += sigma      # Adunăm în T3
        
        iter_idx += 1
        st.divider()

    # Rezultate
    st.markdown("### 🏆 Soluția Finală")
    c_res1, c_res2 = st.columns(2)
    
    with c_res1:
        st.write("**Repartizarea optimă:**")
        v_final = 0
        for r, c in cuplaj:
            cost = int(orig[r, c])
            v_final += cost
            st.write(f"- Muncitor $x_{r+1} \longrightarrow$ Sarcina $y_{c+1}$ (Cost: {cost})")
        st.subheader(f"Valoarea Optimă: {v_final}")
        
    with c_res2:
        # Graful bipartit final
        graf = graphviz.Digraph()
        graf.attr(rankdir='LR')
        for i in range(n): graf.node(f'X{i}', f'x{i+1}', color='blue')
        for j in range(n): graf.node(f'Y{j}', f'y{j+1}', color='red')
        for r, c in cuplaj:
            graf.edge(f'X{r}', f'Y{c}', label=str(int(orig[r, c])))
        st.graphviz_chart(graf)

    # Verificarea analitică conform paginii 16 din curs
    st.info("**Verificare conform curs:**")
    suma_min = np.sum(min_l) + np.sum(min_c)
    suma_sig = sum([s * (n - mv) for s, mv in sigmas])
    
    if tip == "Minimizare (Vmin)":
        st.latex(r"V_{min} = \sum MIN(L) + \sum MIN(C) + \sum \Sigma_k(n - m_k)")
        st.write(f"Calcul: {int(suma_min)} + {int(suma_sig)} = {int(suma_min + suma_sig)}")
