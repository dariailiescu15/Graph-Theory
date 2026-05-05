import streamlit as st
import pandas as pd
import graphviz

# ==============================================================================
# CONFIGURARE PAGINĂ ȘI STILURI CSS
# ==============================================================================
# Setăm titlul paginii și un layout extins pentru a avea loc de afișare a grafurilor
st.set_page_config(page_title="Algoritmul Ford-Fulkerson", layout="wide", page_icon="🌊")

# CSS personalizat pentru aspectul estetic (portocaliu pastel, profesional)
st.markdown("""
    <style>
    .title-box { background-color: #ffecd9; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
    .title-text { color: #e65c00; font-size: 50px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .subtitle-text { color: #cc5200; font-size: 24px; margin: 0; font-style: italic;}
    .authors-box { color: #cc5200; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #e65c00; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #cc5200; line-height: 1.6; font-size: 18px; }
    .info-box { background-color: #fff4ea; border-left: 5px solid #e65c00; padding: 15px; margin-bottom: 20px; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

def fmt(val):
    """
    Formatăm valorile pentru a arăta bine pe grafic și în LaTeX (fără zecimale .0 inutile).
    """
    if pd.isna(val): return "0"
    return str(int(val)) if float(val).is_integer() else f"{val:.2f}"

# ==============================================================================
# REPREZENTAREA GRAFICĂ (GRAPHVIZ)
# ==============================================================================
def deseneaza_graf_retea(arce_df, etichete_noduri=None, lant_curent=None):
    """
    Generăm vizualizarea grafului.
    Pentru Algoritmul Ford-Fulkerson, pe muchii vom afișa "flux / capacitate".
    Dacă avem etichete (procedura de marcare), le afișăm deasupra nodurilor.
    Dacă avem un lanț nesaturat găsit, îl evidențiem.
    """
    graf = graphviz.Digraph()
    graf.attr(rankdir='LR', bgcolor='transparent')
    
    # Nodurile standard
    graf.attr('node', shape='circle', style='filled', fillcolor='#ffecd9', color='#e65c00', fontcolor='#cc5200', fontname='Helvetica', penwidth='2')
    
    # Adunăm toate nodurile
    noduri = set(arce_df['Start (x_i)']).union(set(arce_df['Destinație (x_j)']))
    
    # Creăm nodurile și le atașăm etichetele dacă există
    for n in noduri:
        label = f"x{int(n)}"
        # Dacă nodul a primit o etichetă la etapa curentă, o scriem lângă el
        if etichete_noduri and n in etichete_noduri:
            eticheta_text = etichete_noduri[n]
            # Folosim un format HTML specific Graphviz pentru a afișa eticheta deasupra nodului
            label = f"<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='0'><TR><TD><FONT POINT-SIZE='10' COLOR='#e65c00'>{eticheta_text}</FONT></TD></TR><TR><TD>x{int(n)}</TD></TR></TABLE>>"
        
        # Colorăm diferit nodul dacă e vizitat (are etichetă)
        color_fill = '#ffcda8' if (etichete_noduri and n in etichete_noduri) else '#ffecd9'
        graf.node(str(int(n)), label, fillcolor=color_fill)
        
    # Extragem muchiile din lanțul curent (pentru a le îngroșa/colora)
    muchii_lant = set()
    if lant_curent:
        for u, v, dir in lant_curent:
            muchii_lant.add((str(int(u)), str(int(v))))
            
    # Adăugăm arcele (muchiile)
    for _, rand in arce_df.iterrows():
        i = str(int(rand['Start (x_i)']))
        j = str(int(rand['Destinație (x_j)']))
        c_ij = fmt(rand['Capacitate c(u)'])
        f_ij = fmt(rand['Flux f(u)'])
        
        label_arc = f"{f_ij} / {c_ij}"
        
        # Dacă arcul e în lanțul de augmentare curent
        if (i, j) in muchii_lant or (j, i) in muchii_lant:
            graf.edge(i, j, label=label_arc, color='#cc5200', penwidth='3.5', fontcolor='#cc5200', fontsize='14', fontname='Helvetica-bold')
        else:
            # Arcul este saturat dacă fluxul = capacitatea (îl colorăm gri, e complet)
            if float(rand['Flux f(u)']) == float(rand['Capacitate c(u)']):
                graf.edge(i, j, label=label_arc, color='#a0a0a0', penwidth='1.5', fontcolor='#606060')
            else:
                graf.edge(i, j, label=label_arc, color='#ffb380', penwidth='1.5', fontcolor='#888888')
            
    return graf

# ==============================================================================
# LOGICA MATEMATICĂ: ALGORITMUL FORD-FULKERSON
# ==============================================================================
def ford_fulkerson(df_arce, sursa, dest):
    """
    Funcția principală care rulează algoritmul Ford-Fulkerson complet.
    Explicatie: 
    Căutăm repetat un "lanț nesaturat" de la sursă la destinație folosind o căutare (Procedura de Marcare).
    Dacă găsim lanțul, calculăm valoarea alpha (rezerva minimă) și actualizăm fluxul.
    Dacă nu mai găsim niciun lanț, algoritmul se oprește (Flux Optim / Tăietură Minimă).
    """
    df = df_arce.copy() # Lucrăm pe o copie pentru a nu strica datele inițiale
    istoric =[]        # Aici salvăm starea la fiecare iterație pentru a o afișa pe UI
    
    iteratie = 1
    while True:
        # 1. PROCEDURA DE ETICHETARE (MARCARE) - O implementare de BFS (Breadth-First Search)
        # Dicționarul de etichete: nod -> (semn, parinte_string) pt afișare, ex: 2 -> ("+x1")
        etichete = {sursa: "[+]"}
        # Dicționar intern pentru a putea reconstitui drumul: nod -> (nod_parinte, sens) unde sens = '+' sau '-'
        parinti = {sursa: (None, None)} 
        
        coada = [sursa]
        dest_gasita = False
        
        # Exploram graful (căutăm un drum)
        while coada and not dest_gasita:
            nod_curent = coada.pop(0)
            
            # Căutăm vecini pe ARCE DIRECTE (nod_curent -> vecin)
            arce_directe = df[df['Start (x_i)'] == nod_curent]
            for _, rand in arce_directe.iterrows():
                vecin = rand['Destinație (x_j)']
                flux, cap = rand['Flux f(u)'], rand['Capacitate c(u)']
                
                # Regula 1: Daca vecinul e neetichetat si arcul nu e saturat (f < c) -> Etichetam cu [+x_i]
                if vecin not in etichete and flux < cap:
                    etichete[vecin] = f"[+x_{int(nod_curent)}]"
                    parinti[vecin] = (nod_curent, '+')
                    coada.append(vecin)
                    if vecin == dest:
                        dest_gasita = True
                        break
                        
            if dest_gasita: break
            
            # Căutăm vecini pe ARCE INVERSE (vecin -> nod_curent)
            arce_inverse = df[df['Destinație (x_j)'] == nod_curent]
            for _, rand in arce_inverse.iterrows():
                vecin = rand['Start (x_i)']
                flux = rand['Flux f(u)']
                
                # Regula 2: Daca vecinul e neetichetat si exista flux pe arc (f > 0) -> Etichetam cu [-x_i]
                if vecin not in etichete and flux > 0:
                    etichete[vecin] = f"[-x_{int(nod_curent)}]"
                    parinti[vecin] = (nod_curent, '-')
                    coada.append(vecin)
                    if vecin == dest:
                        dest_gasita = True
                        break

        # Dacă nu am putut eticheta destinația, algoritmul se oprește. Am găsit fluxul maxim!
        if not dest_gasita:
            istoric.append({
                'iteratie': iteratie,
                'status': 'STOP',
                'etichete': etichete,
                'df_stare': df.copy()
            })
            break
            
        # 2. RECONSTITUIREA LANȚULUI NESATURAT
        lant =[] # va conține tupluri (nod1, nod2, sens)
        curent = dest
        while curent != sursa:
            parinte, sens = parinti[curent]
            if sens == '+':
                lant.append((parinte, curent, '+'))
            else:
                lant.append((curent, parinte, '-')) # Arc invers
            curent = parinte
        lant.reverse() # Inversăm ca să fie de la Sursă -> Destinație
        
        # 3. CALCULUL REZERVEI (ALPHA)
        alphas =[]
        formule_alpha =[] # Pentru LaTeX
        for u, v, sens in lant:
            if sens == '+':
                # Pentru arc direct: alpha = c - f
                rand = df[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].iloc[0]
                rezerva = rand['Capacitate c(u)'] - rand['Flux f(u)']
                alphas.append(rezerva)
                formule_alpha.append(f"c(x_{int(u)}, x_{int(v)}) - f(x_{int(u)}, x_{int(v)}) = {fmt(rezerva)}")
            else:
                # Pentru arc invers: alpha = f
                rand = df[(df['Start (x_i)'] == curent) & (df['Destinație (x_j)'] == parinte)].iloc[0] # atentie u,v aici is pe dos
                rand = df[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].iloc[0]
                rezerva = rand['Flux f(u)']
                alphas.append(rezerva)
                formule_alpha.append(f"f(x_{int(u)}, x_{int(v)}) = {fmt(rezerva)}")
                
        alpha = min(alphas)
        
        # 4. ACTUALIZAREA FLUXULUI
        for u, v, sens in lant:
            idx = df.index[(df['Start (x_i)'] == u) & (df['Destinație (x_j)'] == v)].tolist()[0]
            if sens == '+':
                df.at[idx, 'Flux f(u)'] += alpha
            else:
                df.at[idx, 'Flux f(u)'] -= alpha
                
        # Salvăm iterația
        istoric.append({
            'iteratie': iteratie,
            'status': 'CONTINUA',
            'etichete': etichete,
            'lant': lant,
            'alpha': alpha,
            'formule_alpha': formule_alpha,
            'df_stare': df.copy()
        })
        
        iteratie += 1
        # Protecție pentru bucle infinite (în caz de inputuri ciudate)
        if iteratie > 50: 
            break
            
    return istoric, df

# ==============================================================================
# INTERFAȚA CU UTILIZATORUL (STREAMLIT)
# ==============================================================================
st.markdown('''
    <div class="title-box">
        <p class="title-text">🌊 Teoria Grafurilor 🔗</p>
        <p class="subtitle-text">Flux în Rețele: Algoritmul FORD-FULKERSON</p>
    </div>
''', unsafe_allow_html=True)

st.markdown('''
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

# Secționarea interfeței
col_tabel, col_graf = st.columns([1, 1.2])

with col_tabel:
    st.markdown("<h3 style='color: #e65c00;'>📝 1. Structura Rețelei $G = (X, U)$</h3>", unsafe_allow_html=True)
    st.write("Introduceți arcele grafului, capacitatea $c(u)$ și un flux inițial $f_0 \in \mathcal{F}$ (de obicei 0).")

    # Date implicite - un mic exemplu generic pentru rețele
    if "tabel_retea" not in st.session_state:
        # Structura: Nod_i, Nod_j, Capacitate, Flux_initial
        date_initiale = [
            [1, 2, 10, 0],[1, 3, 10, 0], 
            [2, 3, 2, 0],[2, 4, 4, 0], [2, 5, 8, 0],
            [3, 5, 9, 0],[4, 6, 10, 0], 
            [5, 4, 6, 0],[5, 6, 10, 0]
        ]
        df_initial = pd.DataFrame(date_initiale, columns=["Start (x_i)", "Destinație (x_j)", "Capacitate c(u)", "Flux f(u)"])
        st.session_state.tabel_retea = df_initial

    edited_df = st.data_editor(
        st.session_state.tabel_retea, 
        num_rows="dynamic",
        use_container_width=True,
        key="editor_retea"
    )

with col_graf:
    st.markdown("<h3 style='color: #e65c00;'>🌍 Graful Inițial</h3>", unsafe_allow_html=True)
    graf_initial = deseneaza_graf_retea(edited_df)
    st.graphviz_chart(graf_initial, use_container_width=True)

# Setările algoritmului (Sursă și Destinație)
noduri_disponibile = sorted(list(set(edited_df['Start (x_i)']).union(set(edited_df['Destinație (x_j)']))))
if len(noduri_disponibile) > 0:
    st.markdown("### 📍 Parametrii Problemei")
    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        nod_start = st.selectbox("Nodul Sursă ($x_s$)", noduri_disponibile, index=0)
    with c2:
        nod_dest = st.selectbox("Nodul Destinație ($x_t$)", noduri_disponibile, index=len(noduri_disponibile)-1)

# Validare matematică de bază
eroare = False
for _, rand in edited_df.iterrows():
    if rand['Flux f(u)'] > rand['Capacitate c(u)']:
        st.error(f"Eroare: Fluxul depășește capacitatea pe arcul ({int(rand['Start (x_i)'])} -> {int(rand['Destinație (x_j)'])}). $f(u) \le c(u)$ este o condiție obligatorie!")
        eroare = True

# Rularea algoritmului la apăsarea butonului
if st.button("🚀 Determină Fluxul Maxim", type="primary", use_container_width=True) and not eroare:
    st.divider()
    
    st.markdown("<h3 style='color: #e65c00;'>⚙️ 2. Algoritmul Ford-Fulkerson (Etapele de etichetare)</h3>", unsafe_allow_html=True)
    
    istoric, df_final = ford_fulkerson(edited_df, nod_start, nod_dest)
    
    # Afișarea iterativă a pașilor algoritmului
    for pas in istoric:
        with st.expander(f"🟡 Iterația {pas['iteratie']}: Procedura de etichetare", expanded=(pas['status']=='STOP')):
            
            # Afișăm setul de etichete obținut
            str_etichete = ", ".join([f"x_{{{int(n)}}}: \text{{{lbl}}}" for n, lbl in pas['etichete'].items()])
            st.latex(r"\text{Marcaje obținute: } \{ " + str_etichete + r" \}")
            
            if pas['status'] == 'CONTINUA':
                # Am găsit un drum
                lant_str = f"x_{{{int(nod_start)}}}"
                for u, v, sens in pas['lant']:
                    s = "+" if sens == '+' else "-"
                    lant_str += rf" \xrightarrow{{{s}}} x_{{{int(v)}}}"
                
                st.write("**1. S-a identificat lanțul nesaturat de la sursă la destinație:**")
                st.latex(rf"\mu = [{lant_str}]")
                
                st.write("**2. Se calculează cantitatea de flux cu care putem suplimenta ($\\alpha$):**")
                formule_str = r" \\ ".join(pas['formule_alpha'])
                st.latex(rf"\alpha = \min \begin{{cases}} {formule_str} \end{{cases}} = {fmt(pas['alpha'])}")
                
                st.write("**3. Se actualizează fluxul pe rețea:**")
                st.latex(r"f'(u) = \begin{cases} f(u) + \alpha, & \text{dacă } u \in \mu^+ \\ f(u) - \alpha, & \text{dacă } u \in \mu^- \\ f(u), & \text{în rest} \end{cases}")
                
                # Desenăm graful specific iterației
                graf_iter = deseneaza_graf_retea(pas['df_stare'], etichete_noduri=pas['etichete'], lant_curent=pas['lant'])
                st.graphviz_chart(graf_iter, use_container_width=True)
                
            else:
                # Condiția de STOP
                st.success(f"**Testul de optimalitate:** Destinația $x_{{{int(nod_dest)}}}$ nu a mai putut fi etichetată. Algoritmul STOP.")
                graf_iter = deseneaza_graf_retea(pas['df_stare'], etichete_noduri=pas['etichete'])
                st.graphviz_chart(graf_iter, use_container_width=True)

    # --------------------------------------------------------------------------
    # CONCLUZIA MATEMATICĂ ȘI TĂIETURA MINIMĂ
    # --------------------------------------------------------------------------
    st.divider()
    st.markdown("<h3 style='color: #e65c00;'>🏆 3. Soluția Optimă & Tăietura Minimă</h3>", unsafe_allow_html=True)
    
    # Valoarea fluxului maxim = Suma fluxurilor de pe arcele care ies din Sursă MINUS suma celor care intră în Sursă
    flux_iesire_sursa = df_final[df_final['Start (x_i)'] == nod_start]['Flux f(u)'].sum()
    flux_intrare_sursa = df_final[df_final['Destinație (x_j)'] == nod_start]['Flux f(u)'].sum()
    valoare_flux_maxim = flux_iesire_sursa - flux_intrare_sursa
    
    # Determinarea Tăieturii (Mulțimea A = noduri etichetate la pasul STOP, Mulțimea X\A = restul)
    noduri_A = list(istoric[-1]['etichete'].keys())
    noduri_X_A = [n for n in noduri_disponibile if n not in noduri_A]
    
    # Calculăm Capacitatea Tăieturii: suma capacităților arcelor care ies din A și intră în X\A
    capacitate_taietura = 0
    arce_taietura =[]
    for _, rand in df_final.iterrows():
        i, j = rand['Start (x_i)'], rand['Destinație (x_j)']
        if i in noduri_A and j in noduri_X_A:
            capacitate_taietura += rand['Capacitate c(u)']
            arce_taietura.append(f"c(x_{int(i)}, x_{int(j)})")
            
    # Afișarea soluțiilor în limbaj matematic LaTeX
    col_rez1, col_rez2 = st.columns(2)
    
    with col_rez1:
        st.markdown('''
            <div class="info-box">
                <h4 style="color:#e65c00; margin-top:0;">🌟 Fluxul Maxim</h4>
                Fluxul este considerat complet când niciun lanț de la sursă la destinație nu mai poate fi nesaturat.
            </div>
        ''', unsafe_allow_html=True)
        st.latex(rf"V(f_{{max}}) = {fmt(valoare_flux_maxim)}")
        
    with col_rez2:
        st.markdown('''
            <div class="info-box">
                <h4 style="color:#e65c00; margin-top:0;">✂️ Tăietura Minimă</h4>
                Conform Teoremei Ford-Fulkerson, valoarea maximă a fluxului coincide cu capacitatea minimă a tăieturilor sale.
            </div>
        ''', unsafe_allow_html=True)
        
        str_A = ", ".join([f"x_{int(n)}" for n in noduri_A])
        str_XA = ", ".join([f"x_{int(n)}" for n in noduri_X_A])
        st.latex(rf"A = \{{{str_A}\}} \quad ; \quad X \setminus A = \{{{str_XA}\}}")
        
        if arce_taietura:
            str_arce_calc = " + ".join(arce_taietura)
            st.latex(rf"C(\mu_A^-) = {str_arce_calc} = {fmt(capacitate_taietura)}")
            
            # Verificarea fundamentală a teoremei
            if abs(valoare_flux_maxim - capacitate_taietura) < 1e-9:
                st.success(r"**Teorema se verifică!** $V(f) = C(\mu_A^-) \Rightarrow \text{Fluxul este matematic optim.}$")
            else:
                st.warning("Verificarea teoremei nu a reușit. Posibil să existe un arc cu flux inițial negativ sau o excepție matematică în graf.")
