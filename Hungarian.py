import streamlit as st
import pandas as pd
import numpy as np
import graphviz

# ==============================================================================
# 1. IDENTITATE VIZUALĂ ȘI STILURI ACADEMICE (T1, T2, T3)
# ==============================================================================
st.set_page_config(page_title="Algoritmul UNGAR - Studiu Academic", layout="wide", page_icon="🧩")

st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin-top: 10px; font-style: italic;}
    
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 18px; border: 2px solid #333; }
    .matrix-table td { border: 1px solid #333; width: 60px; height: 60px; text-align: center; vertical-align: middle; }
    
    /* Clasificare elemente curs */
    .t1 { background-color: #ffffff; } 
    .t2 { background-color: #ffb366; } /* Portocaliu - Tăietură (T2) */
    .t3 { background-color: #e67300; } /* Portocaliu închis - Intersecție (T3) */
    .min-cell { background-color: #e3f2fd; color: #0d47a1; font-weight: bold; border: 2px solid #1565c0 !important; }
    
    .boxed-zero { border: 2px solid black; padding: 4px; font-weight: bold; display: inline-block; background: white; line-height: 1; }
    .crossed-zero { text-decoration: line-through; color: #777; font-weight: bold; }
    .star-sym { color: red; font-weight: bold; font-size: 24px; margin-left: 5px; }
    </style>
""", unsafe_allow_html=True)

# Antet Titlu și Autori
st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Algoritmul UNGAR (AU) - Afectare de Cost Optim</p>
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
# 2. LOGICA MATEMATICĂ (MANUALĂ)
# ==============================================================================

def repartizare_manuala_zerouri(mat):
    n = mat.shape[0]
    boxed, crossed = [], []
    r_done, c_done = [False] * n, [False] * n
    m_temp = mat.copy()
    while True:
        candidates = []
        for i in range(n):
            if not r_done[i]:
                zeros = [j for j in range(n) if m_temp[i,j] == 0 and not c_done[j]]
                if zeros: candidates.append((len(zeros), i, zeros))
        if not candidates: break
        candidates.sort()
        _, r_idx, z_cols = candidates[0]
        c_idx = z_cols[0]
        boxed.append((r_idx, c_idx))
        r_done[r_idx], c_done[c_idx] = True, True
        for j in range(n):
            if m_temp[r_idx, j] == 0 and j != c_idx: crossed.append((r_idx, j))
            if m_temp[j, c_idx] == 0 and j != r_idx: crossed.append((j, c_idx))
    return sorted(boxed), list(set(crossed))

def procedura_marcaj_lateral(mat, boxed, crossed):
    n = mat.shape[0]
    bx_rows = {r for r, c in boxed}
    m_rows = set(range(n)) - bx_rows
    m_cols = set()
    changed = True
    while changed:
        before = len(m_rows) + len(m_cols)
        for r, c in crossed:
            if r in m_rows: m_cols.add(c)
        for r, c in boxed:
            if c in m_cols: m_rows.add(r)
        changed = (len(m_rows) + len(m_cols)) != before
    cov_rows = [i for i in range(n) if i not in m_rows]
    cov_cols = list(m_cols)
    return cov_rows, cov_cols, m_rows, m_cols

def draw_html_matrix(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols, row_mins=None, col_mins=None):
    n = mat.shape[0]
    bx, cr = set(boxed), set(crossed)
    html = '<table class="matrix-table"><tr><td></td>'
    for j in range(n):
        star = '<span class="star-sym">*</span>' if j in m_cols else ''
        html += f'<td>y{j+1}{star}</td>'
    if row_mins is not None: html += '<td class="min-cell">MIN L</td>'
    html += '</tr>'
    for i in range(n):
        star = '<span class="star-sym">*</span>' if i in m_rows else ''
        html += f'<tr><td>x{i+1}{star}</td>'
        for j in range(n):
            cls = "t1"
            if i in r_cov and j in c_cov: cls = "t3"
            elif i in r_cov or j in c_cov: cls = "t2"
            val = int(mat[i, j])
            content = str(val)
            if (i, j) in bx: content = '<span class="boxed-zero">0</span>'
            elif (i, j) in cr: content = '<span class="crossed-zero">0</span>'
            html += f'<td class="{cls}">{content}</td>'
        if row_mins is not None: html += f'<td class="min-cell">{int(row_mins[i])}</td>'
        html += '</tr>'
    if col_mins is not None:
        html += '<tr><td class="min-cell">MIN C</td>'
        for v in col_mins: html += f'<td class="min-cell">{int(v) if v > 0 else "-"}</td>'
        html += '<td></td></tr>'
    return html + "</table>"

# ==============================================================================
# 3. INTERFAȚĂ ȘI SELECȚIE PROBLEMA
# ==============================================================================

seminar_data = [
    [99, 21, 53, 46, 18, 80], [34, 20, 79, 65, 11, 14], [76, 10, 73, 56, 47, 42],
    [79, 39, 76, 80, 81, 24], [37, 95, 89, 83, 73, 19], [74, 54, 91, 34, 20, 85]
]

st.subheader("I. Datele Problemei ")
df_in = st.data_editor(pd.DataFrame(seminar_data, 
                                    columns=[f"y{i+1}" for i in range(6)], 
                                    index=[f"x{i+1}" for i in range(6)]), 
                       use_container_width=True)

col_obj, _ = st.columns([1, 2])
with col_obj:
    tip_opt = st.selectbox("Obiectivul algoritmului:", ["Minimizare (Vmin)", "Maximizare (Vmax)"])

if st.button("Execută Algoritmul Complet", type="primary", use_container_width=True):
    mat_orig = df_in.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]

    st.markdown("### PAS 1: Etapa de Reducere")
    
    if tip_opt == "Maximizare (Vmax)":
        val_max = np.max(mat)
        st.write(f"Problema de maximizare: scădem elementele din Valoarea Maximă = **{int(val_max)}**")
        mat = val_max - mat

    # Reducere Linii
    r_mins = mat.min(axis=1)
    st.markdown(draw_html_matrix(mat, [], [], [], [], set(), set(), row_mins=r_mins), unsafe_allow_html=True)
    for i in range(n): mat[i, :] -= r_mins[i]

    # Reducere Coloane
    c_mins = np.zeros(n)
    for j in range(n):
        if not np.any(mat[:, j] == 0):
            c_mins[j] = mat[:, j].min()
    st.markdown(draw_html_matrix(mat, [], [], [], [], set(), set(), col_mins=c_mins), unsafe_allow_html=True)
    for j in range(n): mat[:, j] -= c_mins[j]

    # Iterații
    iter_idx = 0
    history_eps = []
    final_bx = []

    while iter_idx < 10:
        bx, cr = repartizare_manuala_zerouri(mat)
        r_cov, c_cov, m_rows, m_cols = procedura_marcaj_lateral(mat, bx, cr)
        st.divider()
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        if len(bx) == n:
            st.markdown(draw_html_matrix(mat, [], [], bx, cr, set(), set()), unsafe_allow_html=True)
            st.success(f"Soluție optimă găsită la $I_{iter_idx}$ ($m=n={n}$).")
            final_bx = bx
            break
        else:
            st.markdown(draw_html_matrix(mat, r_cov, c_cov, bx, cr, m_rows, m_cols), unsafe_allow_html=True)
            uncovered = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
            eps = min(uncovered)
            history_eps.append((eps, len(r_cov) + len(c_cov)))
            st.latex(r"\epsilon_{" + str(iter_idx) + r"} = " + str(int(eps)))
            for r in range(n):
                for c in range(n):
                    if r not in r_cov and c not in c_cov: mat[r, c] -= eps
                    if r in r_cov and c in c_cov: mat[r, c] += eps
        iter_idx += 1

    # REZULTAT FINAL
    st.divider()
    st.markdown("### Rezultate Finale")
    w_max_elements = [f"(x_{r+1}, y_{c+1})" for r, c in final_bx]
    st.latex(r"W_{max} = \{ " + ", ".join(w_max_elements) + r" \}")
    v_total = sum(mat_orig[r, c] for r, c in final_bx)
    st.markdown(f"#### Valoare Funcție Obiectiv: $V(W_{{max}}) = {int(v_total)}$")
    
    st.info("**Verificare Analitică:**")
    sum_red = np.sum(r_mins) + np.sum(c_mins)
    sum_eps = sum(e * (n - m) for e, m in history_eps)
    if tip_opt == "Minimizare (Vmin)":
        st.latex(r"V_{min}(W_{max}) = \sum MIN(L) + \sum MIN(C) + \sum \epsilon_k(n - m_k)")
        st.write(f"Calcul: {int(sum_red)} + {int(sum_eps)} = **{int(sum_red + sum_eps)}**")
    else:
        st.write("Verificarea se confirmă prin însumarea elementelor din matricea originală.")
