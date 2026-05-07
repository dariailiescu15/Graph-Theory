import streamlit as st
import pandas as pd
import numpy as np
import graphviz

# ==============================================================================
# 1. CONFIGURARE MEDIU ȘI IDENTITATE VIZUALĂ
# ==============================================================================
st.set_page_config(page_title="Algoritmul UNGAR - Studiu Academic", layout="wide", page_icon="🧩")

# Definirea stilurilor CSS pentru o interfață academică (Matrice, Culori, Simboluri)
st.markdown("""
    <style>
    /* Stiluri pentru antet și titlu */
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin-top: 10px; font-style: italic;}
    
    /* Stiluri pentru autori (Aliniere dreapta conform cerinței) */
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    
    /* Stiluri pentru tabelele matematice (Matricea de costuri) */
    .matrix-table { border-collapse: collapse; margin: 0 auto; font-family: 'Courier New', monospace; font-size: 18px; border: 2px solid #333; }
    .matrix-table td { border: 1px solid #333; width: 55px; height: 55px; text-align: center; vertical-align: middle; }
    
    /* Reprezentarea zonelor de acoperire (Tăieturi) */
    .t1 { background-color: #ffffff; } /* Zonă albă - Neacoperită (Elemente T1) */
    .t2 { background-color: #ffb366; } /* Portocaliu - Linie de tăiere (Elemente T2) */
    .t3 { background-color: #e67300; } /* Portocaliu închis - Intersecție (Elemente T3) */
    
    /* Simboluri specifice Algoritmului Ungar */
    .boxed-zero { border: 2px solid black; padding: 3px; font-weight: bold; display: inline-block; width: 25px; background: white; }
    .crossed-zero { text-decoration: line-through; color: #777; font-weight: bold; }
    .star-sym { color: red; font-weight: bold; font-size: 20px; margin-left: 5px; }
    
    /* Casete de informații */
    .legend-box { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Afișarea Antetului (Titlu și Autori)
st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Probleme de afectare: Algoritmul UNGAR (AU)</p>
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
# 2. LOGICA ALGORITMICĂ (IMPLEMENTARE MANUALA CONFORM SEMINAR)
# ==============================================================================

def incadrare_zerouri_manual(mat):
    """
    Identifică zerourile independente conform procedurii manuale:
    1. Se caută linia cu cel mai mic număr de zerouri disponibile.
    2. Se încadrează primul zero găsit (boxed).
    3. Se barează automat toate celelalte zerouri de pe aceeași linie și coloană (crossed).
    """
    n = mat.shape[0]
    boxed = []
    crossed = []
    r_used = [False] * n
    c_used = [False] * n
    m_temp = mat.copy()

    while True:
        counts = []
        for i in range(n):
            if not r_used[i]:
                # Numărăm zerourile pe coloane care nu au fost încă ocupate de un zero încadrat
                zeros = [j for j in range(n) if m_temp[i, j] == 0 and not c_used[j]]
                if zeros:
                    counts.append((len(zeros), i, zeros))
        
        if not counts: break # Nu mai există zerouri de încadrat
        
        # Alegem linia prioritară (cele mai puține zerouri)
        counts.sort()
        _, r_idx, available_cols = counts[0]
        c_idx = available_cols[0]

        boxed.append((r_idx, c_idx))
        r_used[r_idx] = True
        c_used[c_idx] = True

        # Barăm restul zerourilor conflictuale (aceeași linie sau coloană)
        for j in range(n):
            if m_temp[r_idx, j] == 0 and j != c_idx:
                crossed.append((r_idx, j))
            if m_temp[j, c_idx] == 0 and j != r_idx:
                crossed.append((j, c_idx))
                
    return boxed, list(set(crossed))

def marcaj_si_taieturi_könig(mat, boxed, crossed):
    """
    Implementează Teorema lui König (Procedura de marcaj lateral):
    - Marcarea rândurilor fără zero încadrat.
    - Marcarea coloanelor cu zerouri barate în rânduri marcate.
    - Marcarea rândurilor cu zerouri încadrate în coloane marcate.
    Determină suportul minim (tăieturile portocalii).
    """
    n = mat.shape[0]
    bx_rows = {r for r, c in boxed}
    
    # 1. Marcăm rândurile care NU conțin zerouri încadrate
    m_rows = set(range(n)) - bx_rows
    m_cols = set()
    
    changed = True
    while changed:
        before = len(m_rows) + len(m_cols)
        # 2. Marcăm coloanele care au 0 barat (crossed) în rânduri deja marcate
        for r, c in crossed:
            if r in m_rows: m_cols.add(c)
        # 3. Marcăm rândurile care au 0 încadrat (boxed) în coloane deja marcate
        for r, c in boxed:
            if c in m_cols: m_rows.add(r)
        changed = (len(m_rows) + len(m_cols)) != before

    # Tăieturile sunt definite de rândurile nemarcate și coloanele marcate
    cov_rows = [i for i in range(n) if i not in m_rows]
    cov_cols = list(m_cols)
    return cov_rows, cov_cols, m_rows, m_cols

def draw_table_html(mat, r_cov, c_cov, boxed, crossed, m_rows, m_cols):
    """Construiește reprezentarea grafică a matricei în format HTML."""
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
            # Determinarea culorii fundalului (Tăieturi și Intersecții)
            cls = "t1"
            if i in r_cov and j in c_cov: cls = "t3" # Intersecție
            elif i in r_cov or j in c_cov: cls = "t2" # Tăietură (Acoperire)
            
            val = int(mat[i, j])
            content = str(val)
            if (i, j) in bx: content = '<span class="boxed-zero">0</span>'
            elif (i, j) in cr: content = '<span class="crossed-zero">0</span>'
            
            html += f'<td class="{cls}">{content}</td>'
        html += '</tr>'
    return html + "</table>"

# ==============================================================================
# 3. INTERFAȚĂ ȘI GESTIUNEA DATELOR
# ==============================================================================

# Matricea extrasă din seminarul scris de mână (Pagina 4)
seminar_initial_data = [
    [99, 21, 53, 46, 18, 80],
    [34, 20, 79, 65, 11, 14],
    [76, 10, 73, 56, 47, 42],
    [79, 39, 76, 80, 81, 24],
    [37, 95, 89, 83, 73, 19],
    [74, 54, 91, 34, 20, 85]
]

st.markdown("""
<div class="legend-box">
    <strong>Legendă Reprezentări Grafice:</strong><br>
    • <strong>Tăieturile (Supportul Minim):</strong> Reprezentate prin celule <strong>portocalii</strong> (Liniile nemarcate și coloanele marcate).<br>
    • <strong>Intersecțiile (Elemente T3):</strong> Reprezentate prin celule <strong>portocaliu închis</strong> (Locul unde se adună elementul minim epsilon).<br>
    • <strong>Marcajul (*) :</strong> Procedură laterală utilizată pentru determinarea suportului optim în cazul în care cuplajul nu este maxim.
</div>
""", unsafe_allow_html=True)

st.subheader("I. Matricea Costurilor (C) - Date Seminar")
input_df = st.data_editor(pd.DataFrame(seminar_initial_data, 
                                       columns=[f"y{i+1}" for i in range(6)], 
                                       index=[f"x{i+1}" for i in range(6)]), 
                          use_container_width=True)

# Selecția tipului de optimizare
tip_problem = st.selectbox("Obiectivul Optimizării:", ["Minimizare (Cost Minim)", "Maximizare (Profit Maxim)"])

# ==============================================================================
# 4. PROCESARE PAS CU PAS
# ==============================================================================

if st.button("Execută Studiul de Afectare", type="primary", use_container_width=True):
    mat_orig = input_df.values.copy()
    mat = mat_orig.astype(float)
    n = mat.shape[0]
    
    st.markdown("### PAS 1: Etapa de Reducere")
    
    # Tratarea cazului de Maximizare (C* = Max_Matrix - C)
    if tip_problem == "Maximizare (Profit Maxim)":
        mat = np.max(mat) - mat
        st.write("Notă: Matricea a fost transformată pentru o problemă de minimizare prin scădere din valoarea maximă absolută.")

    # Reducerea pe linii (MIN L)
    min_l = mat.min(axis=1, keepdims=True)
    mat -= min_l
    # Reducerea pe coloane (MIN C)
    min_c = mat.min(axis=0, keepdims=True)
    mat -= min_c
    
    st.latex(r"\sum MIN(L) = " + str(int(np.sum(min_l))) + r", \quad \sum MIN(C) = " + str(int(np.sum(min_c))))

    # Inițierea procesului iterativ de la I0
    iter_idx = 0
    history_eps = []

    while iter_idx < 10:
        bx, cr = incadrare_zerouri_manual(mat)
        r_cov, c_cov, m_rows, m_cols = marcaj_si_taieturi_könig(mat, bx, cr)
        
        st.divider()
        st.markdown(f"#### Iterația $I_{iter_idx}$")
        
        col_stare, col_matr = st.columns([1, 2])
        
        with col_stare:
            st.write(f"Zerouri încadrate ($\boxed{0}$): **{len(bx)}**")
            st.write(f"Ordin matrice (n): **{n}**")
            
            if len(bx) == n:
                st.success("✅ Condiția de optimalitate a fost atinsă (m = n). STOP Algoritm.")
                # La optimalitate, afișăm doar cuplajul, fără tăieturi portocalii
                r_cov, c_cov, m_rows, m_cols = [], [], set(), set()
                st.markdown(draw_table_html(mat, r_cov, c_cov, bx, cr, m_rows, m_cols), unsafe_allow_html=True)
                break
            else:
                st.warning(f"Condiția eșuată ({len(bx)} < {n}). Se determină suportul minim pentru ajustare.")
                with col_matr:
                    st.markdown(draw_table_html(mat, r_cov, c_cov, bx, cr, m_rows, m_cols), unsafe_allow_html=True)

        # Calculul Epsilon (E): minimul elementelor neacoperite (T1)
        uncovered = [mat[r, c] for r in range(n) for c in range(n) if r not in r_cov and c not in c_cov]
        epsilon = min(uncovered)
        history_eps.append((epsilon, len(r_cov) + len(c_cov)))
        st.latex(r"\epsilon_{" + str(iter_idx) + r"} = \min \{ \text{elemente netăiate} \} = " + str(int(epsilon)))

        # Ajustarea matricei conform regulilor AU
        for r in range(n):
            for c in range(n):
                if r not in r_cov and c not in c_cov: mat[r, c] -= epsilon # T1: Scădere
                if r in r_cov and c in c_cov: mat[r, c] += epsilon      # T3: Adunare
        
        iter_idx += 1

    # Rezultate Finale și Reprezentare Grafică
    st.divider()
    st.subheader("III. Rezumatul Afectării și Validare Matematică")
    
    res_text, res_graph = st.columns(2)
    v_sum = 0
    with res_text:
        st.write("**Repartizarea optimă a resurselor:**")
        for r, c in bx:
            cost_u = int(mat_orig[r, c])
            v_sum += cost_u
            st.write(f"• **x{r+1}** repartizat la **y{c+1}** | Cost unitar: {cost_u}")
        
        st.markdown(f"### Valoare Funcție Obiectiv ($V_{{AU}}$): {v_sum}")

    with res_graph:
        # Generarea grafului bipartit al soluției
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR', size='6,6')
        for i in range(n): dot.node(f'X{i}', f'x{i+1}', color='#e65c00', fontcolor='#e65c00', penwidth='2')
        for j in range(n): dot.node(f'Y{j}', f'y{j+1}', color='#2e7d32', fontcolor='#2e7d32', penwidth='2')
        for r, c in bx:
            dot.edge(f'X{r}', f'Y{c}', label=str(int(mat_orig[r, c])), color='#333', penwidth='2.5')
        st.graphviz_chart(dot)

    # Validare pe baza reducerilor și ajustărilor succesive
    st.markdown("#### Validarea analitică a costului final:")
    sum_red = np.sum(min_l) + np.sum(min_c)
    sum_eps = sum([e * (n - m) for e, m in history_eps])
    
    if tip_problem == "Minimizare (Cost Minim)":
        st.latex(r"V_{min} = \sum MIN(L) + \sum MIN(C) + \sum_{k=0}^{STOP} \epsilon_k(n - m_k)")
        st.write(f"Verificare: {int(sum_red)} (reduceri) + {int(sum_eps)} (ajustări epsilon) = **{int(sum_red + sum_eps)}**")
    else:
        st.write("Pentru probleme de Maximizare, validarea se confirmă prin însumarea valorilor din matricea originală.")
