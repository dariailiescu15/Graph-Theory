import streamlit as st
import pandas as pd
import numpy as np
import graphviz

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
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 20px; }
    .matrix-table td { border: 1px solid #000; width: 60px; height: 60px; text-align: center; vertical-align: middle; position: relative; }
    
    .t1 { background-color: #ffffff; } /* Neacoperite */
    .t2 { background-color: #ffcc80; } /* Tăietură (Portocaliu) */
    .t3 { background-color: #e67300; } /* Intersecție (Portocaliu închis) */
    
    .boxed { border: 2px solid black; padding: 4px; font-weight: bold; }
    .crossed { text-decoration: line-through; color: #777; }
    .star { color: red; font-weight: bold; font-size: 25px; }
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
# 2. LOGICA MANUALĂ A ALGORITMULUI
# ==============================================================================

def procedura_incadrare_manuala(mat):
    """
    Alege zerourile conform regulii: 
    Linia cu cele mai puține zerouri -> Încadrează primul -> Barează restul pe linie/coloană.
    """
    n = mat.shape[0]
    boxed = []
    crossed = []
    
    temp_mat = mat.copy()
    rows_done = [False] * n
    cols_done = [False] * n

    while True:
        # Numărăm zerourile disponibile pe fiecare linie care nu e gata
        zero_counts = []
        for i in range(n):
            if not rows_done[i]:
                count = sum(1 for j in range(n) if temp_mat[i, j] == 0 and not cols_done[j])
                if count > 0:
                    zero_counts.append((count, i))
        
        if not zero_counts:
            break
        
        # Alegem linia cu cel mai mic număr de zerouri (minim > 0)
        zero_counts.sort()
        _, best_row = zero_counts[0]
        
        # Găsim primul zero disponibil pe acea linie
        for j in range(n):
            if temp_mat[best_row, j] == 0 and not cols_done[j]:
                boxed.append((best_row, j))
                rows_done[best_row] = True
                cols_done[j] = True
                
                # Barăm restul zerourilor de pe acea linie și coloană
                for k in range(n):
                    if temp_mat[best_row, k] == 0 and k != j:
                        crossed.append((best_row, k))
                    if temp_mat[k, j] == 0 and k != best_row:
                        crossed.append((k, j))
                break
    return boxed, crossed

def procedura_marcaj_stea(mat, boxed, crossed):
    """
    Regula marcajului cu stea (*) conform caietului.
    """
    n = mat.shape[0]
    boxed_rows = {r for r, c in boxed}
    
    # 1. Marcăm liniile fără 0 încadrat
    marked_rows = set(range(n)) - boxed_rows
    marked_cols = set()
    
    changed = True
    while changed:
        changed = False
        # 2. Marcăm coloanele care au 0 barat pe linii marcate
        for r, c in crossed:
            if r in marked_rows and c not in marked_cols:
                marked_cols.add(c)
                changed = True
        # 3. Marcăm liniile care au 0 încadrat pe coloane marcate
        for r, c in boxed:
            if c in marked_cols and r not in marked_rows:
                marked_rows.add(r)
                changed = True
                
    # Suportul minim (tăieturi): Linii NEMARCATE și Coloane MARCATE
    cov_rows = [i for i in range(n) if i not in marked_rows]
    cov_cols = list(marked_cols)
    return cov_rows, cov_cols, marked_rows, marked_cols

def get_html_table(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols):
    n = mat.shape[0]
    boxed_set = set(boxed)
    crossed_set = set(crossed)
    
    html = '<table class="matrix-table"><tr><td></td>'
    for j in range(n):
        s = '<span class="star">*</span>' if j in m_cols else ''
        html += f'<td>y{j+1}{s}</td>'
    html += '</tr>'
    
    for i in range(n):
        s = '<span class="star">*</span>' if i in m_rows else ''
        html += f'<tr><td>x{i+1}{s}</td>'
        for j in range(n):
            cls = "t1"
            if i in r_cov and j in c_cov: cls = "t3"
            elif i in r_cov or j in c_cov: cls = "t2"
            
            val = int(mat[i, j])
            content = f"{val}"
            if (i, j) in boxed_set: content = f'<span class="boxed">0</span>'
            elif (i, j) in crossed_set: content = f'<span class="crossed">0</span>'
            
            html += f'<td class="{cls}">{content}</td>'
        html += '</tr>'
    return html + "</table>"

# ==============================================================================
# 3. INTERFAȚĂ
# ==============================================================================

st.subheader("Date de intrare")
if "matrix" not in st.session_state:
    # Exemplu din curs pagina 4/7
    st.session_state.matrix = pd.DataFrame([
        [99, 21, 53, 46, 18, 80],
        [34, 20, 79, 65, 11, 14],
        [76, 10, 73, 56, 47, 42],
        [79, 39, 76, 80, 81, 24],
        [37, 95, 89, 83, 73, 19],
        [74, 54, 91, 34, 20, 85]
    ])

df_in = st.data_editor(st.session_state.matrix, use_container_width=True)

if st.button("Execută pas cu pas (începând cu I0)", type="primary"):
    mat_orig = df_in.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]
    
    # Pas 1: Reducere
    st.markdown("### Reducerea inițială (Linii apoi Coloane)")
    row_m = mat.min(axis=1, keepdims=True)
    mat -= row_m
    col_m = mat.min(axis=0, keepdims=True)
    mat -= col_m
    st.write(f"Suma minime linii: {int(np.sum(row_m))}, Suma minime coloane: {int(np.sum(col_m))}")
    
    iter_idx = 0
    sigmas = []

    # Iterațiile
    while iter_idx < 10:
        boxed, crossed = procedura_incadrare_manuala(mat)
        r_cov, c_cov, m_rows, m_cols = procedura_marcaj_stea(mat, boxed, crossed)
        
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        
        # Afișare stare curentă
        st.markdown(get_html_table(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols), unsafe_allow_html=True)
        
        # Test oprire
        if len(boxed) == n:
            st.success(f"STOP! Numărul de zerouri încadrate ({len(boxed)}) este egal cu ordinul matricei.")
            break
        
        # Calcul Epsilon (Sigma) din elementele neacoperite (T1)
        t1_vals = []
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov:
                    t1_vals.append(mat[r, c])
        
        epsilon = min(t1_vals)
        sigmas.append((epsilon, len(r_cov) + len(c_cov)))
        st.write(f"Elementul minim neacoperit: **$\epsilon = {int(epsilon)}$**")
        
        # Ajustare
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= epsilon # T1
                if r in r_cov and j in c_cov: mat[r, c] += epsilon      # T3
        
        iter_idx += 1
        st.divider()

    # Final
    st.markdown("### Soluția Finală")
    v_final = 0
    for r, c in boxed:
        v_final += mat_orig[r, c]
        st.write(f"Afectare: x{r+1} -> y{c+1} (Cost: {int(mat_orig[r, c])})")
    st.subheader(f"Cost Total: {int(v_final)}")
