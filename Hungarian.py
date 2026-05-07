import streamlit as st
import pandas as pd
import numpy as np
import graphviz
from scipy.optimize import linear_sum_assignment

# ==============================================================================
# 1. CONFIGURARE PAGINĂ ȘI DESIGN (CSS CUSTOM)
# ==============================================================================
st.set_page_config(page_title="Algoritmul Ungar - Cercetări Operaționale", layout="wide", page_icon="🧮")

# Stiluri CSS pentru a face interfața să arate ca un document academic/curs
st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    .title-box { background-color: #e3f2fd; border-radius: 15px; padding: 30px; text-align: center; border: 2px solid #1565c0; margin-bottom: 25px; }
    .title-text { color: #0d47a1; font-size: 40px; font-weight: bold; margin: 0; }
    .subtitle-text { color: #1565c0; font-size: 20px; }
    
    /* Stiluri pentru tabelele de tip matrice */
    .matrix-table { border-collapse: collapse; margin: 20px auto; font-family: monospace; font-size: 18px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .matrix-table td { border: 1px solid #999; width: 50px; height: 50px; text-align: center; vertical-align: middle; }
    
    /* Culori pentru tipurile de elemente conform cursului */
    .t1 { background-color: #ffffff; } /* Neacoperite */
    .t2 { background-color: #fff9c4; } /* Acoperite o dată */
    .t3 { background-color: #ffcc80; border: 2px solid #e65100 !important; } /* Intersecții (dublu acoperite) */
    
    .step-header { color: #2e7d32; border-bottom: 2px solid #2e7d32; padding-bottom: 5px; margin-top: 30px; }
    .info-box { background-color: #f1f8e9; border-left: 5px solid #2e7d32; padding: 15px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA MATEMATICĂ (ALGORITMUL UNGAR)
# ==============================================================================

def get_minimum_cover(matrix):
    """
    Determină numărul minim de linii (orizontale/verticale) necesare pentru a acoperi toate zerourile.
    Implementează Teorema lui König.
    """
    n = matrix.shape[0]
    # Creăm o matrice booleană unde True sunt zerourile
    zero_mask = (matrix == 0)
    
    # Utilizăm linear_sum_assignment pentru a găsi un cuplaj maxim în graful zerourilor
    row_ind, col_ind = linear_sum_assignment(~zero_mask)
    matches = list(zip(row_ind, col_ind))
    # Filtrăm doar acele potriviri care sunt efectiv zerouri
    actual_matches = [(r, c) for r, c in matches if matrix[r, c] == 0]
    
    # Procedura de marcare (labeling procedure) pentru a găsi suportul minim
    matched_rows = {r for r, c in actual_matches}
    unmatched_rows = set(range(n)) - matched_rows
    
    marked_rows = set(unmatched_rows)
    marked_cols = set()
    new_marks = True
    
    while new_marks:
        new_marks = False
        # Marcăm coloanele care au zerouri în rândurile marcate
        for r in list(marked_rows):
            for c in range(n):
                if matrix[r, c] == 0 and c not in marked_cols:
                    marked_cols.add(c)
                    new_marks = True
        # Marcăm rândurile care au cuplaje în coloanele marcate
        for r, c in actual_matches:
            if c in marked_cols and r not in marked_rows:
                marked_rows.add(r)
                new_marks = True
                
    # Suportul minim: rândurile NEMARCATE și coloanele MARCATE
    covered_rows = set(range(n)) - marked_rows
    covered_cols = marked_cols
    
    return list(covered_rows), list(covered_cols), actual_matches

# ==============================================================================
# 3. COMPONENTE VIZUALE (MATRICE HTML ȘI GRAF)
# ==============================================================================

def render_matrix_html(mat, cov_rows, cov_cols):
    """Generează un tabel HTML colorat conform regulilor T1, T2, T3 din curs."""
    html = '<table class="matrix-table">'
    for i in range(mat.shape[0]):
        html += '<tr>'
        for j in range(mat.shape[1]):
            val = int(mat[i, j])
            # Clasificare celule
            is_row_cov = i in cov_rows
            is_col_cov = j in cov_cols
            
            cell_class = "t1"
            if is_row_cov and is_col_cov: cell_class = "t3" # Intersecție
            elif is_row_cov or is_col_cov: cell_class = "t2" # Acoperit o dată
            
            style = "color: #d32f2f; font-weight: bold;" if val == 0 else "color: #333;"
            html += f'<td class="{cell_class}" style="{style}">{val}</td>'
        html += '</tr>'
    html += '</table>'
    return html

def draw_bipartite(assignment, original_matrix):
    """Desenează graful bipartit final folosind Graphviz."""
    dot = graphviz.Digraph(comment='Soluție Finală')
    dot.attr(rankdir='LR', size='8,5')
    
    # Noduri stânga (Muncitori/Resurse X)
    with dot.subgraph(name='cluster_0') as c:
        c.attr(label='Muncitori (X)', color='blue')
        for i in range(original_matrix.shape[0]):
            c.node(f'X{i+1}', f'x{i+1}', style='filled', fillcolor='#bbdefb')

    # Noduri dreapta (Sarcini Y)
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='Sarcini (Y)', color='red')
        for j in range(original_matrix.shape[1]):
            c.node(f'Y{j+1}', f'y{j+1}', style='filled', fillcolor='#ffcdd2')

    # Muchii (Cuplajul optim)
    for r, c in assignment:
        cost = int(original_matrix[r, c])
        dot.edge(f'X{r+1}', f'Y{c+1}', label=f'cost {cost}', color='#2e7d32', penwidth='2.0')
    
    return dot

# ==============================================================================
# 4. INTERFAȚA UTILIZATOR (UI)
# ==============================================================================

st.markdown('''
    <div class="title-box">
        <p class="title-text">Metoda Ungară (Kuhn-Munkres)</p>
        <p class="subtitle-text">Optimizarea Problemelor de Afectare (Minimizarea Costurilor)</p>
    </div>
''', unsafe_allow_html=True)

# Sidebar pentru info
with st.sidebar:
    st.header("📌 Legendă Curs")
    st.info("""
    **T1 (Alb):** Elemente netăiate. Din ele se scade $\Sigma$.
    
    **T2 (Galben):** Elemente tăiate o dată. Rămân neschimbate.
    
    **T3 (Portocaliu):** Intersecții. Se adună $\Sigma$.
    """)
    st.write("---")
    st.latex(r"m: \text{nr. linii acoperire}")
    st.latex(r"n: \text{dimensiune matrice}")

# Introducere date
st.subheader("1. Introducere Matricea Costurilor ($C$)")
if "data" not in st.session_state:
    # Date implicite din exemplul de curs (6x6)
    default_data = [
        [55, 23, 83, 61, 66, 22],
        [99, 81, 14, 77, 61, 55],
        [59, 39, 58, 49, 24, 54],
        [36, 10, 37, 62, 28, 33],
        [73, 51, 51, 24, 26, 55],
        [72, 54, 78, 91, 89, 96]
    ]
    st.session_state.data = pd.DataFrame(default_data)

input_df = st.data_editor(st.session_state.data, use_container_width=True)

if st.button("🚀 Execută Calculul Pas cu Pas", type="primary"):
    mat_orig = input_df.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]
    
    # --------------------------------------------------------------------------
    # PASUL 1: Reducerea pe linii și coloane
    # --------------------------------------------------------------------------
    st.markdown('<h3 class="step-header">Pasul 1: Reducerea Matricei</h3>', unsafe_allow_html=True)
    
    # Reducere Linii
    row_mins = mat.min(axis=1)
    for i in range(n): mat[i, :] -= row_mins[i]
    
    # Reducere Coloane
    col_mins = mat.min(axis=0)
    for j in range(n): mat[:, j] -= col_mins[j]
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Minime pe linii:**")
        st.latex(r"\sum MIN(L) = " + " + ".join([str(int(x)) for x in row_mins]) + f" = {int(sum(row_mins))}")
    with c2:
        st.write("**Minime pe coloane:**")
        st.latex(r"\sum MIN(C) = " + " + ".join([str(int(x)) for x in col_mins]) + f" = {int(sum(col_mins))}")

    # --------------------------------------------------------------------------
    # ITERAȚII: Acoperire și Ajustare (Sigma)
    # --------------------------------------------------------------------------
    st.markdown('<h3 class="step-header">Pasul 2 & 3: Determinarea Suportului Minim</h3>', unsafe_allow_html=True)
    
    iteration = 0
    total_sigma_adjustment = 0
    
    while iteration < 10: # Siguranță împotriva buclelor infinite
        cov_rows, cov_cols, assignment = get_minimum_cover(mat)
        m = len(cov_rows) + len(cov_cols)
        
        st.write(f"**Iterația {iteration + 1}:**")
        st.markdown(render_matrix_html(mat, cov_rows, cov_cols), unsafe_allow_html=True)
        
        if m == n:
            st.success(f"✅ Optimizare reușită! $m = n = {n}$")
            break
        
        # Calcul $\Sigma$ (minimul elementelor neacoperite - T1)
        uncovered_elements = []
        for r in range(n):
            for c in range(n):
                if r not in cov_rows and c not in cov_cols:
                    uncovered_elements.append(mat[r, c])
        
        sigma = min(uncovered_elements)
        st.warning(f"⚠️ $m ({m}) < n ({n})$. Se aplică ajustarea $\Sigma = {int(sigma)}$")
        
        # Ajustare matrice conform regulii din curs
        # T1 (netăiate): -sigma | T3 (intersecții): +sigma
        for r in range(n):
            for c in range(n):
                if r not in cov_rows and c not in cov_cols:
                    mat[r, c] -= sigma
                elif r in cov_rows and c in cov_cols:
                    mat[r, c] += sigma
        
        total_sigma_adjustment += sigma * (n - m)
        iteration += 1

    # --------------------------------------------------------------------------
    # REZULTAT FINAL
    # --------------------------------------------------------------------------
    st.markdown('<h3 class="step-header">Pasul Final: Soluția Optimă</h3>', unsafe_allow_html=True)
    
    col_res1, col_res2 = st.columns([1, 1])
    
    with col_res1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.write("**Cuplajul Maxim Găsit:**")
        cost_final = 0
        expresie_calcul = []
        for r, c in assignment:
            val = int(mat_orig[r, c])
            cost_final += val
            expresie_calcul.append(str(val))
            st.write(f"Muncitor $x_{r+1} \longrightarrow$ Sarcina $y_{c+1}$ (Cost: {val})")
        
        st.write("---")
        st.write("**Valoarea Minimă a Funcției Obiectiv:**")
        st.latex(r"V(W_{max}) = " + " + ".join(expresie_calcul) + f" = {cost_final}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_res2:
        st.write("**Reprezentare Graf Bipartit:**")
        st.graphviz_chart(draw_bipartite(assignment, mat_orig))

    # --------------------------------------------------------------------------
    # VERIFICARE TEORETICĂ (Formula din Curs)
    # --------------------------------------------------------------------------
    st.markdown('<h3 class="step-header">Verificarea Analitică</h3>', unsafe_allow_html=True)
    st.write("Conform formulei de verificare din curs (Pag. 7/16):")
    st.latex(r"V_{min} = \sum MIN(L) + \sum MIN(C) + \sum \Sigma_k(n - m_k)")
    
    term1 = sum(row_mins)
    term2 = sum(col_mins)
    term3 = total_sigma_adjustment
    
    st.latex(f"{int(term1)} + {int(term2)} + {int(term3)} = {int(term1 + term2 + term3)}")
    
    if int(term1 + term2 + term3) == cost_final:
        st.info("💡 Observație: Rezultatul analitic coincide cu suma costurilor de pe graf. Verificare OK.")
    else:
        st.error("Eroare de calcul în verificare.")

# Subsol
st.markdown("---")
st.caption("Proiect realizat pentru disciplina Cercetări Operaționale - Facultatea de Științe Aplicate.")
