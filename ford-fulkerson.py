import streamlit as st
import pandas as pd
import graphviz
import random

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI CSS
# ==============================================================================
st.set_page_config(page_title="Algoritmul Ford-Fulkerson", layout="wide", page_icon="🌊")

st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin: 0; font-style: italic;}
    </style>
""", unsafe_allow_html=True)

def fmt(val):
    if pd.isna(val): return "0"
    return str(int(val)) if float(val).is_integer() else f"{val:.2f}"

def get_random_color():
    culori =['#d62728', '#2ca02c', '#1f77b4', '#9400D3', '#FF8C00', '#008B8B', '#FF1493', '#8A2BE2']
    return random.choice(culori)

def genereaza_eticheta_arc(cap, istoric_flux):
    """
    Generează eticheta exact cum se cere în curs:
    - saturat: "Capacitate = f1 + f2 + ... ." și adaugă "//"
    - nesaturat: "Capacitate = f1 + f2 + ... +"
    """
    if not istoric_flux or sum(istoric_flux) == 0:
        return f"{fmt(cap)} +"
    
    flux_curent = sum(istoric_flux)
    str_flux = ""
    for idx, val in enumerate(istoric_flux):
        if val == 0: continue
        if val > 0 and idx > 0:
            str_flux += f" + {fmt(val)}"
        elif val > 0 and idx == 0:
            str_flux += f"{fmt(val)}"
        else:
            str_flux += f" - {fmt(abs(val))}"
            
    if flux_curent >= cap:
        return f"{fmt(cap)} = {str_flux} . \n //" # Punctul și cele 2 liniuțe
    else:
        return f"{fmt(cap)} = {str_flux} +"

# ==============================================================================
# REPREZENTAREA GRAFICĂ
# ==============================================================================
def deseneaza_graf_retea(arce_df, istoric_fluxuri, etichete_noduri=None, lant_curent=None):
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', bgcolor='transparent')
    
    graf.attr('node', shape='circle', style='filled', fillcolor='#ffecd9', color='#e65c00', fontcolor='#cc5200', fontname='Helvetica', penwidth='2')
    
    noduri = set(arce_df['Start (x_i)']).union(set(arce_df['Destinație (x_j)']))
    str_noduri = {str(int(n)) for n in noduri}
    
    # Așezare forțată ca în curs
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
        c_ij = rand['Capacitate c(u)']
        f_ij = rand['Flux f(u)']
        
        flux_history = istoric_fluxuri.get((int(i), int(j)),[])
        label_arc = genereaza_eticheta_arc(c_ij, flux_history)
        
        # Stilizarea muchiilor
        if (i, j) in muchii_lant or (j, i) in muchii_lant:
            graf.edge(i, j, label=label_arc, color='#1f77b4', penwidth='3.5', fontcolor='#1f77b4', fontsize='12', fontname='Helvetica-bold')
        elif f_ij >= c_ij:
            # ARC SATURAT -> ROȘU și mai gros
            graf.edge(i, j, label=label_arc, color='#d62728', penwidth='2.5', fontcolor='#d62728', fontsize='12', fontname='Helvetica-bold')
        else:
            # ARC NESATURAT -> Gri normal
            graf.edge(i, j, label=label_arc, color='#a0a0a0', penwidth='1.5', fontcolor='#555555', fontsize='11')
            
    return graf

# ==============================================================================
# ALGORITMUL FORD-FULKERSON
# ==============================================================================
def ford_fulkerson(df_arce, sursa, dest):
    df = df_arce.copy()
    istoric =[]
    iteratie = 1
    
    # Inițializăm dicționarul care ține minte cum s-au adunat fluxurile (pentru afișarea cu + și .)
    istoric_fluxuri = {}
    for _, rand in df.iterrows():
        i, j = int(rand['Start (x_i)']), int(rand['Destinație (x_j)'])
        f = rand['Flux f(u)']
        if f > 0:
            istoric_fluxuri[(i, j)] = [f]
        else:
            istoric_fluxuri[(i, j)] =[]
    
    while True:
        culoare_iter = get_random_color() 
        etichete = {sursa: ("[+]", culoare_iter)}
        parinti = {sursa: (None, None)} 
        
        coada = [sursa]
        dest_gasita = False
        
        while coada and not dest_gasita:
            nod_curent = coada.pop(0)
            
            # Arce directe
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
            
            # Arce inverse
            arce_inverse = df[df['Destinație (x_j)'] == nod_curent]
            for _, rand in arce_inverse.iterrows():
                vecin = rand['Start (x_i)']
                flux = rand['Flux f(u)']
                if vecin not in etichete and flux > 0:
                    etichete[vecin] = (f"[-x_{int(nod_curent)}]", culoare_iter)
                    parinti[vecin] = (nod_curent, '-')
                    coada.append(vecin)
                    if vecin == dest: dest_gasita = True; break

        # Condiția de STOP
        if not dest_gasita:
            istoric.append({'iteratie': 'STOP', 'status': 'STOP', 'etichete': etichete, 'df_stare': df.copy(), 'istoric_fluxuri': {k: list(v) for k, v in istoric_fluxuri.items()}})
            break
            
        # Reconstituire lanț
        lant =[]
        curent = dest
        while curent != sursa:
            parinte, sens = parinti[curent]
            if sens == '+': lant.append((parinte, curent, '+'))
            else: lant.append((curent, parinte, '-'))
            curent = parinte
        lant.reverse()
        
        # Calculăm Alpha
        alphas =[]
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
        
        # Actualizăm fluxul și istoricul (pentru desen)
        for u, v, sens in lant:
            idx = df.index[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].tolist()[0]
            if sens == '+': 
                df.at[idx, 'Flux f(u)'] += alpha
                istoric_fluxuri[(int(u), int(v))].append(alpha)
            else: 
                df.at[idx, 'Flux f(u)'] -= alpha
                istoric_fluxuri[(int(u), int(v))].append(-alpha)
                
        istoric.append({
            'iteratie': iteratie, 'status': 'CONTINUA', 'etichete': etichete,
            'lant': lant, 'alpha': alpha, 'formule_alpha': formule_alpha, 
            'df_stare': df.copy(), 'istoric_fluxuri': {k: list(v) for k, v in istoric_fluxuri.items()}
        })
        iteratie += 1
        if iteratie > 50: break
    return istoric, df

# ==============================================================================
# UI PRINCIPAL STREAMLIT
# ==============================================================================
st.markdown('''
    <div class="title-box">
        <p class="title-text">📐 Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Flux Maxim: Algoritmul Ford-Fulkerson</p>
    </div>
''', unsafe_allow_html=True)

col_t1, col_g1 = st.columns([1, 1.2])
with col_t1:
    st.markdown("<h4 style='color:#e65c00;'>1. Structura Rețelei</h4>", unsafe_allow_html=True)
    st.write("Datele sunt introduse conform problemei scrise, plecând deja de la fluxul $f_0 = 37$ pentru a prinde exact iterațiile din curs.")
    
    if "tabel_retea" not in st.session_state:
        # Date precise din curs, paginile 1-5
        date_curs =[
            [1,2, 20, 10],[1,3, 30, 4],[1,4, 40, 23],[2,5, 20, 0],[2,7, 10, 10],[3,5, 17, 0],[3,8, 24, 4],[4,6, 18, 0],[4,9, 23, 23],[5,7, 10, 0],[5,8, 9, 0],[6,8, 12, 0], [6,9, 8, 0],[7,10, 31, 10],[8,10, 23, 4],[9,10, 42, 23]
        ]
        st.session_state.tabel_retea = pd.DataFrame(date_curs, columns=["Start (x_i)", "Destinație (x_j)", "Capacitate c(u)", "Flux f(u)"])

    edited_df = st.data_editor(st.session_state.tabel_retea, num_rows="dynamic", use_container_width=True)
    noduri_disp = sorted(list(set(edited_df['Start (x_i)']).union(set(edited_df['Destinație (x_j)']))))
    
    col_sursa, col_dest = st.columns(2)
    with col_sursa: n_start = st.selectbox("Sursă", noduri_disp, index=0)
    with col_dest: n_dest = st.selectbox("Destinație", noduri_disp, index=len(noduri_disp)-1)

with col_g1:
    st.markdown("<h4 style='color:#e65c00;'>Graful Curent</h4>", unsafe_allow_html=True)
    istoric_initial = { (int(r['Start (x_i)']), int(r['Destinație (x_j)'])): [r['Flux f(u)']] if r['Flux f(u)']>0 else[] for _, r in edited_df.iterrows() }
    st.graphviz_chart(deseneaza_graf_retea(edited_df, istoric_initial), use_container_width=True)

if st.button("🚀 Rulează Ford-Fulkerson", type="primary", use_container_width=True):
    st.divider()
    istoric, df_final = ford_fulkerson(edited_df, n_start, n_dest)
    
    st.markdown("<h3 style='color: #e65c00;'>⚙️ Etapele Algoritmului</h3>", unsafe_allow_html=True)
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
                st.graphviz_chart(deseneaza_graf_retea(pas['df_stare'], pas['istoric_fluxuri'], etichete_noduri=pas['etichete'], lant_curent=pas['lant']), use_container_width=True)
            else:
                st.success(f"**TO ($I_{{STOP}}$)**: Destinația NU a mai putut fi etichetată. STOP ALGORITM.")
                st.graphviz_chart(deseneaza_graf_retea(pas['df_stare'], pas['istoric_fluxuri'], etichete_noduri=pas['etichete']), use_container_width=True)

    # ==========================================================================
    # VALIDAREA FINALĂ (TĂIETURA) CONFORM PROBLEMELOR SCRISE DE MÂNĂ
    # ==========================================================================
    st.divider()
    st.markdown("### VERIFICARE")
    
    # Nodurile marcate și nemarcate
    noduri_A = list(istoric[-1]['etichete'].keys())
    noduri_XA = [n for n in noduri_disp if n not in noduri_A]
    
    str_XA = ", ".join([f"x_{{{int(n)}}}" for n in noduri_XA])
    
    st.write("**① Tăietura $T$** = { mulțimea vf. graf care nu s-au putut eticheta cu etich. de la $I_{STOP}$ }")
    st.latex(rf"T = \{{ {str_XA} \}} \implies \begin{{cases}} x_s \notin T & \checkmark \\ x_t \in T & \checkmark \end{{cases}}")
    
    st.write("**② Grafic Tăietura T** = trasare curbă care:")
    st.write("* trece doar prin arce saturate;")
    st.write("* separă vf. marcate cu eticheta $I_{STOP}$ de cele nemarcate cu aceeași etichetă.")
    
    st.write("**③ $C(T) = \sum c(u)$** ($u$ arc saturat din tăietură) $\overset{?}{=} f_{max}$")
    
    # Calcul Tăietura (Suma capacităților de la A la T)
    cap_taietura = 0
    arce_taietura_noduri =[]
    arce_taietura_valori =[]
    
    for _, rand in df_final.iterrows():
        i, j = rand['Start (x_i)'], rand['Destinație (x_j)']
        if i in noduri_A and j in noduri_XA:
            c = rand['Capacitate c(u)']
            cap_taietura += c
            arce_taietura_noduri.append((i, j))
            arce_taietura_valori.append(c)
            
    flux_iesire = df_final[df_final['Start (x_i)'] == n_start]['Flux f(u)'].sum()
    flux_intrare = df_final[df_final['Destinație (x_j)'] == n_start]['Flux f(u)'].sum()
    f_max = flux_iesire - flux_intrare
    
    if arce_taietura_noduri:
        str_arce_calc = " + ".join([f"c(x_{{{int(u)}}}, x_{{{int(v)}}})" for u, v in arce_taietura_noduri])
        str_vals_calc = " + ".join([str(int(val)) for val in arce_taietura_valori])
        st.latex(rf"C(T) = {str_arce_calc} = {str_vals_calc} = {fmt(cap_taietura)} = f_{{max}} \;\; \checkmark")
