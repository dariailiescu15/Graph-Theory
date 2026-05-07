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
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 20px; }
    .matrix-table td { border: 1px solid #000; width: 60px; height: 60px; text-align: center; vertical-align: middle; position: relative; }
    
    /* Culori conform cerinței */
    .t1 { background-color: #ffffff; } /* Neacoperite */
    .t2 { background-color: #ffb366; } /* Tăietură (Portocaliu) */
    .t3 { background-color: #e67300; } /* Intersecție (Portocaliu închis) */
    
    .framed-zero { border: 2px solid black; padding: 5px; font-weight: bold; background-color: rgba(255,255,255,0.5); }
    .crossed-zero { text-decoration: line-through; color: #888; }
    .star-label { color: red; font-weight: bold; font-size: 24px; }
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
# 2. LOGICA DE REZOLVARE (PAS CU PAS DIN CURS)
# ==============================================================================

def gaseste_cuplaj(mat):
    """Identifică zerourile încadrate și barate conform regulii de sus în jos."""
    n = mat.shape[0]
    incadrate = []
    barate = []
    randuri_ocupate = set()
    cols_ocupate = set()

    # Parcurgem pentru a găsi zerourile încadrate (cel mult unul pe linie/coloană)
    for i in range(n):
        for j in range(n):
            if mat[i, j] == 0 and i not in randuri_ocupate and j not in cols_ocupate:
                incadrate.append((i, j))
                randuri_ocupate.add(i)
                cols_ocupate.add(j)
            elif mat[i, j] == 0:
                barate.append((i, j))
    return incadrate, barate

def procedura_marcaj_stea(mat, incadrate, barate):
    """Procedura de marcaj lateral cu '*' pentru suportul minim (Pag 8)."""
    n = mat.shape[0]
    incadrate_set = set(incadrate)
    
    marked_rows = set(range(n)) - {r for r, c in incadrate}
    marked_cols = set()
    
    while True:
        old_state = (len(marked_rows), len(marked_cols))
        # Marcam coloane care au 0 barat în linii marcate
        for r in list(marked_rows):
            for c in range(n):
                if mat[r, c] == 0 and (r, c) not in incadrate_set and c not in marked_cols:
                    marked_cols.add(c)
        # Marcam linii care au 0 încadrat în coloane marcate
        for r, c in incadrate:
            if c in marked_cols and r not in marked_rows:
                marked_rows.add(r)
        if (len(marked_rows), len(marked_cols)) == old_state:
            break
            
    # Tăieturi: Linii fără '*' + Coloane cu '*'
    cov_rows = [i for i in range(n) if i not in marked_rows]
    cov_cols = list(marked_cols)
    return cov_rows, cov_cols, marked_rows, marked_cols

def generate_matrix_html(mat, r_cov, c_cov, incadrate, barate, m_rows, m_cols):
    """Generează HTML-ul matricei cu simbolurile din caiet."""
    n = mat.shape[0]
    incadrate_set = set(incadrate)
    barate_set = set(barate)
    
    html = '<table class="matrix-table"><tr><td></td>'
    # Cap de tabel coloane + marcaje stea coloane
    for j in range(n):
        star = '<span class="star-label">*</span>' if j in m_cols else ''
        html += f'<td>y{j+1}{star}</td>'
    html += '</tr>'
    
    for i in range(n):
        star = '<span class="star-label">*</span>' if i in m_rows else ''
        html += f'<tr><td>x{i+1}{star}</td>'
        for j in range(n):
            is_r = i in r_cov
            is_c = j in c_cov
            cls = "t1"
            if is_r and is_c: cls = "t3"
            elif is_r or is_c: cls = "t2"
            
            val = int(mat[i, j])
            content = f"{val}"
            if (i, j) in incadrate_set:
                content = f'<span class="framed-zero">0</span>'
            elif (i, j) in barate_set:
                content = f'<span class="crossed-zero">0</span>'
            
            html += f'<td class="{cls}">{content}</td>'
        html += '</tr>'
    html += '</table>'
    return html

# ==============================================================================
# 3. INTERFAȚĂ ȘI INPUT
# ==============================================================================

if "mat_data" not in st.session_state:
    st.session_state.mat_data = pd.DataFrame([
        [99, 21, 53, 46, 18, 80],
        [34, 20, 79, 65, 11, 14],
        [76, 10, 73, 56, 47, 42],
        [79, 39, 76, 80, 81, 24],
        [37, 95, 89, 83, 73, 19],
        [74, 54, 91, 34, 20, 85]
    ])

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Matricea Costurilor (C)")
    df_input = st.data_editor(st.session_state.mat_data, use_container_width=True)
with col2:
    tip_p = st.radio("Obiectiv:", ["Minimizare (Vmin)", "Maximizare (Vmax)"])
    st.info("**Legendă Culori:**\n- Alb: T1 (Netăiat)\n- Portocaliu: T2 (Tăiat)\n- Portocaliu Închis: T3 (Intersecție)")

# ==============================================================================
# 4. EXECUȚIA ALGORITMULUI
# ==============================================================================

if st.button("Începe Rezolvarea", type="primary", use_container_width=True):
    mat_orig = df_input.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]

    # Pas 1: Reducerea
    st.markdown("### PAS 1: Crearea de zerouri")
    if tip_p == "Maximizare (Vmax)":
        mat = np.max(mat) - mat
        st.write("S-a transformat problema prin scădere din valoarea maximă.")

    min_l = mat.min(axis=1, keepdims=True)
    mat -= min_l
    min_c = mat.min(axis=0, keepdims=True)
    mat -= min_c
    
    st.write("Matricea redusă după $MIN(L)$ și $MIN(C)$:")
    st.markdown(generate_matrix_html(mat, [], [], *gaseste_cuplaj(mat), set(), set()), unsafe_allow_html=True)

    # Iterații
    iter_idx = 0
    istoric_sigmas = []

    while iter_idx < 10:
        incadrate, barate = gaseste_cuplaj(mat)
        r_cov, c_cov, m_rows, m_cols = procedura_marcaj_stea(mat, incadrate, barate)
        m = len(r_cov) + len(c_cov)
        
        st.divider()
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        
        col_text, col_mat = st.columns([1, 2])
        with col_text:
            st.write(f"Număr zerouri încadrate ($\boxed{0}$): **{len(incadrate)}**")
            st.write(f"Număr tăieturi ($m$): **{m}**")
            
            if len(incadrate) == n:
                st.success(f"STOP! Avem {n} zerouri încadrate. Soluție optimă găsită.")
                break
            else:
                st.warning(f"Se continuă marcajul lateral ($*$) și determinarea $\Sigma$.")

        with col_mat:
            st.markdown(generate_matrix_html(mat, r_cov, c_cov, incadrate, barate, m_rows, m_cols), unsafe_allow_html=True)

        # Calcul Sigma (Min din T1)
        t1_vals = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
        sigma = min(t1_vals)
        istoric_sigmas.append((sigma, m))
        st.latex(r"\Sigma_{" + str(iter_idx) + r"} = " + str(int(sigma)))

        # Ajustare T1 (-sigma), T3 (+sigma)
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= sigma
                if r in r_cov and c in c_cov: mat[r, c] += sigma
        
        iter_idx += 1

    # Final
    st.divider()
    st.subheader("🏁 Soluție și Verificare")
    v_total = 0
    repartitii = []
    for r, c in incadrate:
        cost = int(mat_orig[r, c])
        v_total += cost
        repartitii.append(f"x{r+1} -> y{c+1} ({cost})")
    
    st.write("Repartizarea finală: " + ", ".join(repartitii))
    st.markdown(f"## Valoare Finală: {v_total}")

    # Verificare
    sum_m = np.sum(min_l) + np.sum(min_c)
    sum_s = sum([s * (n - m_val) for s, m_val in istoric_sigmas])
    st.info(f"Verificare: {int(sum_m)} (minime) + {int(sum_s)} (sigmas) = {int(sum_m + sum_s)}")
