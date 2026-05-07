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
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 18px; }
    .matrix-table td { border: 1px solid #000; width: 55px; height: 55px; text-align: center; vertical-align: middle; position: relative; }
    
    .t1 { background-color: #ffffff; } /* Neacoperite */
    .t2 { background-color: #ffb366; } /* Tăietură (Portocaliu) */
    .t3 { background-color: #e67300; } /* Intersecție (Portocaliu închis) */
    
    .boxed-zero { border: 2px solid black; padding: 4px; font-weight: bold; background-color: rgba(255,255,255,0.7); }
    .crossed-zero { text-decoration: line-through; color: #888; font-weight: bold; }
    .star-label { color: red; font-weight: bold; font-size: 22px; }
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
# 2. LOGICA MATEMATICĂ (MANUALĂ)
# ==============================================================================

def repartizare_zerouri_manuala(mat):
    """Implementează regula: linia cu cele mai puține zerouri -> încadrează -> barează."""
    n = mat.shape[0]
    boxed = []
    crossed = []
    temp_mat = mat.copy()
    rows_filled = [False] * n
    cols_filled = [False] * n

    while True:
        candidates = []
        for i in range(n):
            if not rows_filled[i]:
                # Numărăm zerourile disponibile pe coloane neocupate
                zeros_in_row = [j for j in range(n) if temp_mat[i, j] == 0 and not cols_filled[j]]
                if zeros_in_row:
                    candidates.append((len(zeros_in_row), i, zeros_in_row))
        
        if not candidates: break
        
        # Alegem linia cu cele mai puține zerouri (conform regulii din curs)
        candidates.sort()
        _, row_idx, available_cols = candidates[0]
        col_idx = available_cols[0] # Alegem primul zero disponibil

        boxed.append((row_idx, col_idx))
        rows_filled[row_idx] = True
        cols_filled[col_idx] = True

        # Barăm restul zerourilor de pe linie și coloană
        for j in range(n):
            if temp_mat[row_idx, j] == 0 and j != col_idx:
                crossed.append((row_idx, j))
            if temp_mat[j, col_idx] == 0 and j != row_idx:
                crossed.append((j, col_idx))
                
    return boxed, list(set(crossed))

def procedura_marcaj_curs(mat, boxed, crossed):
    """Procedura de marcaj lateral cu '*' pentru a afla suportul minim (Pag 8/13)."""
    n = mat.shape[0]
    boxed_rows = {r for r, c in boxed}
    
    # 1. Marcăm liniile care NU au zero încadrat
    m_rows = set(range(n)) - boxed_rows
    m_cols = set()
    
    changed = True
    while changed:
        old_len = len(m_rows) + len(m_cols)
        # 2. Marcăm coloanele care au zerouri barate pe linii marcate
        for r, c in crossed:
            if r in m_rows: m_cols.add(c)
        # 3. Marcăm liniile care au zerouri încadrate pe coloane marcate
        for r, c in boxed:
            if c in m_cols: m_rows.add(r)
        
        changed = (len(m_rows) + len(m_cols)) != old_len

    # Tăieturi conform curs: Linii NEMARCATE + Coloane MARCATE
    cov_rows = [i for i in range(n) if i not in m_rows]
    cov_cols = list(m_cols)
    return cov_rows, cov_cols, m_rows, m_cols

def render_matrix(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols):
    """Randare HTML a matricei cu toate simbolurile cerute."""
    n = mat.shape[0]
    b_set = set(boxed)
    c_set = set(crossed)
    
    html = '<table class="matrix-table"><tr><td></td>'
    for j in range(n):
        s = '<span class="star-label">*</span>' if j in m_cols else ''
        html += f'<td>y{j+1}{s}</td>'
    html += '</tr>'
    
    for i in range(n):
        s = '<span class="star-label">*</span>' if i in m_rows else ''
        html += f'<tr><td>x{i+1}{s}</td>'
        for j in range(n):
            cls = "t1"
            if i in r_cov and j in c_cov: cls = "t3"
            elif i in r_cov or j in c_cov: cls = "t2"
            
            val = int(mat[i, j])
            content = str(val)
            if (i, j) in b_set: content = '<span class="boxed-zero">0</span>'
            elif (i, j) in c_set: content = '<span class="crossed-zero">0</span>'
            
            html += f'<td class="{cls}">{content}</td>'
        html += '</tr>'
    return html + "</table>"

# ==============================================================================
# 3. INTERFAȚĂ UTILIZATOR
# ==============================================================================

if "input_matrix" not in st.session_state:
    # Date implicite (Pag 4 curs)
    st.session_state.input_matrix = pd.DataFrame([
        [99, 21, 53, 46, 18, 80], [34, 20, 79, 65, 11, 14], [76, 10, 73, 56, 47, 42],
        [79, 39, 76, 80, 81, 24], [37, 95, 89, 83, 73, 19], [74, 54, 91, 34, 20, 85]
    ])

c_input, c_type = st.columns([2, 1])
with c_input:
    st.subheader("📊 Matricea Costurilor ($C$)")
    df_data = st.data_editor(st.session_state.input_matrix, use_container_width=True)
with c_type:
    st.subheader("⚙️ Obiectiv")
    tip_p = st.radio("Tipul problemei:", ["Minimizare (Vmin)", "Maximizare (Vmax)"])
    st.write("---")
    st.info("**Legendă Culori:**\n- Portocaliu (T2): Tăietură\n- Portocaliu Închis (T3): Intersecție")

# ==============================================================================
# 4. EXECUȚIE ȘI VALIDARE
# ==============================================================================

if st.button("Execută Algoritmul detaliat (I0...In)", type="primary", use_container_width=True):
    mat_orig = df_data.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]
    
    st.markdown("### 📝 PAS 1: Crearea de zerouri și reduceri")
    
    if tip_p == "Maximizare (Vmax)":
        v_max = np.max(mat)
        st.write(f"Problema de maximizare: scădem elementele din Max = {int(v_max)}")
        mat = v_max - mat
    
    r_mins = mat.min(axis=1, keepdims=True)
    mat -= r_mins
    c_mins = mat.min(axis=0, keepdims=True)
    mat -= c_mins
    
    st.write(f"Suma MIN(L): {int(np.sum(r_mins))} | Suma MIN(C): {int(np.sum(c_mins))}")
    
    iter_idx = 0
    istoric_eps = []

    while iter_idx < 12:
        boxed, crossed = repartizare_zerouri_manuala(mat)
        r_cov, c_cov, m_rows, m_cols = procedura_marcaj_curs(mat, boxed, crossed)
        m_count = len(r_cov) + len(c_cov)
        
        st.divider()
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        
        col_m, col_t = st.columns([2, 1])
        with col_m:
            st.markdown(render_matrix(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols), unsafe_allow_html=True)
        with col_t:
            st.write(f"Zerouri încadrate ($\boxed{0}$): **{len(boxed)}**")
            st.write(f"Linii de tăiere ($m$): **{m_count}**")
            
            if len(boxed) == n:
                st.success(f"STOP! Cuplaj maxim găsit ($m=n={n}$).")
                break
            else:
                st.warning(f"Test optimalitate eșuat ({len(boxed)} < {n}).")
        
        # Calcul Epsilon (min T1)
        t1_vals = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
        epsilon = min(t1_vals)
        istoric_eps.append((epsilon, m_count))
        st.latex(r"\epsilon_{" + str(iter_idx) + r"} = " + str(int(epsilon)))
        
        # Ajustare Matrice
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= epsilon # T1
                if r in r_cov and c in c_cov: mat[r, c] += epsilon      # T3
        
        iter_idx += 1

    # REZULTAT FINAL
    st.divider()
    st.subheader("🏁 Soluție și Reprezentare Grafică")
    
    sol_col, sol_graf = st.columns(2)
    v_f = 0
    with sol_col:
        for r, c in boxed:
            val = int(mat_orig[r, c])
            v_f += val
            st.write(f"Afectare: **x{r+1}** $\\rightarrow$ **y{c+1}** (Cost: {val})")
        st.markdown(f"### Valoare Finală: {v_f}")
    
    with sol_graf:
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR')
        for i in range(n): dot.node(f'X{i}', f'x{i+1}', color='#e65c00')
        for j in range(n): dot.node(f'Y{j}', f'y{j+1}', color='#2e7d32')
        for r, c in boxed:
            dot.edge(f'X{r}', f'Y{c}', label=str(int(mat_orig[r, c])))
        st.graphviz_chart(dot)

    # VERIFICARE ANALITICĂ (FORMULA DIN CURS)
    st.info("**Verificare analitică conform curs:**")
    val_r_c = np.sum(r_mins) + np.sum(c_mins)
    val_eps = sum([e * (n - m) for e, m in istoric_eps])
    
    if tip_p == "Minimizare (Vmin)":
        st.latex(r"V_{min} = \sum MIN(L) + \sum MIN(C) + \sum \epsilon_k(n - m_k)")
        st.write(f"Calcul: {int(val_r_c)} (minime) + {int(val_eps)} (epsilons) = {int(val_r_c + val_eps)}")
    else:
        st.write("Pentru Maximizare, verificarea se face prin însumarea valorilor din matricea originală corespunzătoare cuplajului.")
