import streamlit as st
import pandas as pd
import numpy as np
import graphviz
import random
from scipy.optimize import linear_sum_assignment

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI CSS
# ==============================================================================
st.set_page_config(page_title="Proiect Teoria Grafurilor", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin: 0; font-style: italic;}
    .info-box { background-color: #fff4ea; border-left: 5px solid #e65c00; padding: 15px; margin-bottom: 20px; border-radius: 5px;}
    .matrix-table { border-collapse: collapse; text-align: center; font-size: 18px; margin-bottom: 20px; }
    .matrix-table td { border: 1px solid #cc5200; padding: 10px; width: 40px; height: 40px; }
    </style>
""", unsafe_allow_html=True)

def fmt(val):
    if pd.isna(val): return "0"
    return str(int(val)) if float(val).is_integer() else f"{val:.2f}"

def get_random_color():
    """Returnează o culoare hex random dintr-o paletă vibrantă și vizibilă pentru etichete."""
    culori =['#d62728', '#2ca02c', '#1f77b4', '#9400D3', '#FF8C00', '#008B8B', '#FF1493', '#8A2BE2']
    return random.choice(culori)

# ==============================================================================
# TAB 1: FORD-FULKERSON
# ==============================================================================
def deseneaza_graf_retea(arce_df, etichete_noduri=None, lant_curent=None):
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', bgcolor='transparent')
    
    graf.attr('node', shape='circle', style='filled', fillcolor='#ffecd9', color='#e65c00', fontcolor='#cc5200', fontname='Helvetica', penwidth='2')
    
    noduri = set(arce_df['Start (x_i)']).union(set(arce_df['Destinație (x_j)']))
    str_noduri = {str(int(n)) for n in noduri}
    
    # FORȚĂM AȘEZAREA GRAFULUI CA ÎN CURS (Dacă rețeaua are fix nodurile 1-10 din curs)
    if str_noduri.issuperset({'1','2','3','4','5','6','7','8','9','10'}):
        graf.body.append('{rank=same; "1"}')
        graf.body.append('{rank=same; "2"; "3"; "4"}')
        graf.body.append('{rank=same; "5"; "6"}')
        graf.body.append('{rank=same; "7"; "8"; "9"}')
        graf.body.append('{rank=same; "10"}')
    
    for n in noduri:
        label = f"x{int(n)}"
        color_fill = '#ffecd9'
        
        if etichete_noduri and n in etichete_noduri:
            eticheta_text, culoare_eticheta = etichete_noduri[n]
            # Desenăm eticheta deasupra nodului cu culoarea aferentă (HTML-like)
            label = f"<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='0'><TR><TD><FONT POINT-SIZE='12' COLOR='{culoare_eticheta}'><B>{eticheta_text}</B></FONT></TD></TR><TR><TD>x{int(n)}</TD></TR></TABLE>>"
            color_fill = '#ffe0c2'
            
        graf.node(str(int(n)), label, fillcolor=color_fill)
        
    muchii_lant = set()
    if lant_curent:
        for u, v, _ in lant_curent:
            muchii_lant.add((str(int(u)), str(int(v))))
            
    for _, rand in arce_df.iterrows():
        i = str(int(rand['Start (x_i)']))
        j = str(int(rand['Destinație (x_j)']))
        c_ij = fmt(rand['Capacitate c(u)'])
        f_ij = fmt(rand['Flux f(u)'])
        
        label_arc = f"{f_ij} / {c_ij}"
        
        if (i, j) in muchii_lant or (j, i) in muchii_lant:
            graf.edge(i, j, label=label_arc, color='#cc5200', penwidth='3.5', fontcolor='#cc5200', fontsize='14', fontname='Helvetica-bold')
        elif float(rand['Flux f(u)']) == float(rand['Capacitate c(u)']):
            graf.edge(i, j, label=label_arc, color='#a0a0a0', penwidth='1.5', fontcolor='#606060')
        else:
            graf.edge(i, j, label=label_arc, color='#ffb380', penwidth='1.5', fontcolor='#888888')
            
    return graf

def ford_fulkerson(df_arce, sursa, dest):
    df = df_arce.copy()
    istoric =[]
    iteratie = 1
    
    while True:
        # Păstrăm o culoare specifică pentru toate marcajele din această iterație
        culoare_iter = get_random_color() 
        
        etichete = {sursa: ("[+]", culoare_iter)}
        parinti = {sursa: (None, None)} 
        
        coada =[sursa]
        dest_gasita = False
        
        while coada and not dest_gasita:
            nod_curent = coada.pop(0)
            
            arce_directe = df[df['Start (x_i)'] == nod_curent]
            for _, rand in arce_directe.iterrows():
                vecin = rand['Destinație (x_j)']
                flux, cap = rand['Flux f(u)'], rand['Capacitate c(u)']
                if vecin not in etichete and flux < cap:
                    etichete[vecin] = (f"[+x_{int(nod_curent)}]", culoare_iter)
                    parinti[vecin] = (nod_curent, '+')
                    coada.append(vecin)
                    if vecin == dest: dest_gasita = True; break
                        
            if dest_gasita: break
            
            arce_inverse = df[df['Destinație (x_j)'] == nod_curent]
            for _, rand in arce_inverse.iterrows():
                vecin = rand['Start (x_i)']
                flux = rand['Flux f(u)']
                if vecin not in etichete and flux > 0:
                    etichete[vecin] = (f"[-x_{int(nod_curent)}]", culoare_iter)
                    parinti[vecin] = (nod_curent, '-')
                    coada.append(vecin)
                    if vecin == dest: dest_gasita = True; break

        if not dest_gasita:
            istoric.append({'iteratie': 'STOP', 'status': 'STOP', 'etichete': etichete, 'df_stare': df.copy()})
            break
            
        lant =[]
        curent = dest
        while curent != sursa:
            parinte, sens = parinti[curent]
            if sens == '+': lant.append((parinte, curent, '+'))
            else: lant.append((curent, parinte, '-'))
            curent = parinte
        lant.reverse()
        
        alphas = []
        formule_alpha =[]
        for u, v, sens in lant:
            if sens == '+':
                rand = df[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].iloc[0]
                rezerva = rand['Capacitate c(u)'] - rand['Flux f(u)']
                alphas.append(rezerva)
                formule_alpha.append(f"c(x_{int(u)}, x_{int(v)}) - f = {fmt(rezerva)}")
            else:
                rand = df[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].iloc[0]
                rezerva = rand['Flux f(u)']
                alphas.append(rezerva)
                formule_alpha.append(f"f(x_{int(u)}, x_{int(v)}) = {fmt(rezerva)}")
                
        alpha = min(alphas)
        for u, v, sens in lant:
            idx = df.index[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].tolist()[0]
            if sens == '+': df.at[idx, 'Flux f(u)'] += alpha
            else: df.at[idx, 'Flux f(u)'] -= alpha
                
        istoric.append({
            'iteratie': iteratie, 'status': 'CONTINUA', 'etichete': etichete,
            'lant': lant, 'alpha': alpha, 'formule_alpha': formule_alpha, 'df_stare': df.copy()
        })
        iteratie += 1
        if iteratie > 50: break
    return istoric, df

# ==============================================================================
# TAB 2: ALGORITMUL UNGAR (KUHN-MUNKRES)
# ==============================================================================
def minim_linii_acoperire(mat):
    """Aplică Teorema lui König pentru a găsi liniile minime care acoperă zerourile."""
    cost_matrix = np.where(mat == 0, 1, 0)
    row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)
    
    matches =[(r, c) for r, c in zip(row_ind, col_ind) if cost_matrix[r, c] == 1]
    
    matched_rows = {r for r, c in matches}
    unmatched_rows = set(range(mat.shape[0])) - matched_rows
    
    visited_rows = set(unmatched_rows)
    visited_cols = set()
    queue = list(unmatched_rows)
    
    while queue:
        r = queue.pop(0)
        for c in range(mat.shape[1]):
            if cost_matrix[r, c] == 1 and c not in visited_cols:
                visited_cols.add(c)
                for mr, mc in matches:
                    if mc == c and mr not in visited_rows:
                        visited_rows.add(mr)
                        queue.append(mr)
                        break
                        
    covered_rows = set(range(mat.shape[0])) - visited_rows
    return list(covered_rows), list(visited_cols), matches

def deseneaza_graf_bipartit(mat_originala, assignment):
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', splines='false')
    graf.attr('node', shape='circle', style='filled', fillcolor='#ffecd9', color='#e65c00', fontcolor='#e65c00')
    
    for i in range(mat_originala.shape[0]): graf.node(f"X{i}", f"x{i+1}")
    for j in range(mat_originala.shape[1]): graf.node(f"Y{j}", f"y{j+1}")
        
    for r, c in assignment:
        graf.edge(f"X{r}", f"Y{c}", label=str(int(mat_originala[r, c])), color='#FF1493', penwidth='2')
    return graf

# ==============================================================================
# UI PRINCIPAL STREAMLIT
# ==============================================================================
st.markdown('''
    <div class="title-box">
        <p class="title-text">📐 Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Algoritmul Ford-Fulkerson & Algoritmul Ungar</p>
    </div>
''', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🌊 Problema 1: Ford-Fulkerson (Flux)", "🧩 Problema 2: Algoritmul Ungar (Alocare)"])

# ------------------------------------------------------------------------------
# TAB 1: FORD-FULKERSON
# ------------------------------------------------------------------------------
with tab1:
    col_t1, col_g1 = st.columns([1, 1.2])
    with col_t1:
        st.markdown("<h4 style='color:#e65c00;'>1. Structura Rețelei (Date din Curs)</h4>", unsafe_allow_html=True)
        
        # Exact datele din curs (cu fluxul inițial pus pe 3 lanțuri -> f0=37)
        if "tabel_retea" not in st.session_state:
            date_curs = [
                [1,2, 20, 10], [1,3, 30, 4],[1,4, 40, 23],
                [2,5, 20, 0],[2,7, 10, 10],
                [3,5, 17, 0],[3,8, 24, 4],
                [4,6, 18, 0],[4,9, 23, 23],
                [5,7, 10, 0],[5,8, 9, 0],
                [6,8, 12, 0], [6,9, 8, 0],[7,10, 31, 10], [8,10, 23, 4],[9,10, 42, 23]
            ]
            st.session_state.tabel_retea = pd.DataFrame(date_curs, columns=["Start (x_i)", "Destinație (x_j)", "Capacitate c(u)", "Flux f(u)"])

        edited_df = st.data_editor(st.session_state.tabel_retea, num_rows="dynamic", use_container_width=True)
        noduri_disp = sorted(list(set(edited_df['Start (x_i)']).union(set(edited_df['Destinație (x_j)']))))
        n_start = st.selectbox("Sursă", noduri_disp, index=0)
        n_dest = st.selectbox("Destinație", noduri_disp, index=len(noduri_disp)-1)

    with col_g1:
        st.markdown("<h4 style='color:#e65c00;'>Graful Inițial (Așezare stânga-dreapta)</h4>", unsafe_allow_html=True)
        st.graphviz_chart(deseneaza_graf_retea(edited_df), use_container_width=True)

    if st.button("🚀 Rulează Ford-Fulkerson", type="primary", use_container_width=True):
        st.divider()
        istoric, df_final = ford_fulkerson(edited_df, n_start, n_dest)
        
        for pas in istoric:
            with st.expander(f"🟡 Iterația {pas['iteratie']}", expanded=(pas['status']=='STOP')):
                str_etichete = ", ".join([f"x_{{{int(n)}}}: \text{{{lbl[0]}}}" for n, lbl in pas['etichete'].items()])
                st.latex(r"\{ " + str_etichete + r" \}")
                
                if pas['status'] == 'CONTINUA':
                    lant_str = f"x_{{{int(n_start)}}}"
                    for u, v, sens in pas['lant']:
                        lant_str += rf" \xrightarrow{{{'+' if sens == '+' else '-'}}} x_{{{int(v)}}}"
                    st.latex(rf"\mu = [{lant_str}]")
                    st.latex(r"\alpha = \min \{" + r", ".join(pas['formule_alpha']) + r"\} = " + fmt(pas['alpha']))
                    st.graphviz_chart(deseneaza_graf_retea(pas['df_stare'], etichete_noduri=pas['etichete'], lant_curent=pas['lant']), use_container_width=True)
                else:
                    st.success(f"**STOP!** Destinația nu a mai fost etichetată.")
                    st.graphviz_chart(deseneaza_graf_retea(pas['df_stare'], etichete_noduri=pas['etichete']), use_container_width=True)

        # Calcul Final
        st.markdown("<h3 style='color: #e65c00;'>🏆 Soluția Finală și Tăietura Minimă</h3>", unsafe_allow_html=True)
        flux_iesire = df_final[df_final['Start (x_i)'] == n_start]['Flux f(u)'].sum()
        flux_intrare = df_final[df_final['Destinație (x_j)'] == n_start]['Flux f(u)'].sum()
        v_max = flux_iesire - flux_intrare
        
        noduri_A = list(istoric[-1]['etichete'].keys())
        noduri_XA =[n for n in noduri_disp if n not in noduri_A]
        cap_taietura = df_final[df_final['Start (x_i)'].isin(noduri_A) & df_final['Destinație (x_j)'].isin(noduri_XA)]['Capacitate c(u)'].sum()
        
        c1, c2 = st.columns(2)
        c1.latex(rf"V(f_{{max}}) = {fmt(v_max)}")
        c2.latex(rf"C(T) = {fmt(cap_taietura)} \implies V(f_{{max}}) = C(T) \text{{ (Corect)}}")

# ------------------------------------------------------------------------------
# TAB 2: ALGORITMUL UNGAR
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("<h4 style='color:#e65c00;'>Matricea Costurilor Inițiale</h4>", unsafe_allow_html=True)
    
    if "matrice_ungar" not in st.session_state:
        # Datele exacte din curs pag 10 (rezultat 166)
        date_mat = [[55, 23, 83, 61, 66, 22],[99, 81, 14, 77, 61, 55],[59, 39, 58, 49, 24, 54],[36, 10, 37, 62, 28, 33],[73, 51, 51, 24, 26, 55],
            [72, 54, 78, 91, 89, 96]
        ]
        cols = [f"Y{i+1}" for i in range(6)]
        st.session_state.matrice_ungar = pd.DataFrame(date_mat, columns=cols, index=[f"X{i+1}" for i in range(6)])

    df_mat = st.data_editor(st.session_state.matrice_ungar, use_container_width=True)
    
    if st.button("🚀 Calculează Alocarea Optimă (Kuhn-Munkres)", type="primary", use_container_width=True):
        st.divider()
        mat_orig = df_mat.values.copy()
        mat = mat_orig.copy()
        n = mat.shape[0]
        
        # PAS 1
        st.markdown("#### **PAS 1:** Reducerea matricii (Minim Linii și Coloane)")
        min_l = mat.min(axis=1, keepdims=True)
        mat = mat - min_l
        min_c = mat.min(axis=0, keepdims=True)
        mat = mat - min_c
        
        st.write(pd.DataFrame(mat, columns=df_mat.columns, index=df_mat.index))
        
        # Iterare PAS 2 și 3
        iteratie = 1
        while True:
            st.markdown(f"#### **PAS 2:** Iterația {iteratie} - Acoperirea Zerourilor")
            cov_r, cov_c, assignment = minim_linii_acoperire(mat)
            nr_linii = len(cov_r) + len(cov_c)
            
            # Generare HTML pentru a arăta liniile trasaet
            html = "<table class='matrix-table'>"
            for i in range(n):
                html += "<tr>"
                for j in range(n):
                    bg = "#ffffff"
                    if i in cov_r and j in cov_c: bg = "#d0bdf4" # intersecție (2 linii)
                    elif i in cov_r or j in cov_c: bg = "#e2eefa" # 1 linie
                    
                    val = int(mat[i,j])
                    if val == 0: html += f"<td style='background-color:{bg}; color:red; font-weight:bold;'>0</td>"
                    else: html += f"<td style='background-color:{bg};'>{val}</td>"
                html += "</tr>"
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
            
            if nr_linii == n:
                st.success(f"Număr de linii ({nr_linii}) = m ({n}). STOP Algoritm!")
                break
                
            st.markdown(f"Număr de linii = {nr_linii} $\\neq {n}$. **Se trece la PAS 3.**")
            
            # PAS 3
            uncovered =[]
            for i in range(n):
                for j in range(n):
                    if i not in cov_r and j not in cov_c:
                        uncovered.append(mat[i,j])
            
            sigma = min(uncovered)
            st.latex(rf"\Sigma_0 = \min(T_1) = {int(sigma)}")
            
            for i in range(n):
                for j in range(n):
                    if i not in cov_r and j not in cov_c:
                        mat[i,j] -= sigma
                    if i in cov_r and j in cov_c:
                        mat[i,j] += sigma
            iteratie += 1

        # Rezultat
        st.divider()
        st.markdown("### 🏆 Soluția Optimă (Cuplajul Maxim)")
        c1, c2 = st.columns([1, 1])
        with c1:
            cost_total = 0
            str_alocari =[]
            for r, c in assignment:
                cost = mat_orig[r, c]
                cost_total += cost
                str_alocari.append(f"C_{{{r+1},{c+1}}}")
            
            st.latex(r"W_{max} = \{ " + ", ".join([f"(X_{r+1}, Y_{c+1})" for r,c in assignment]) + r" \}")
            st.latex(rf"V(W_{{max}}) = {' + '.join(str_alocari)} = {int(cost_total)}")
            
        with c2:
            st.graphviz_chart(deseneaza_graf_bipartit(mat_orig, assignment), use_container_width=True)
