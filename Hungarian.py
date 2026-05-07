import streamlit as st
import pandas as pd
import numpy as np
import graphviz

# 1. SETĂRI PAGINĂ ȘI DESIGN (CSS)
st.set_page_config(page_title="Algoritmul UNGAR - Studiu Academic", layout="wide", page_icon="🧩")

# Definirea stilurilor pentru culori (T1, T2, T3) și simboluri (0 încadrat/barat)
st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin-top: 10px; font-style: italic;}
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    
    /* Tabelul academic */
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 18px; border: 2px solid #333; }
    .matrix-table td { border: 1px solid #333; width: 60px; height: 60px; text-align: center; vertical-align: middle; }
    
    /* Culorile T1, T2, T3 conform cursului */
    .t1 { background-color: #ffffff; } 
    .t2 { background-color: #ffb366; } /* Portocaliu - Tăietură */
    .t3 { background-color: #e67300; } /* Portocaliu închis - Intersecție */
    .min-cell { background-color: #e3f2fd; color: #0d47a1; font-weight: bold; border: 2px solid #1565c0 !important; }
    
    /* Simboluri corectate pentru a evita erorile de randare */
    .boxed-zero { border: 2px solid black; padding: 4px; font-weight: bold; display: inline-block; background: white; line-height: 1; }
    .crossed-zero { text-decoration: line-through; color: #777; font-weight: bold; }
    .star-sym { color: red; font-weight: bold; font-size: 24px; margin-left: 5px; }
    .academic-note { background-color: #f1f8e9; border-left: 5px solid #4caf50; padding: 15px; margin: 10px 0; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ANTET (Titlu și Autori)
st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Algoritmul UNGAR (AU) - Soluționarea Problemelor de Afectare</p>
    </div>
    <div class="authors-box">
        <div class="authors-title">Facultatea de Științe Aplicate</div>
        <div class="authors-names">Dedu Anișoara-Nicoleta, 1333a<br>Dumitrescu Andreea Mihaela, 1333a<br>Iliescu Daria-Gabriela, 1333a<br>Lungu Ionela-Diana, 1333a</div>
    </div>
''', unsafe_allow_html=True)

# 2. LOGICA MATEMATICĂ (FUNCȚII)
def repartizare_manuala_zerouri(mat):
    """Încadrarea și bararea zerourilor conform regulii liniei cu cele mai puține zerouri."""
    n = mat.shape[0]
    boxed, crossed = [], []
    r_done, c_done = [False] * n, [False] * n
    m_temp = mat.copy()
    while True:
        candidates = []
        for i in range(n):
            if not r_done[i]:
                z_cols = [j for j in range(n) if m_temp[i,j] == 0 and not c_done[j]]
                if z_cols: candidates.append((len(z_cols), i, z_cols))
        if not candidates: break
        candidates.sort() 
        _, r_idx, available_cols = candidates[0]
        c_idx = available_cols[0]
        boxed.append((r_idx, c_idx))
        r_done[r_idx], c_done[c_idx] = True, True
        for j in range(n):
            if m_temp[r_idx, j] == 0 and j != c_idx: crossed.append((r_idx, j))
            if m_temp[j, c_idx] == 0 and j != r_idx: crossed.append((j, c_idx))
    return sorted(boxed), list(set(crossed))

def procedura_marcaj_lateral(mat, boxed, crossed):
    """Determinarea suportului minim (tăieturile) prin marcaj lateral."""
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
    return [i for i in range(n) if i not in m_rows], list(m_cols), m_rows, m_cols

def draw_matrix(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols, r_mins=None, c_mins=None):
    """Generare HTML pentru matrice."""
    n = mat.shape[0]
    bx, cr = set(boxed), set(crossed)
    html = '<table class="matrix-table"><tr><td></td>'
    for j in range(n):
        s = '<span class="star-sym">*</span>' if j in m_cols else ''
        html += f'<td>y{j+1}{s}</td>'
    if r_mins is not None: html += '<td class="min-cell">MIN L</td>'
    html += '</tr>'
    for i in range(n):
        s = '<span class="star-sym">*</span>' if i in m_rows else ''
        html += f'<tr><td>x{i+1}{s}</td>'
        for j in range(n):
            cls = "t3" if i in r_cov and j in c_cov else ("t2" if i in r_cov or j in c_cov else "t1")
            content = f'<span class="boxed-zero">0</span>' if (i,j) in bx else (f'<span class="crossed-zero">0</span>' if (i,j) in cr else str(int(mat[i,j])))
            html += f'<td class="{cls}">{content}</td>'
        if r_mins is not None: html += f'<td class="min-cell">{int(r_mins[i])}</td>'
        html += '</tr>'
    if c_mins is not None:
        html += '<tr><td class="min-cell">MIN C</td>'
        for v in c_mins: html += f'<td class="min-cell">{int(v) if v > 0 else "-"}</td>'
        html += '<td></td></tr>'
    return html + "</table>"

# 3. INTERFAȚĂ ȘI DATE
seminar_data = [[99, 21, 53, 46, 18, 80], [34, 20, 79, 65, 11, 14], [76, 10, 73, 56, 47, 42], [79, 39, 76, 80, 81, 24], [37, 95, 89, 83, 73, 19], [74, 54, 91, 34, 20, 85]]
st.subheader("I. Datele problemei")
df_in = st.data_editor(pd.DataFrame(seminar_data, columns=[f"y{i+1}" for i in range(6)], index=[f"x{i+1}" for i in range(6)]), use_container_width=True)
tip_opt = st.selectbox("Obiectivul algoritmului:", ["Minimizare (Vmin)", "Maximizare (Vmax)"])

if st.button("Execută Algoritmul Ungar", type="primary", use_container_width=True):
    mat_orig = df_in.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]

    # PAS 1: REDUCERE
    st.markdown("### PAS 1: Etapa de Reducere a Matricei")
    if tip_opt == "Maximizare (Vmax)":
        mat = np.max(mat) - mat
    r_mins = mat.min(axis=1)
    st.markdown(draw_matrix(mat, [], [], [], [], set(), set(), r_mins=r_mins), unsafe_allow_html=True)
    for i in range(n): mat[i, :] -= r_mins[i]
    c_mins = np.zeros(n)
    for j in range(n):
        if not np.any(mat[:, j] == 0):
            c_mins[j] = mat[:, j].min()
    st.markdown(draw_matrix(mat, [], [], [], [], set(), set(), c_mins=c_mins), unsafe_allow_html=True)
    for j in range(n): mat[:, j] -= c_mins[j]

    # PAS 2: ITERAȚII
    st.markdown("### PAS 2: Procesul Iterativ de Afectare")
    st.markdown('<div class="academic-note"><b>Definiție:</b> m reprezintă numărul de zerouri încadrate (cuplajul maximal).</div>', unsafe_allow_html=True)
    iter_idx, history_eps, final_bx = 0, [], []
    
    while iter_idx < 10:
        bx, cr = repartizare_manuala_zerouri(mat)
        m = len(bx)
        r_cov, c_cov, m_rows, m_cols = procedura_marcaj_lateral(mat, bx, cr)
        st.divider()
        st.markdown(f"#### Iterația I{iter_idx}")
        col_t, col_m = st.columns([1, 2])
        with col_t:
            st.write(f"**1. Repartizare:** m = {m}")
            st.write(f"**2. Test optimalitate:**")
            if m == n:
                st.success(f"m = n = {n} (Optim)")
                final_bx = bx
                st.markdown(draw_matrix(mat, [], [], bx, cr, set(), set()), unsafe_allow_html=True)
                break
            else:
                st.warning(f"m ({m}) < n ({n}) (Nu e optim)")
        with col_m:
            st.markdown(draw_matrix(mat, r_cov, c_cov, bx, cr, m_rows, m_cols), unsafe_allow_html=True)
        uncovered = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
        eps = min(uncovered)
        history_eps.append((eps, len(r_cov) + len(c_cov)))
        st.latex(rf"\epsilon_{iter_idx} = {int(eps)}")
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= eps
                if r in r_cov and c in c_cov: mat[r, c] += eps
        iter_idx += 1

    # PAS 3: REZULTAT
    st.divider()
    st.markdown("### PAS 3: Rezultat Final")
    v_total = sum(mat_orig[r, c] for r, c in final_bx)
    st.latex(r"W_{max} = \{ " + ", ".join([f"(x_{r+1}, y_{c+1})" for r, c in final_bx]) + r" \}")
    st.markdown(f"#### Valoare Finală: {int(v_total)}")
