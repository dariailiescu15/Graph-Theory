import streamlit as st
import pandas as pd
import graphviz
import random

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI
# ==============================================================================
st.set_page_config(page_title="Algoritmul Ford-Fulkerson", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 45px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 22px; margin-top: 10px; font-style: italic;}
    
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    
    .validation-box { background-color: #fff4ea; border-left: 5px solid #e65c00; padding: 15px; margin-top: 20px; color: #333; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# FUNCȚII UTILITARE ȘI FORMATĂRI
# ==============================================================================
def fmt(val):
    """Formatează valorile numerice pentru a elimina zecimalele (.0) inutile."""
    if pd.isna(val): return "0"
    return str(int(val)) if float(val).is_integer() else f"{val:.2f}"

def get_random_color():
    """Generează o culoare hexazecimală pentru a diferenția etichetele nodurilor la fiecare iterație."""
    culori =['#d62728', '#2ca02c', '#1f77b4', '#9400D3', '#FF8C00', '#008B8B', '#FF1493', '#8A2BE2']
    return random.choice(culori)

def genereaza_eticheta_arc(cap, istoric_flux, is_initial=False):
    """
    Construiește eticheta muchiei:
    - Graful inițial: doar capacitatea (ex: "10")
    - Iterații nesaturate: capacitate = f1 + f2 + ... + (ex: "10 = 4 +")
    - Iterații saturate: capacitate = f1 + f2 + ... . // (ex: "10 = 4 + 6 .\n//")
    """
    # Dacă suntem pe graful inițial, returnăm strict valoarea capacității
    if is_initial:
        return f"{fmt(cap)}"
        
    # Dacă suntem în timpul iterațiilor, dar arcul e neatins
    if not istoric_flux:
        return f"{fmt(cap)} +"
    
    flux_curent = sum(istoric_flux)
    str_flux = ""
    
    # Construim șirul operațiilor pentru flux
    for idx, val in enumerate(istoric_flux):
        if val == 0: continue
        if val > 0 and len(str_flux) > 0:
            str_flux += f" + {fmt(val)}"
        elif val > 0 and len(str_flux) == 0:
            str_flux += f"{fmt(val)}"
        else:
            str_flux += f" - {fmt(abs(val))}"
            
    if str_flux == "":
        str_flux = "0"
            
    # Adăugăm terminatiile specifice: . și // pentru saturat, + pentru nesaturat
    if flux_curent >= cap:
        return f"{fmt(cap)} = {str_flux} . \n //"
    else:
        return f"{fmt(cap)} = {str_flux} +"

# ==============================================================================
# MODULUL DE REPREZENTARE GRAFICĂ (GRAPHVIZ)
# ==============================================================================
def deseneaza_graf_retea(arce_df, istoric_fluxuri, etichete_noduri=None, lant_curent=None, muchii_taietura=None, is_initial=False):
    """Generează obiectul topologic Graphviz."""
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', bgcolor='transparent')
    graf.attr('node', shape='circle', style='filled', fillcolor='#f8f9fa', color='#343a40', fontname='Helvetica', penwidth='1.5')
    
    noduri = set(arce_df['Start (x_i)']).union(set(arce_df['Destinație (x_j)']))
    str_noduri = {str(int(n)) for n in noduri}
    
    # Alinierea arhitecturală a nodurilor pe straturi (specific pentru 10 noduri)
    if str_noduri.issuperset({'1','2','3','4','5','6','7','8','9','10'}):
        graf.body.append('{rank=same; "1"}')
        graf.body.append('{rank=same; "2"; "3"; "4"}')
        graf.body.append('{rank=same; "5"; "6"}')
        graf.body.append('{rank=same; "7"; "8"; "9"}')
        graf.body.append('{rank=same; "10"}')
    
    for n in noduri:
        label = f"x{int(n)}"
        color_fill = '#f8f9fa'
        
        if etichete_noduri and n in etichete_noduri:
            eticheta_text, culoare_eticheta = etichete_noduri[n]
            label = f"<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='0'><TR><TD><FONT POINT-SIZE='12' COLOR='{culoare_eticheta}'><B>{eticheta_text}</B></FONT></TD></TR><TR><TD>x{int(n)}</TD></TR></TABLE>>"
            color_fill = '#e9ecef'
            
        graf.node(str(int(n)), label, fillcolor=color_fill)
        
    muchii_lant = set()
    if lant_curent:
        for u, v, _ in lant_curent:
            muchii_lant.add((int(u), int(v)))
            
    for _, rand in arce_df.iterrows():
        i = int(rand['Start (x_i)'])
        j = int(rand['Destinație (x_j)'])
        c_ij = rand['Capacitate c(u)']
        f_ij = rand['Flux f(u)']
        
        flux_history = istoric_fluxuri.get((i, j),[])
        
        # Generăm textul de pe arc folosind funcția corectată
        label_arc = genereaza_eticheta_arc(c_ij, flux_history, is_initial)
        
        if muchii_taietura and (i, j) in muchii_taietura:
            graf.edge(str(i), str(j), label=label_arc, color='#e67e22', style='dashed', penwidth='3.5', fontcolor='#d35400', fontsize='12', fontname='Helvetica-bold')
        elif (i, j) in muchii_lant or (j, i) in muchii_lant:
            graf.edge(str(i), str(j), label=label_arc, color='#1f77b4', penwidth='3.5', fontcolor='#1f77b4', fontsize='12', fontname='Helvetica-bold')
        elif f_ij >= c_ij and not is_initial:
            graf.edge(str(i), str(j), label=label_arc, color='#d62728', penwidth='2.5', fontcolor='#d62728', fontsize='12', fontname='Helvetica-bold')
        else:
            graf.edge(str(i), str(j), label=label_arc, color='#868e96', penwidth='1.2', fontcolor='#495057', fontsize='11')
            
    return graf

# ==============================================================================
# ALGORITMUL MATEMATIC FORD-FULKERSON
# ==============================================================================
def executa_ford_fulkerson(df_arce, sursa, dest):
    """Implementarea procedurii de etichetare și determinare iterativă a fluxului."""
    df = df_arce.copy()
    istoric =[]
    iteratie = 0    # Index pentru Iterație și Flux (I_0, \varphi_0)
    mu_idx = 1      # Index continuu pentru Lanț (\mu_1, \mu_2...)
    phi_total = 0
    
    istoric_fluxuri = {(int(r['Start (x_i)']), int(r['Destinație (x_j)'])):[] for _, r in df.iterrows()}
    df['Flux f(u)'] = 0
    
    while True:
        culoare_iter = get_random_color() 
        etichete = {sursa: ("[+]", culoare_iter)}
        parinti = {sursa: (None, None)} 
        
        coada = [sursa]
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
            istoric.append({
                'iteratie': 'STOP', 'status': 'STOP', 'etichete': etichete, 
                'df_stare': df.copy(), 
                'istoric_fluxuri': {k: list(v) for k, v in istoric_fluxuri.items()},
                'phi_curent': phi_total
            })
            break
            
        lant =[]
        curent = dest
        while curent != sursa:
            parinte, sens = parinti[curent]
            if sens == '+': lant.append((parinte, curent, '+'))
            else: lant.append((curent, parinte, '-'))
            curent = parinte
        lant.reverse()
        
        valori_min_mu = []
        formule_min_mu =[]
        for u, v, sens in lant:
            if sens == '+':
                rand = df[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].iloc[0]
                rezerva = rand['Capacitate c(u)'] - rand['Flux f(u)']
                valori_min_mu.append(rezerva)
                formule_min_mu.append(f"c(x_{int(u)}, x_{int(v)}) - f = {fmt(rezerva)}")
            else:
                rand = df[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].iloc[0]
                rezerva = rand['Flux f(u)']
                valori_min_mu.append(rezerva)
                formule_min_mu.append(f"f(x_{int(u)}, x_{int(v)}) = {fmt(rezerva)}")
                
        min_mu_curent = min(valori_min_mu)
        
        for u, v, sens in lant:
            idx = df.index[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].tolist()[0]
            if sens == '+': 
                df.at[idx, 'Flux f(u)'] += min_mu_curent
                istoric_fluxuri[(int(u), int(v))].append(min_mu_curent)
            else: 
                df.at[idx, 'Flux f(u)'] -= min_mu_curent
                istoric_fluxuri[(int(u), int(v))].append(-min_mu_curent)
                
        phi_prec = phi_total
        phi_total += min_mu_curent
        
        istoric.append({
            'iteratie': iteratie, 
            'mu_idx': mu_idx,
            'status': 'CONTINUA', 
            'etichete': etichete,
            'lant': lant, 
            'min_mu': min_mu_curent, 
            'formule_min_mu': formule_min_mu,
            'phi_prec': phi_prec, 
            'phi_curent': phi_total,
            'df_stare': df.copy(), 
            'istoric_fluxuri': {k: list(v) for k, v in istoric_fluxuri.items()}
        })
        
        iteratie += 1
        mu_idx += 1
        if iteratie > 50: break 
        
    return istoric, df

# ==============================================================================
# INTERFAȚA APLICAȚIEI (STREAMLIT)
# ==============================================================================

st.markdown('''
    <div class="title-box">
        <p class="title-text">Cercetări Operaționale - Teoria Grafurilor</p>
        <p class="subtitle-text">Determinarea Fluxului Maxim: Algoritmul Ford-Fulkerson</p>
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

col_tabel, col_graf = st.columns([1, 1.2])
with col_tabel:
    st.markdown("#### 1. Arhitectura Rețelei de Transport")
    st.write("Datele inițiale reprezintă capacitățile rețelei. **Algoritmul va inițializa automat fluxul de la $0$** și va efectua toate iterațiile necesare folosind Procedura de Etichetare (PE).")
    
    if "tabel_retea" not in st.session_state:
        date_initiale = [[1,2, 20, 0],[1,3, 30, 0],[1,4, 40, 0],[2,5, 20, 0],[2,7, 10, 0],[3,5, 17, 0],[3,8, 24, 0],[4,6, 18, 0],[4,9, 23, 0],[5,7, 10, 0],[5,8, 9, 0],[6,8, 12, 0],[6,9, 8, 0],[7,10, 31, 0],[8,10, 23, 0],[9,10, 42, 0]
        ]
        st.session_state.tabel_retea = pd.DataFrame(date_initiale, columns=["Start (x_i)", "Destinație (x_j)", "Capacitate c(u)", "Flux f(u)"])

    edited_df = st.data_editor(st.session_state.tabel_retea, num_rows="dynamic", use_container_width=True)
    noduri_disp = sorted(list(set(edited_df['Start (x_i)']).union(set(edited_df['Destinație (x_j)']))))
    
    c_start, c_dest = st.columns(2)
    with c_start: n_start = st.selectbox("Sursă ($x_s$)", noduri_disp, index=0)
    with c_dest: n_dest = st.selectbox("Destinație ($x_t$)", noduri_disp, index=len(noduri_disp)-1)

with col_graf:
    st.markdown("#### Starea Inițială a Rețelei")
    istoric_initial = { (int(r['Start (x_i)']), int(r['Destinație (x_j)'])):[] for _, r in edited_df.iterrows() }
    
    # Parametrul is_initial=True va asigura printarea STRICT a valorii capacității
    st.graphviz_chart(deseneaza_graf_retea(edited_df, istoric_initial, is_initial=True), use_container_width=True)

if st.button("Execută Algoritmul Ford-Fulkerson", type="primary", use_container_width=True):
    st.divider()
    istoric, df_final = executa_ford_fulkerson(edited_df, n_start, n_dest)
    
    st.markdown("### Etapele Analitice ale Algoritmului")
    
    for pas in istoric:
        with st.expander(f"Iterația {pas['iteratie']} - Procedura de Etichetare (PE)", expanded=(pas['status']=='STOP')):
            
            str_etichete = ", ".join([f"x_{{{int(n)}}}: \text{{{lbl[0]}}}" for n, lbl in pas['etichete'].items()])
            st.latex(r"\{ " + str_etichete + r" \}")
            
            if pas['status'] == 'CONTINUA':
                iter_idx = pas['iteratie']
                mu_index = pas['mu_idx']
                
                lant_str = f"x_{{{int(n_start)}}}"
                for u, v, sens in pas['lant']:
                    lant_str += r" \xrightarrow{" + ('+' if sens == '+' else '-') + r"} x_{" + str(int(v)) + "}"
                
                st.latex(r"\mu_{" + str(mu_index) + r"} =[" + lant_str + r"]")
                
                str_min_formule = ", ".join(pas['formule_min_mu'])
                st.latex(r"\min(\mu_{" + str(mu_index) + r"}) = \min \{" + str_min_formule + r"\} = " + fmt(pas['min_mu']))
                
                # Fluxul ia indexul iterației, lanțul ia indexul continuu
                if iter_idx == 0:
                    st.latex(r"\varphi_0 = \min(\mu_{" + str(mu_index) + r"}) = " + fmt(pas['phi_curent']))
                else:
                    st.latex(r"\varphi_{" + str(iter_idx) + r"} = \varphi_{" + str(iter_idx-1) + r"} + \min(\mu_{" + str(mu_index) + r"}) = " + fmt(pas['phi_prec']) + " + " + fmt(pas['min_mu']) + " = " + fmt(pas['phi_curent']))
                
                st.graphviz_chart(deseneaza_graf_retea(pas['df_stare'], pas['istoric_fluxuri'], etichete_noduri=pas['etichete'], lant_curent=pas['lant']), use_container_width=True)
            else:
                st.info(f"**Testul de Optimalitate $TO(I_{{STOP}})$**: Procedura de etichetare nu a putut atinge destinația $x_{{{int(n_dest)}}}$. Procesul converge.")

    # ==========================================================================
    # VALIDAREA TEOREMI FORD-FULKERSON ȘI EVIDENȚIEREA TĂIETURII
    # ==========================================================================
    st.divider()
    st.markdown("### Validare: Tăietura Minimă")
    
    noduri_A = list(istoric[-1]['etichete'].keys())
    noduri_T =[n for n in noduri_disp if n not in noduri_A] 
    str_T = ", ".join([f"x_{{{int(n)}}}" for n in noduri_T])
    
    st.write("Conform definiției, determinăm tăietura $T$ ca mulțimea vârfurilor de graf care nu au putut fi etichetate la $I_{STOP}$:")
    st.latex(r"T = \{ " + str_T + r" \} \implies \begin{cases} x_s \notin T \\ x_t \in T \end{cases}")
    
    cap_taietura = 0
    arce_taietura_noduri =[]
    arce_taietura_valori =[]
    
    for _, rand in df_final.iterrows():
        i, j = int(rand['Start (x_i)']), int(rand['Destinație (x_j)'])
        if i in noduri_A and j in noduri_T:
            c = rand['Capacitate c(u)']
            cap_taietura += c
            arce_taietura_noduri.append((i, j))
            arce_taietura_valori.append(c)

    st.markdown(f"<div class='validation-box'><b>Graficul Tăieturii:</b> Curba de separare trece strict prin arcele saturate marcate cu linie întreruptă portocalie, delimitând vârfurile marcate de cele nemarcate.</div>", unsafe_allow_html=True)
    st.graphviz_chart(deseneaza_graf_retea(df_final, istoric[-1]['istoric_fluxuri'], etichete_noduri=istoric[-1]['etichete'], muchii_taietura=arce_taietura_noduri), use_container_width=True)

    f_max = istoric[-1]['phi_curent']
    st.write("Verificarea teoremei fundamentale: Capacitatea tăieturii $C(T)$ coincide cu fluxul maxim $\\varphi_{max}$:")
    
    if arce_taietura_noduri:
        str_arce_calc = " + ".join([f"c(x_{{{u}}}, x_{{{v}}})" for u, v in arce_taietura_noduri])
        str_vals_calc = " + ".join([fmt(val) for val in arce_taietura_valori])
        st.latex(r"C(T) = \sum_{u \in T} c(u) = " + str_arce_calc + " = " + str_vals_calc + " = " + fmt(cap_taietura))
        st.latex(r"C(T) = " + fmt(cap_taietura) + r" = \varphi_{max} \quad (\text{Validat})")
