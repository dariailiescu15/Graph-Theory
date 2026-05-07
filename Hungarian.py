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
    
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 18px; border: 2px solid #333; }
    .matrix-table td { border: 1px solid #333; width: 55px; height: 55px; text-align: center; vertical-align: middle; }
    
    /* Culori Seminar: Portocaliu pentru tăieturi */
    .t1 { background-color: #ffffff; } /* Zona albă - Neacoperită */
    .t2 { background-color: #ffb366; } /* Portocaliu - Tăietură (T2) */
    .t3 { background-color: #e67300; } /* Portocaliu închis - Intersecție (T3) */
    
    .boxed-zero { border: 2px solid black; padding: 3px; font-weight: bold; display: inline-block; width: 25px; background: white; }
    .crossed-zero { text-decoration: line-through; color: #777; font-weight: bold; }
    .star-sym { color: red; font-weight: bold; font-size: 20px; margin-left: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Probleme de afectare: Algoritmul Ungar (AU)</p>
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
# 2. LOGICA MANUALĂ A ALGORITMULUI (REPARAȚII)
# ==============================================================================

def incadrare_zerouri_manual(mat):
    """Regula: linia cu cele mai puține zerouri -> încadrează primul -> barează restul."""
    n = mat.shape[0]
    boxed = []
    crossed = []
    r_used = [False] * n
    c_used = [False] * n

    # Facem o copie să nu stricăm matricea originală
    m_temp = mat.copy()

    while True:
        counts = []
        for i in range(n):
            if not r_used[i]:
                # Numărăm zerourile disponibile pe coloane neocupate
                zeros = [j for j in range(n) if m_temp[i, j] == 0 and not c_used[j]]
                if zeros:
                    counts.append((len(zeros), i, zeros))
        
        if not counts: break
        
        # Alegem linia cu cele mai puține zerouri (conform seminar)
        counts.sort()
        _, r_idx, available_cols = counts[0]
        c_idx = available_cols[0]

        boxed.append((r_idx, c_idx))
        r_used[r_idx] = True
        c_used[c_idx] = True

        # Barăm restul pe linie și coloană
        for j in range(n):
            if m_temp[r_idx, j] == 0 and j != c_idx:
                crossed.append((r_idx, j))
            if m_temp[j, c_idx] == 0 and j != r_idx:
                crossed.append((j, c_idx))
                
    return boxed, list(set(crossed))

def marcaj_si_taieturi(mat, boxed, crossed):
    """Procedura de marcaj lateral conform Seminar."""
    n = mat.shape[0]
    bx_rows = {r for r, c in boxed}
    
    # 1. Marcăm liniile care NU au zero încadrat (pătrat)
    m_rows = set(range(n)) - bx_rows
    m_cols = set()
    
    changed = True
    while changed:
        before = len(m_rows) + len(m_cols)
        # 2. Marcăm coloanele cu 0 barat în linii marcate
        for r, c in crossed:
            if r in m_rows: m_cols.add(c)
        # 3. Marcăm liniile cu 0 încadrat în coloane marcate
        for r, c in boxed:
            if c in m_cols: m_rows.add(r)
        changed = (len(m_rows) + len(m_cols)) != before

    # Tăieturi: Linii NEMARCATE + Coloane MARCATE (Zonele Portocalii)
    cov_rows = [i for i in range(n) if i not in m_rows]
    cov_cols = list(m_cols)
    return cov_rows, cov_cols, m_rows, m_cols

def draw_table_html(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols):
    n = mat.shape[0]
    bx = set(boxed)
    cr = set(crossed)
    
    html = '<table class="matrix-table"><tr><td></td>'
    for j in range(n):
        star = '<span class="star-sym">*</span>' if j in m_cols else ''
        html += f'<td>y{j+1}{star}</td>'
    html += '</tr>'
    
    for i in range(n):
        star = '<span class="star-sym">*</span>' if i in m_rows else ''
        html += f'<tr><td>x{i+1}{star}</td>'
        for j in range(n):
            # Logica de culori portocaliu
            cls = "t1"
            if i in r_cov and j in c_cov: cls = "t3" # Intersecție
            elif i in r_cov or j in c_cov: cls = "t2" # Tăietură
            
            val = int(mat[i, j])
            content = str(val)
            if (i, j) in bx: content = '<span class="boxed-zero">0</span>'
            elif (i, j) in cr: content = '<span class="crossed-zero">0</span>'
            
            html += f'<td class="{cls}">{content}</td>'
        html += '</tr>'
    return html + "</table>"

# ==============================================================================
# 3. DATE SEMINAR ȘI INTERFAȚĂ
# ==============================================================================

# Datele de la pagina 4 (problema principală)
seminar_data = [
    [99, 21, 53, 46, 18, 80],
    [34, 20, 79, 65, 11, 14],
    [76, 10, 73, 56, 47, 42],
    [79, 39, 76, 80, 81, 24],
    [37, 95, 89, 83, 73, 19],
    [74, 54, 91, 34, 20, 85]
]

st.subheader("Seminar: Problema de afectare (Pagina 4-8)")
input_df = st.data_editor(pd.DataFrame(seminar_data), use_container_width=True)

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    tip_problem = st.radio("Tip problemă:", ["Minimizare (Vmin)", "Maximizare (Vmax)"])
with col_cfg2:
    st.info("**Scurt Ghid:**\n- I0: Starea după reduceri.\n- Portocaliu: Tăieturile conform marcajului.\n- Boxed: Zerouri independente (Soluția).")

# ==============================================================================
# 4. EXECUȚIA PAS CU PAS
# ==============================================================================

if st.button("Execută Algoritmul Ungar", type="primary", use_container_width=True):
    mat_orig = input_df.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]
    
    st.markdown("### PAS 1: Matricea costurilor și reducerea")
    
    # Maximizare (C* = Max - C)
    if tip_problem == "Maximizare (Vmax)":
        mat = np.max(mat) - mat
        st.write("Problema de maximizare: reducerea prin scădere din valoarea maximă.")

    # Reducerile (Seminar)
    min_l = mat.min(axis=1, keepdims=True)
    mat -= min_l
    min_c = mat.min(axis=0, keepdims=True)
    mat -= min_c
    
    st.write(f"Suma minime linii: **{int(np.sum(min_l))}** | Suma minime coloane: **{int(np.sum(min_c))}**")

    # Iterațiile (Start I0)
    iter_idx = 0
    history_eps = []

    while iter_idx < 10:
        bx, cr = incadrare_zerouri_manual(mat)
        r_cov, c_cov, m_rows, m_cols = marcaj_si_taieturi(mat, bx, cr)
        
        st.divider()
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        
        # Verificăm dacă m = n
        if len(bx) == n:
            # Tabelul final nu mai are nevoie de tăieturi portocalii (m=n)
            st.markdown(draw_table_html(mat, [], [], bx, cr, set(), set()), unsafe_allow_html=True)
            st.success(f"STOP! S-au găsit {n} zerouri încadrate. Algoritmul se oprește.")
            break
        else:
            # Afișăm tabelul cu tăieturile portocalii
            st.markdown(draw_table_html(mat, r_cov, c_cov, bx, cr, m_rows, m_cols), unsafe_allow_html=True)
            st.warning(f"Test optimalitate: {len(bx)} < {n} $\implies$ Se calculează $\epsilon$ și se trece la $I_{iter_idx+1}$")

        # Calcul Epsilon (min neacoperit)
        uncovered = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
        epsilon = min(uncovered)
        history_eps.append((epsilon, len(r_cov) + len(c_cov)))
        st.latex(r"\epsilon_{" + str(iter_idx) + r"} = " + str(int(epsilon)))

        # Aplicare Epsilon
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= epsilon
                if r in r_cov and c in c_cov: mat[r, c] += epsilon
        
        iter_idx += 1

    # Rezultat Final
    st.divider()
    st.subheader("🏁 Soluția și Validarea")
    
    v_final = 0
    for r, c in bx:
        cost = int(mat_orig[r, c])
        v_final += cost
        st.write(f"- Repartizare: **x{r+1}** la **y{c+1}** (Cost: {cost})")
    
    st.markdown(f"## Valoare Finală: {v_f if tip_problem == 'Maximizare' else v_final}")

    # Formula de verificare analitică
    st.info("**Verificarea analitică a costului:**")
    val_minime = np.sum(min_l) + np.sum(min_c)
    val_sigmas = sum([e * (n - m) for e, m in history_eps])
    
    if tip_problem == "Minimizare (Vmin)":
        st.latex(r"V_{min} = \sum MIN(L) + \sum MIN(C) + \sum \epsilon_k(n - m_k)")
        st.write(f"Calcul: {int(val_minime)} + {int(val_sigmas)} = **{int(val_minime + val_sigmas)}**")
