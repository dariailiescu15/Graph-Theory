import streamlit as st
import pandas as pd
import numpy as np
import graphviz

# ==============================================================================
# 1. IDENTITATE VIZUALĂ ȘI STILURI ACADEMICE
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
    
    /* Tabel Matrice */
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 18px; border: 2px solid #333; }
    .matrix-table td { border: 1px solid #333; width: 60px; height: 60px; text-align: center; vertical-align: middle; }
    
    /* Clase corespunzătoare zonelor de tăiere din Pasul 5 (Curs) */
    .t1 { background-color: #ffffff; }        /* T1: Elemente netăiate */
    .t2 { background-color: #ffcc99; }        /* T2: Elemente tăiate o singură dată */
    .t3 { background-color: #e67300; color: white; font-weight: bold; } /* T3: Elemente dublu tăiate (intersecții) */
    
    .min-cell { background-color: #e3f2fd; color: #0d47a1; font-weight: bold; border: 2px solid #1565c0 !important; }
    
    /* Reprezentarea zerourilor (Încadrat vs. Barat) conform Pasului 3 */
    .boxed-zero { border: 2px solid black; padding: 4px; font-weight: bold; display: inline-block; background: white; color: black; line-height: 1; }
    .crossed-zero { text-decoration: line-through; color: #777; font-weight: bold; }
    .star-sym { color: red; font-weight: bold; font-size: 24px; margin-left: 5px; }
    
    .academic-note { background-color: #f8f9fa; border-left: 5px solid #0056b3; padding: 15px; margin: 10px 0; border-radius: 4px; font-family: 'Segoe UI', sans-serif;}
    
    /* Stiluri specifice pentru matricea decizionala */
    .dec-1 { background-color: #d4edda; color: #155724; font-weight: bold; font-size: 22px; }
    .dec-0 { background-color: #f8f9fa; color: #ced4da; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# Antet
st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Algoritmul UNGAR (AU) - Cuplajul Bipartit și Problema de Afectare</p>
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
# 2. LOGICA MATEMATICĂ ȘI PROCEDURILE ALGORITMULUI (CONFORM CURSULUI)
# ==============================================================================

def repartizare_manuala_zerouri(mat):
    n = mat.shape[0]
    boxed, crossed = [], []
    r_done, c_done =[False] * n, [False] * n
    m_temp = mat.copy()
    
    while True:
        candidates = []
        for i in range(n):
            if not r_done[i]:
                zeros = [j for j in range(n) if m_temp[i, j] == 0 and not c_done[j]]
                if zeros: candidates.append((len(zeros), i, zeros))
                
        if not candidates: break 
        
        candidates.sort() 
        _, r_idx, z_cols = candidates[0]
        c_idx = z_cols[0] 
        
        boxed.append((r_idx, c_idx))
        r_done[r_idx] = True
        c_done[c_idx] = True
        
        for j in range(n):
            if m_temp[r_idx, j] == 0 and j != c_idx: crossed.append((r_idx, j))
        for i in range(n):
            if m_temp[i, c_idx] == 0 and i != r_idx: crossed.append((i, c_idx))
            
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
        html += f'<td><b>y{j+1}</b>{star}</td>'
    if row_mins is not None: html += '<td class="min-cell">u<sub>i</sub> (L)</td>'
    html += '</tr>'
    
    for i in range(n):
        star = '<span class="star-sym">*</span>' if i in m_rows else ''
        html += f'<tr><td><b>x{i+1}</b>{star}</td>'
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
        html += '<tr><td class="min-cell">v<sub>j</sub> (C)</td>'
        for v in col_mins: html += f'<td class="min-cell">{int(v) if v > 0 else "-"}</td>'
        html += '<td></td></tr>'
        
    return html + "</table>"

def draw_decision_matrix(n, boxed):
    """
    Generează Matricea de Afectare (Variabilele de decizie x_ij),
    unde elementele sunt 1 (asociere realizată) și 0 în rest.
    """
    bx_set = set(boxed)
    html = '<table class="matrix-table" style="margin: 0;"><tr><td></td>'
    for j in range(n):
        html += f'<td><b>y{j+1}</b></td>'
    html += '</tr>'
    
    for i in range(n):
        html += f'<tr><td><b>x{i+1}</b></td>'
        for j in range(n):
            if (i, j) in bx_set:
                html += '<td class="dec-1">1</td>'
            else:
                html += '<td class="dec-0">0</td>'
        html += '</tr>'
        
    return html + "</table>"

# ==============================================================================
# 3. INTERFAȚĂ UTILIZATOR ȘI EXECUTARE ALGORITM
# ==============================================================================

seminar_data =[[99, 21, 53, 46, 18, 80],[34, 20, 79, 65, 11, 14],[76, 10, 73, 56, 47, 42],[79, 39, 76, 80, 81, 24],[37, 95, 89, 83, 73, 19],[74, 54, 91, 34, 20, 85]
]

st.subheader("I. Datele problemei (Matricea Costurilor)")
df_in = st.data_editor(pd.DataFrame(seminar_data, 
                                    columns=[f"y{i+1}" for i in range(6)], 
                                    index=[f"x{i+1}" for i in range(6)]), 
                       use_container_width=True)

col_obj, _ = st.columns([1, 2])
with col_obj:
    tip_opt = st.selectbox("Obiectivul algoritmului:",["Minimizare a timpului total", "Maximizare a asocierilor"])

if st.button("Execută Algoritmul Ungar", type="primary", use_container_width=True):
    mat_orig = df_in.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]

    st.markdown("### PAS 1 și 2: Matricea Costurilor și Crearea Zerourilor")
    
    if tip_opt == "Maximizare a asocierilor":
        val_max = np.max(mat)
        st.write(f"Conform observațiilor teoretice, pentru **maximizare** determinăm $\lambda = \max(c_{{ij}}) = {int(val_max)}$ și lucrăm cu matricea modificată $C^* = \lambda - C$.")
        mat = val_max - mat

    st.write("**Reducerea liniilor:** Se scade $u_i$ (minimul fiecărei linii) din elementele liniei respective.")
    r_mins = mat.min(axis=1)
    for i in range(n): mat[i, :] -= r_mins[i]
    
    st.write("**Reducerea coloanelor:** Se scade $v_j$ (minimul pe coloane, din matricea rezultată) pentru a garanta cel puțin un 0 pe fiecare rând și coloană.")
    c_mins = np.zeros(n)
    for j in range(n):
        if not np.any(mat[:, j] == 0): c_mins[j] = mat[:, j].min()
    
    st.markdown(draw_html_matrix(mat, [], [], [],[], set(), set(), row_mins=r_mins, col_mins=c_mins), unsafe_allow_html=True)
    for j in range(n): mat[:, j] -= c_mins[j]

    st.markdown("### Procesul Iterativ (Afectare, Taieturi, Deplasare)")
    
    st.markdown("""
    <div class="academic-note">
    <strong>Legendă Cromatică și Notații Formale:</strong><br>
    <span style="display:inline-block; width:15px; height:15px; background-color:#ffffff; border:1px solid #333;"></span> <strong>Grupa T1</strong>: Elemente netăiate.<br>
    <span style="display:inline-block; width:15px; height:15px; background-color:#ffcc99; border:1px solid #333;"></span> <strong>Grupa T2</strong>: Elemente tăiate o singură dată (Suport minim S).<br>
    <span style="display:inline-block; width:15px; height:15px; background-color:#e67300; border:1px solid #333;"></span> <strong>Grupa T3</strong>: Elemente dublu tăiate (Intersecții).<br>
    <strong>(*)</strong> Marcajele laterale utilizate pentru determinarea suportului minim.
    </div>
    """, unsafe_allow_html=True)

    iter_idx = 1
    history_eps =[]
    final_bx =[]

    while iter_idx < 10:
        bx, cr = repartizare_manuala_zerouri(mat)
        m = len(bx)
        r_cov, c_cov, m_rows, m_cols = procedura_marcaj_lateral(mat, bx, cr)
        
        st.divider()
        st.markdown(f"#### Iterația {iter_idx}")
        
        col_txt, col_tbl = st.columns([1, 1.8])
        
        with col_txt:
            st.write(f"**PAS 3: Determinarea cuplajului maxim curent**")
            st.write(f"• Număr zerouri încadrate (cardinal cuplaj): **m = {m}**")
            
            if m == n:
                st.success(f"**STOP ALGORITM!** Deoarece $m = n = {n}$, cuplajul găsit este maximal și reprezintă soluția optimă a problemei.")
                final_bx = bx
                with col_tbl:
                    st.markdown(draw_html_matrix(mat, [],[], bx, cr, set(), set()), unsafe_allow_html=True)
                break
            else:
                st.warning(f"Deoarece $m ({m}) < n ({n})$, cuplajul nu este complet. Se aplică pașii de tăiere.")
                
                st.write("**PAS 4: Determinare suport minim S**")
                st.write("S-au marcat liniile/coloanele cu (*) pentru a trasa tăieturile (zonele portocalii).")
                
                uncovered = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
                eps = min(uncovered)
                history_eps.append((eps, m))
                
                st.write(f"**PAS 5: Deplasarea zerourilor**")
                st.latex(r"\epsilon = \min(x \in T_1) = " + str(int(eps)))
                st.write(f"• Se scade $\epsilon = {int(eps)}$ din elementele neacoperite ($T_1$).")
                st.write(f"• Se adună $\epsilon = {int(eps)}$ la elementele de la intersecții ($T_3$).")
                
        with col_tbl:
            st.markdown(draw_html_matrix(mat, r_cov, c_cov, bx, cr, m_rows, m_cols), unsafe_allow_html=True)

        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: 
                    mat[r, c] -= eps   
                elif r in r_cov and c in c_cov: 
                    mat[r, c] += eps   
        
        iter_idx += 1

    # ==============================================================================
    # 4. REZULTATE FINALE: MATRICEA DE AFECTARE ȘI GRAFUL BIPARTIT
    # ==============================================================================
    st.divider()
    st.markdown("### REZULTAT FINAL: Modelarea Soluției Optime")
    
    col_rez, col_grf = st.columns([1, 1])
    
    with col_rez:
        # Reprezentarea formală a cuplajului
        w_max_elements = [f"(x_{r+1}, y_{c+1})" for r, c in final_bx]
        st.latex(r"W_{max} = \{ " + ", ".join(w_max_elements) + r" \}")
        
        v_total = sum(mat_orig[r, c] for r, c in final_bx)
        st.success(f"**Valoare Funcție Obiectiv:** $V(W_{{max}}) = {int(v_total)}$")
        
        # Verificare
        if tip_opt == "Minimizare a timpului total":
            sum_ui = np.sum(r_mins)
            sum_vj = np.sum(c_mins)
            sum_eps = sum(e * (n - m_val) for e, m_val in history_eps)
            st.latex(r"V_{min} = \sum u_i + \sum v_j + \sum \epsilon_k(n - n_k^{\Box})")
            st.write(f"Verificare: {int(sum_ui)} + {int(sum_vj)} + {int(sum_eps)} = **{int(sum_ui + sum_vj + sum_eps)}**")

        st.markdown("<br><b>Matricea Variabilelor de Decizie ($x_{ij} \in \{0, 1\}$)</b>", unsafe_allow_html=True)
        st.markdown(draw_decision_matrix(n, final_bx), unsafe_allow_html=True)

    with col_grf:
        st.markdown("<b>Reprezentarea Geometrică a Grafului Bipartit Asociat</b>", unsafe_allow_html=True)
        
        # Generarea Grafului Bipartit Ordonat (2 coloane top-down paralele)
        dot = graphviz.Digraph(engine='dot')
        dot.attr(rankdir='LR', ranksep='2.5', nodesep='0.4')
        dot.attr('node', shape='circle', style='filled', fontcolor='white', fontname='Helvetica-bold', width='0.6')
        
        # Cluster/Subgraph pentru nodurile X (garantează alinierea pe o singură coloană)
        with dot.subgraph() as s_x:
            s_x.attr(rank='same')
            for i in range(n):
                s_x.node(f'X{i}', f'x{i+1}', color='#e65c00', fillcolor='#e65c00')
                
        # Cluster/Subgraph pentru nodurile Y (garantează alinierea pe a doua coloană)
        with dot.subgraph() as s_y:
            s_y.attr(rank='same')
            for j in range(n):
                s_y.node(f'Y{j}', f'y{j+1}', color='#2e7d32', fillcolor='#2e7d32')
                
        # Muchii invizibile (cu pondere mare) pentru a forța ordinea top-down (x1 -> x2 -> x3...)
        for i in range(n - 1):
            dot.edge(f'X{i}', f'X{i+1}', style='invis', weight='100')
            dot.edge(f'Y{i}', f'Y{i+1}', style='invis', weight='100')
            
        # Muchiile soluției optime (Săgețile reale de la X la Y)
        for r, c in final_bx:
            dot.edge(f'X{r}', f'Y{c}', label=str(int(mat_orig[r, c])), 
                     color='#333333', fontcolor='#333333', penwidth='2.0', arrowhead='normal', arrowsize='0.8')
            
        st.graphviz_chart(dot)
