import tkinter as tk  #Llibreria per crear gràfics a Python.
from tkinter import filedialog, messagebox, simpledialog, ttk
from airport import * #Importar el document airport.py
from aircraft import * #importar el document aircraft.py
from LEBL import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from tkintermapview import TkinterMapView
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#FUNCIONALITAT EXTRA
def reproducir_gif(ruta_gif, titulo="Operació en curs"):
    try:
        #Obrim el GIF amb Pillow
        img_original = Image.open(ruta_gif)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No s'ha trobat el fitxer: {ruta_gif}")
        return

    #Crear una finestra flotant pel GIF
    ventana_gif = tk.Toplevel()
    ventana_gif.title(titulo)
    ventana_gif.geometry("500x320")
    ventana_gif.resizable(False, False)

    lbl_gif = tk.Label(ventana_gif)
    lbl_gif.pack(expand=True, fill="both")

    #Extreure tots els fotgogrames del GIF, i convertir-los al format Tkinter
    frames = []
    try:
        while True:
            #Convertim el fotograma actual i el guardem
            frame_tk = ImageTk.PhotoImage(img_original.copy().convert("RGBA"))
            frames.append(frame_tk)
            #Avancem al següent fotograma
            img_original.seek(img_original.tell() + 1)
    except EOFError:
        pass

    def actualizar_frame(num_frame):
        if ventana_gif.winfo_exists():  # Comprovem si la finestra segueix oberta
            frame = frames[num_frame]
            lbl_gif.configure(image=frame)
            # 40 milisegons per fotograma
            ventana_gif.after(40, actualizar_frame, (num_frame + 1) % len(frames))

    #Iniciem l'animació des del primer fotograma
    actualizar_frame(0)

    #Tanquem automàticament la finestra després de 4 segons (4000 ms)
    ventana_gif.after(4000, ventana_gif.destroy)

#Llista global on guardarem els aeroports a la memòria del programa.
llista_aeroports=[]
llista_avions=[]
bcn_airport=""
llista_sortides=[]
llista_moviments=[]

def carregar_fitxer():#Obre una finestra perquè l'usuari triï el fitxer.txt, per actualitzar també el boleà Schengen,
    # i per poder modificar la llista "global llista_aeroports".
    global llista_aeroports
    nom_fitxer = filedialog.askopenfilename(title="Selecciona l'arxiu d'aeroports", filetypes=[("Text files", "*.txt")])
    if nom_fitxer != "":
        llista_aeroports, errors = LoadAirports(nom_fitxer)
        mostrar_fitxer(nom_fitxer)
        if len(llista_aeroports) == 0:
            messagebox.showwarning("Avís", "No s'ha carregat cap aeroport vàlid.")
        else:
            messagebox.showinfo("Resultat",f"Aeroports carregats: {len(llista_aeroports)}\nLínies incorrectes: {len(errors)}")


def set_schengen():
    i=0
    while i<len(llista_aeroports):
        SetSchengen(llista_aeroports[i])
        i=i+1
    missatge = "S'han configurat els atributs Schengen dels aeroports correctament."
    messagebox.showinfo("Èxit", missatge)

def mostrar_dades():
    if len(llista_aeroports)==0:
        messagebox.showwarning("Avís", "Primer has de carregar els aeroports.")
        return

    #Crea finestra nova
    win = tk.Toplevel()
    win.title("Llista aeroports")

    #Treeview amb 3 columnes
    cols = ("num", "code", "lat", "lon", "sch")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=8)
    tree.pack(side="left", expand=True, fill="both")

    #Capçaleres
    tree.heading("num", text="Posició")
    tree.heading("code", text="ICAO")
    tree.heading("lat", text="Latitud")
    tree.heading("lon", text="Longitud")
    tree.heading("sch", text="Schengen")

    #Columnes
    tree.column("num", width=80)
    tree.column("code", width=80)
    tree.column("lat", width=150)
    tree.column("lon", width=150)
    tree.column("sch", width=80)

    #Omplir dades dels aeroports
    i = 0
    while i<len(llista_aeroports):
        aeroport = llista_aeroports[i]
        tree.insert("", "end", values=(i+1, aeroport.ICAO, aeroport.latitud, aeroport.longitud, aeroport.Schengen))
        i += 1

def desar_schengen():#Es fa una comprovació de que es tinguin dades. A continuació, obre una nova finestra i crida a la
    # funció "SaveSchengenAirports".
    if len(llista_aeroports) == 0:
        messagebox.showwarning("Avís", "No hi ha aeroports carregats per desar.")
        return
    nom_fitxer = filedialog.asksaveasfilename(defaultextension=".txt", title="Desar aeroports Schengen")

    if nom_fitxer != "":
        resultat = SaveSchengenAirports(llista_aeroports, nom_fitxer)
        if resultat == 0:
            messagebox.showinfo("Èxit", "Fitxer desat correctament.")
        else:
            messagebox.showinfo("Error", "No s'ha pogut desar cap fitxer.")
    else:
        messagebox.showinfo("Error", "No s'ha seleccionat cap fitxer.")

def afegir_aeroport():#Et demana ICAO i coordenades de l'aeroport, crea un objecte "Aeroport", comprova el boleà
    # Schengen, i l'afageix a la llista.
    codi = simpledialog.askstring("Nou Aeroport", "Introdueix el codi ICAO (ex: LEBL):")
    if not codi:#Si l'usuari cancel·la.
        return

    lat = simpledialog.askstring("Nou Aeroport", "Introdueix la latitud en graus decimals (ex: 41.29):")
    lon = simpledialog.askstring("Nou Aeroport", "Introdueix la longitud en graus decimals (ex: 2.08):")

    if lat and lon:
        nou_aero = Airport(codi, float(lat), float(lon))
        resultat = AddAirport(llista_aeroports, nou_aero)
        if resultat == -1:
            messagebox.showerror("Error", "El codi ICAO no és vàlid (ha de tenir 4 lletres).")
        elif resultat == -2:
            messagebox.showwarning("Avís", "Aquest aeroport ja existeix.")
        else:
            SetSchengen(nou_aero)
            messagebox.showinfo("Èxit", "Aeroport afegit correctament.")


def eliminar_aeroport():#Demana codi ICAO, i l'esborra de la llista mitjançant la funció definida anteriorment en
    # el mateix codi.
    codi = simpledialog.askstring("Eliminar Aeroport", "Introdueix el codi ICAO a eliminar:")
    if codi:
        resultat = RemoveAirport(llista_aeroports, codi.upper())
        if resultat== 0:
            messagebox.showinfo("Èxit", "Aeroport eliminat correctament.")
        else:
            messagebox.showerror("Error", "No s'ha trobat cap aeroport amb aquest codi.")

def mostrar_grafic():#Comprova que hi ha dades carregades i, en el cas afirmatiu, carrega el gràfic.
    if len(llista_aeroports) > 0:
        fig = PlotAirports(llista_aeroports)
        mostrar_plot(fig)
    else:
        messagebox.showwarning("Avís", "Primer has de carregar els aeroports.")

def mostrar_mapa_google_earth():#Comprova que hi ha dades carregades i, en el cas afirmatiu, carrega el mapa.
    if len(llista_aeroports) > 0:
        MapAirports(llista_aeroports)
    else:
        messagebox.showwarning("Avís", "Primer has de carregar els aeroports.")

def mostrar_mapa_interactiu():
    if len(llista_aeroports)==0:
        messagebox.showwarning("Avís", "Primer has de carregar els aeroports.")
        return

    # Netejar mapa
    map_widget.delete_all_marker()
    i=0
    while i<len(llista_aeroports):
        aeroport=llista_aeroports[i]
        if aeroport.Schengen == True:
            color = "blue"
        else:
            color = "red"

        map_widget.set_marker(aeroport.latitud, aeroport.longitud, text=aeroport.ICAO, marker_color_circle=color, marker_color_outside=color)
        i+=1

def carregar_vols():#Permet obtenir el llistat de vols a partir d'un document .txt per posteriorment analitzar-lo
    global llista_avions
    nom_fitxer = filedialog.askopenfilename(title="Selecciona l'arxiu d'arribades",filetypes=[("Text files", "*.txt")])

    if nom_fitxer != "":
        llista_avions, errors=LoadArrivals(nom_fitxer)
        mostrar_fitxer(nom_fitxer)
        messagebox.showinfo("Resultat", f"Arrivades carregades: {len(llista_avions)}\nErrors no processats: {len(errors)}")

def mostrar_grafic_arribades():#Mostra la freqüència d'arribades per cada hora del dia a LEBL en un gràfic de barres
    if len(llista_avions) > 0:
        fig = PlotArrivals(llista_avions)
        mostrar_plot(fig)
    else:
        messagebox.showwarning("Avís", "Primer s'han de carregar els vols.")

def mostrar_grafic_aerolinies():#Mostra el numero de vols per cada aerolínia
    if len(llista_avions) > 0:
        fig = PlotAirlines(llista_avions)
        mostrar_plot(fig)
    else:
        messagebox.showwarning("Avís", "Primer has de carregar els vols.")

def mostrar_tipus_vols():#Indica els vols que provenen de l'espai schengen i els que no en un gràfic de barres
    if len(llista_avions) > 0:
        fig = PlotFlightsType(llista_avions)
        mostrar_plot(fig)
    else:
        messagebox.showwarning("Avís", "Primer s'han de carregar els vols.")

def desar_vols():#Permet abocar la llista de vols a un fitxer
    if len(llista_avions)==0:
        messagebox.showwarning("Avís","No hi ha vols")
        return
    nom_fitxer=filedialog.asksaveasfilename(defaultextension=".txt")
    if nom_fitxer !="":
        SaveFlights(llista_avions, nom_fitxer)
        messagebox.showinfo("Èxit","Fitxer desat correctament")
    else:
        messagebox.showinfo("Error", "No s'ha seleccionat cap fitxer.")

def mostrar_mapa_vols_google_earth():#Representa els vols a Google Earth
    if len(llista_avions) > 0 and len(llista_aeroports) > 0:
        MapFlights(llista_avions, llista_aeroports)
    else:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")

def mostrar_mapa_vols_llargs_google_earth(): # Nova funció pont per a llarga distància
    if len(llista_avions) > 0 and len(llista_aeroports) > 0:
        MapLongDistanceFlights(llista_avions, llista_aeroports)
    else:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")

def mostrar_mapa_interactiu_vols():
    if len(llista_avions)==0 or len(llista_aeroports)==0:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")
        return

    map_widget.delete_all_path()
    map_widget.delete_all_marker()

    lat_lebl=41.2974
    lon_lebl=2.0833

    # marcador LEBL
    map_widget.set_marker(lat_lebl, lon_lebl, text="LEBL")

    i=0
    while i<len(llista_avions):
        origen=llista_avions[i].airport_origin
        j=0
        encontrado=False
        while j<len(llista_aeroports) and not encontrado:
            if llista_aeroports[j].ICAO==origen:
                lat=llista_aeroports[j].latitud
                lon=llista_aeroports[j].longitud

                # marcador origen
                map_widget.set_marker(lat, lon, text=origen)

                # línia del vol
                schengen_list = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI',
                                 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
                prefix = origen[:2]
                if prefix in schengen_list:
                    color_linia = "green"
                else:
                    color_linia = "red"
                # Crear línia fina
                map_widget.set_path([(lat, lon),(lat_lebl, lon_lebl)], width=1, color=color_linia)
                encontrado=True
            j+=1
        i+=1

def mostrar_vols_llargs():#mostra en una llista els aeroports que es troben a més de 2000km de l'aeroport de Barcelona
    if len(llista_avions) == 0 or len(llista_aeroports) == 0:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")
        return

    llista_llargs = LongDistanceArrivals(llista_avions, llista_aeroports)

    win = tk.Toplevel()
    win.title("Vols llarga distància (>2000 km)")

    cols = ("num", "avio", "origen", "hora", "companyia")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    tree.pack(expand=True, fill="both")

    tree.heading("num", text="Posició")
    tree.heading("avio", text="Avió")
    tree.heading("origen", text="Origen")
    tree.heading("hora", text="Hora")
    tree.heading("companyia", text="Companyia")

    i=0
    while i<len(llista_llargs):
        avio=llista_llargs[i]
        tree.insert("", "end", values=(i+1, avio.aircraft_id, avio.airport_origin, avio.land_time, avio.company))
        i=i+1
    messagebox.showinfo("Info", "Hi ha " + str(len(llista_llargs)) + " vols de llarga distància.")

def mostrar_mapa_interactiu_vols_llargs():
    if len(llista_avions)==0 or len(llista_aeroports)==0:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")
        return

    vols_llargs=LongDistanceArrivals(llista_avions, llista_aeroports)

    map_widget.delete_all_path()
    map_widget.delete_all_marker()

    lat_lebl=41.2974
    lon_lebl=2.0833
    map_widget.set_marker(lat_lebl, lon_lebl, text="LEBL") # Marcador de Barcelona

    i=0
    while i<len(vols_llargs):
        origen=vols_llargs[i].airport_origin
        j=0
        encontrado=False
        while j<len(llista_aeroports) and not encontrado:
            if llista_aeroports[j].ICAO==origen:
                lat=llista_aeroports[j].latitud
                lon=llista_aeroports[j].longitud
                map_widget.set_marker(lat, lon, text=origen)

                # Vols llargs en color taronja
                map_widget.set_path([(lat, lon), (lat_lebl, lon_lebl)], width=2, color="orange")

                encontrado=True
            j+=1
        i+=1
    messagebox.showinfo("Info", f"Mostrant {len(vols_llargs)} vols de llarga distància.")

def carregar_sortides():
    global llista_sortides
    nom_fitxer=filedialog.askopenfilename(title="Selecciona l'arxiu de sortides", filetypes=[("Text files", "*.txt")])
    if nom_fitxer != "":
        llista_sortides, errors=LoadDepartures(nom_fitxer)
        mostrar_fitxer(nom_fitxer)
        missatge="S'han carregat "+ str(len(llista_sortides))+" sortides."
        messagebox.showinfo("Resultat", f"Sortides carregades: {len(llista_sortides)}\nErrors no processats: {len(errors)}")

def fusionar_moviments():
    global llista_moviments
    if len(llista_avions)==0:
        messagebox.showwarning("Avís", "Primer carrega les arribades.")
        return
    if len(llista_sortides)==0:
        messagebox.showwarning("Avís", "Primer carrega les sortides.")
        return

    llista_moviments=MergeMovements(llista_avions, llista_sortides)
    if llista_moviments==-1:
        messagebox.showerror("Error", "No s'han pogut fusionar els moviments.")
    else:
        messagebox.showinfo("Èxit", "S'han fusionat " + str(len(llista_moviments)) + " moviments.")

def mostrar_avions_nit():
    if len(llista_moviments)==0:
        messagebox.showwarning("Avís","Primer fusiona arribades i sortides.")
        return

    avions_nit = NightAircraft(llista_moviments)
    if avions_nit==-1 or len(avions_nit)==0:
        messagebox.showinfo("Info","No hi ha avions nocturns.")
        return

    win=tk.Toplevel()
    win.title("Avions nocturns")

    cols=("num", "avio", "destinacio", "sortida", "companyia")

    tree=ttk.Treeview(win, columns=cols, show="headings")
    tree.pack(expand=True, fill="both")

    tree.heading("num", text="Posició")
    tree.heading("avio", text="Avió")
    tree.heading("destinacio", text="Destinació")
    tree.heading("sortida", text="Hora sortida")
    tree.heading("companyia", text="Companyia")

    i=0
    while i<len(avions_nit):
        avio=avions_nit[i]
        tree.insert("", "end", values=(i+1, avio.aircraft_id, avio.destination_airport, avio.departure_time,
                                       avio.company))
        i+=1

    messagebox.showinfo("Info", "Hi ha " + str(len(avions_nit)) + " avions nocturns.")

def carregar_estructura_lebl():
    global bcn_airport
    nom_fitxer = filedialog.askopenfilename(title="Selecciona l'arxiu LEBL",filetypes=[("Text files", "*.txt")])

    if nom_fitxer != "":
        bcn_airport,errors = LoadAirportStructure(nom_fitxer)

        mostrar_fitxer(nom_fitxer)

        if bcn_airport == -1:
            messagebox.showerror("Error", "No s'ha pogut carregar l'estructura.")
        else:
            messagebox.showinfo("Èxit","Estructura de l'aeroport carregada correctament.")
        if errors:
            messagebox.showwarning("Errors detectats","\n".join(errors))

def mostrar_ocupacio_portes():

    if bcn_airport=="":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return

    dades = GateOccupancy(bcn_airport)

    win = tk.Toplevel()
    win.title("Ocupació de portes")

    cols = ("porta", "estat", "avio")

    tree = ttk.Treeview(win, columns=cols, show="headings")
    tree.pack(expand=True, fill="both")

    tree.heading("porta", text="Porta")
    tree.heading("estat", text="Estat")
    tree.heading("avio", text="Avió")

    i=0
    while i<len(dades):
        tree.insert("", "end", values=(dades[i][0], dades[i][1], dades[i][2]))
        i=i+1

def buscar_terminal():

    if bcn_airport=="":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return
    aerolinia = simpledialog.askstring("Buscar terminal","Introdueix el codi ICAO de l'aerolínia:")
    if aerolinia:
        terminal = SearchTerminal(bcn_airport, aerolinia.upper())
        if terminal != "":
            messagebox.showinfo("Terminal trobada","L'aerolínia opera a la terminal " + terminal)
        else:
            messagebox.showwarning("No trobada","No existeix cap terminal per aquesta aerolínia.")

def assignar_porta():
    global bcn_airport
    if bcn_airport =="":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return
    if len(llista_avions) == 0:
        messagebox.showwarning("Avís", "Primer carrega els vols.")
        return

    aircraft_id = simpledialog.askstring("Assignar porta","Introdueix el codi de l'avió:")
    if not aircraft_id:
        return
    trobat = False
    avio_trobat=""
    i=0
    while i<len(llista_avions) and not trobat:
        if llista_avions[i].aircraft_id==aircraft_id:
            avio_trobat=llista_avions[i]
            trobat=True
        i=i+1
    if not trobat:
        messagebox.showerror("Error", "No s'ha trobat aquest avió.")
        return
    porta = AssignGate(bcn_airport, avio_trobat)
    if porta == -1:
        messagebox.showwarning("Sense portes","No hi ha portes disponibles.")
    else:
        #FUNCIONALITAT EXTRA
        messagebox.showinfo("Porta assignada", "L'avió s'ha assignat a la porta " + porta)
        reproducir_gif("landing.gif", titulo="Avió acoblant-se a la porta (Safran)")

def alliberar_porta():
    global bcn_airport
    if bcn_airport=="":
        messagebox.showwarning("Avís","Primer carrega l'estructura LEBL.")
        return
    aircraft_id = simpledialog.askstring("Assignar porta","introdueix el codi de l'avió")
    if not aircraft_id:
        return
    resultat=FreeGate(bcn_airport,aircraft_id)
    if resultat == 0:
        #FUNCIONALITAT EXTRA
        messagebox.showinfo("Èxit","La porta s'ha alliberat correctament")
        reproducir_gif("takeoff.gif", titulo="Avió enlairant-se (Airbus)")
    else:
        messagebox.showerror("Error", "No s'ha trobat aquest avió a cap porta")

def assignar_portes_nit():

    global bcn_airport

    if bcn_airport == "":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return

    if len(llista_moviments) == 0:
        messagebox.showwarning("Avís", "Primer fusiona arribades i sortides.")
        return
    avions_nit = NightAircraft(llista_moviments)
    resultat = AssignNightGates(bcn_airport,avions_nit)

    if resultat == -1:
        messagebox.showerror("Error","No hi ha avions nocturns.")
    else:
        messagebox.showinfo("Èxit","Avions nocturns assignats correctament.")

def mostrar_ocupacio_dia():

    if bcn_airport == "":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return

    if len(llista_moviments) == 0:
        messagebox.showwarning("Avís","Primer fusiona arribades i sortides.")
        return

    fig = PlotDayOccupancy(bcn_airport,llista_moviments)
    mostrar_plot(fig)

def assignar_portes_hora():
    global bcn_airport
    if bcn_airport == "":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return
    if len(llista_moviments) == 0:
        messagebox.showwarning("Avís", "Primer fusiona arribades i sortides.")
        return

    hora = simpledialog.askstring("Simulació horària","Introdueix una hora (format HH:MM)")
    if not hora:
        return
    try:
        resultat,recompte = AssignGatesAtTime(bcn_airport,llista_moviments,hora)
        messagebox.showinfo("Simulació completada",
            f"Avions no assignats: {recompte}")

        # Actualitzar mapa gràfic de portes
        PlotLEBLGates(bcn_airport)

    except:
        messagebox.showerror("Error","Format d'hora incorrecte.")

def comptar_sortides_interval():
    if len(llista_sortides) == 0:
        messagebox.showwarning("Avís", "Primer carrega les sortides.")
        return

    try:
        hora_inici = int(entry_hora_inici.get())
        hora_fi = int(entry_hora_fi.get())

        if hora_inici < 0 or hora_inici > 23 or hora_fi < 0 or hora_fi > 23:
            messagebox.showerror("Error", "Les hores han d'estar entre 0 i 23.")
            return
        comptador = 0
        i = 0
        while i < len(llista_sortides):
            hora_vol = int(llista_sortides[i].departure_time[:2])
            if hora_inici <= hora_vol <= hora_fi:
                comptador += 1
            i += 1
        messagebox.showinfo("Resultat",f"Hi ha {comptador} vols previstos entre les {hora_inici:02d}:00 i les {hora_fi:02d}:59")
    except ValueError:
        messagebox.showerror("Error", "Introdueix hores vàlides (0-23).")

def comptar_avions_aerolinia():
    global bcn_airport
    global llista_moviments
    if bcn_airport == "":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return

    codi = entrada_aerolinia.get().strip().upper()
    if len(codi) != 3:
        messagebox.showwarning("Avís","El codi de l'aerolínia ha de tenir exactament 3 caràcters.")
        return
    if codi == "":
        messagebox.showwarning("Avís", "Introdueix un codi d'aerolínia.")
        return

    existeix=False
    i=0
    while i<len(bcn_airport.terminals) and not existeix:
        terminal = bcn_airport.terminals[i]
        if IsAirlineInTerminal(terminal, codi):
            existeix = True
        i+=1
    if not existeix:
        messagebox.showerror("Error",f"L'aerolínia '{codi}' no existeix a l'estructura carregada de LEBL.")
        return
    comptador=0
    i=0
    while i<len(bcn_airport.terminals):
        terminal=bcn_airport.terminals[i]
        j=0
        while j<len(terminal.boarding_areas):
            area=terminal.boarding_areas[j]
            k=0
            while k<len(area.gates):
                gate=area.gates[k]
                if gate.occupied:
                    aircraft_id = gate.aircraft_id
                    x = 0
                    trobat = False
                    while x < len(llista_moviments) and not trobat:
                        if llista_moviments[x].aircraft_id==aircraft_id:
                            if llista_moviments[x].company.upper() == codi:
                                comptador+=1
                            trobat=True
                        x+=1
                k+=1
            j+=1
        i+=1
    messagebox.showinfo("Resultat",f"L'aerolínia {codi} té actualment {comptador} avió(ns) ocupant una porta.")

def mostrar_mapa_portes():
    global bcn_airport
    if bcn_airport == "":
        messagebox.showwarning("Avís","Primer carrega l'estructura LEBL.")
        return
    PlotLEBLGates(bcn_airport)

def actualizar_mapa_puertas(terminal_seleccionada):
    global bcn_airport
    # Validación por si el objeto bcn_airport todavía no se ha inicializado o cargado
    if not bcn_airport or bcn_airport == -1 or bcn_airport == "":
        # Intentamos cargarlo si tienes el archivo por defecto 'LEBL.txt'
        bcn_airport = LoadAirportStructure("LEBL.txt")

    if bcn_airport and bcn_airport != -1:
        # Llama a la nueva función optimizada pasándole la terminal elegida
        PlotLEBLGates(bcn_airport, terminal_filtro=terminal_seleccionada)
    else:
        messagebox.showwarning("Aviso", "No se ha podido cargar la estructura del aeropuerto LEBL.txt")

def mostrar_fitxer(path_fitxer):
    try:
        F = open(path_fitxer, "r")
        contingut = F.read()
        visor_fitxers.delete("1.0", tk.END)
        visor_fitxers.insert(tk.END, contingut)
        F.close()

    except FileNotFoundError:
        messagebox.showerror("Error", "No s'ha pogut obrir el fitxer.")

def mostrar_plot(figura):
    global canvas_plot
    if canvas_plot is not None:
        canvas_plot.get_tk_widget().destroy()
    canvas_plot = FigureCanvasTkAgg(figura, master=plot_inner_frame)
    widget = canvas_plot.get_tk_widget()
    widget.pack(fill="both", expand=True)
    canvas_plot.draw()
    plot_inner_frame.update_idletasks()

#Paleta de colors
COLOR_FONS = "#EEF3F7"
COLOR_FRAME = "#DCE7F0"
COLOR_BOTO = "#5E81AC"
COLOR_BOTO_HOVER = "#4C6F99"
COLOR_TEXT = "#1F2937"
COLOR_TITOL = "#3B5875"

#Creació de la finestra a la interfície principal.
finestra = tk.Tk()
finestra.configure(bg=COLOR_FONS)
finestra.title("Gestor d'Aeroports")#Títol de la finestra.
finestra.geometry("1400x800")#Mida de la finestra.
finestra.minsize(1200, 750)

#Etiqueta de títol.
titol = tk.Label(finestra,text="Gestor d'Aeroports",font=("Segoe UI", 18, "bold"),fg=COLOR_TITOL,bg=COLOR_FONS)
titol.grid(row=0,column=0,pady=10)

#Finestres de les columnes de la interfaç.
finestra.columnconfigure(0, weight=0)
finestra.columnconfigure(1, weight=0)
finestra.columnconfigure(2, weight=0)

# Zona central expansible
finestra.columnconfigure(3, weight=1)

# Files
finestra.rowconfigure(0, weight=1)
finestra.rowconfigure(0,weight=1)
finestra.rowconfigure(1,weight=3)

# FRAME PRINCIPAL CENTRAL
main_content = tk.Frame(finestra,bg=COLOR_FONS)
main_content.grid(row=0, column=3, rowspan=2,padx=8, pady=8,sticky="nsew")
main_content.columnconfigure(0, weight=1)

# visor dades
main_content.rowconfigure(0, weight=2)

# plots futurs
main_content.rowconfigure(1, weight=2)

# mapa
main_content.rowconfigure(2, weight=3)

airport_frame = tk.LabelFrame(finestra,text="AIRPORT",padx=6,pady=6)
airport_frame.grid(row=0,column=0,padx=5,pady=5,sticky="ns")
airport_data_frame = tk.LabelFrame(airport_frame,text="Gestió Aeroports")
airport_data_frame.pack(fill="x", pady=4)
airport_visual_frame = tk.LabelFrame(airport_frame,text="Visualització")
airport_visual_frame.pack(fill="x", pady=4)

aircraft_frame = tk.LabelFrame(finestra,text="AIRCRAFT",padx=6,pady=6)
aircraft_frame.grid(row=0,column=1,padx=5,pady=5,sticky="ns")
aircraft_data_frame = tk.LabelFrame(aircraft_frame,text="Gestió Vols")
aircraft_data_frame.pack(fill="x", pady=4)
aircraft_analysis_frame = tk.LabelFrame(aircraft_frame,text="Anàlisi")
aircraft_analysis_frame.pack(fill="x", pady=4)
aircraft_maps_frame = tk.LabelFrame(aircraft_frame,text="Mapes")
aircraft_maps_frame.pack(fill="x", pady=4)

lebl_frame = tk.LabelFrame(finestra,text="LEBL",padx=6,pady=6)
lebl_frame.grid(row=0,column=2,padx=5,pady=5,sticky="ns")
lebl_structure_frame = tk.LabelFrame(lebl_frame,text="Estructura")
lebl_structure_frame.pack(fill="x", pady=4)
lebl_gates_frame = tk.LabelFrame(lebl_frame,text="Portes")
lebl_gates_frame.pack(fill="x", pady=4)
lebl_visual_frame = tk.LabelFrame(lebl_frame,text="Visualització")
lebl_visual_frame.pack(fill="x", pady=4)

#Donem color als LabelFrame
for frame in [airport_frame, aircraft_frame, lebl_frame,airport_data_frame, airport_visual_frame,aircraft_data_frame, aircraft_analysis_frame, aircraft_maps_frame,lebl_structure_frame, lebl_gates_frame, lebl_visual_frame]:
    frame.configure(bg=COLOR_FRAME,fg=COLOR_TEXT,font=("Segoe UI", 10, "bold"))

#Creem els botons i els enllacem amb les funcions de dalt mitjançant "command".
button1=tk.Button(airport_data_frame,text="1. Carregar Aeroports",width=24,height=1,command=carregar_fitxer)
button1.pack(fill="x", pady=2)
button2=tk.Button(airport_data_frame,text="2. Configurar Schengen",width=24,height=1,command=set_schengen)
button2.pack(fill="x", pady=2)
button3=tk.Button(airport_data_frame,text="3. Mostrar Dades Aeroports",width=24,height=1,command=mostrar_dades)
button3.pack(fill="x", pady=2)
button4=tk.Button(airport_data_frame,text="4. Desar Aeroports Schengen",width=24,height=1,command=desar_schengen)
button4.pack(fill="x", pady=2)
button5=tk.Button(airport_data_frame,text="5. Afegir un Aeroport",width=24,height=1,command=afegir_aeroport)
button5.pack(fill="x", pady=2)
button6=tk.Button(airport_data_frame,text="6. Eliminar un Aeroport",width=24,height=1,command=eliminar_aeroport)
button6.pack(fill="x", pady=2)
button7=tk.Button(airport_visual_frame,text="7. Veure Gràfic",width=24,height=1,command=mostrar_grafic)
button7.pack(fill="x", pady=2)
button8=tk.Button(airport_visual_frame,text="8. Google Earth",width=24,height=1,command=mostrar_mapa_google_earth)
button8.pack(fill="x", pady=2)
button9=tk.Button(airport_visual_frame,text="9. Veure Aeroports",width=24,height=1,command=mostrar_mapa_interactiu)
button9.pack(fill="x", pady=2)

button10=tk.Button(aircraft_data_frame, text="10. Carregar Vols", width=24, height=1, command=carregar_vols)
button10.pack(fill="x", pady=2)
button11=tk.Button(aircraft_data_frame, text="11. Desar Vols", width=24, height=1, command=desar_vols)
button11.pack(fill="x", pady=2)
button12=tk.Button(aircraft_data_frame, text="12. Carregar Sortides", width=24, height=1, command=carregar_sortides)
button12.pack(fill="x", pady=2)
button13=tk.Button(aircraft_data_frame, text="13. Fusionar Moviments", width=24, height=1, command=fusionar_moviments)
button13.pack(fill="x", pady=2)
button14=tk.Button(aircraft_analysis_frame, text="14. Gràfic Arribades", width=24, height=1, command=mostrar_grafic_arribades)
button14.pack(fill="x", pady=2)
button15=tk.Button(aircraft_analysis_frame, text="15. Gràfic Aerolínies", width=24, height=1, command=mostrar_grafic_aerolinies)
button15.pack(fill="x", pady=2)
button16=tk.Button(aircraft_analysis_frame, text="16. Tipus Vols", width=24, height=1, command=mostrar_tipus_vols)
button16.pack(fill="x", pady=2)
button17=tk.Button(aircraft_analysis_frame, text="17. Vols Llargs", width=24, height=1, command=mostrar_vols_llargs)
button17.pack(fill="x", pady=2)
button18=tk.Button(aircraft_analysis_frame, text="18. Avions Nocturns", width=24, height=1, command=mostrar_avions_nit)
button18.pack(fill="x", pady=2)

label_hora_inici = tk.Label(aircraft_analysis_frame,text="Hora inici (0-23)")
label_hora_inici.pack()

entry_hora_inici = tk.Entry(aircraft_analysis_frame,width=10)
entry_hora_inici.pack(pady=2)

label_hora_fi = tk.Label(aircraft_analysis_frame,text="Hora final (0-23)")
label_hora_fi.pack()

entry_hora_fi = tk.Entry(aircraft_analysis_frame,width=10)
entry_hora_fi.pack(pady=2)

button19=tk.Button(aircraft_maps_frame, text="20. Google Earth", width=24, height=1, command=mostrar_mapa_vols_google_earth)
button19.pack(fill="x", pady=2)
button20=tk.Button(aircraft_maps_frame, text="21. Veure Vols", width=24, height=1, command=mostrar_mapa_interactiu_vols)
button20.pack(fill="x", pady=2)
button21=tk.Button(aircraft_maps_frame, text="22. Google Earth (Vols Llargs)", width=24, height=1, command=mostrar_mapa_vols_llargs_google_earth)
button21.pack(fill="x", pady=2)
button22=tk.Button(aircraft_maps_frame, text="23. Veure Vols Llargs", width=24, height=1, command=mostrar_mapa_interactiu_vols_llargs)
button22.pack(fill="x", pady=2)

button23=tk.Button(lebl_structure_frame, text="24. Carregar Estructura", width=24, height=1, command=carregar_estructura_lebl)
button23.pack(fill="x", pady=2)
button24=tk.Button(lebl_structure_frame, text="25. Buscar Terminal", width=24, height=1, command=buscar_terminal)
button24.pack(fill="x", pady=2)
button25=tk.Button(lebl_gates_frame, text="26. Ocupació Portes", width=24, height=1, command=mostrar_ocupacio_portes)
button25.pack(fill="x", pady=2)
button26=tk.Button(lebl_gates_frame, text="27. Assignar Porta", width=24, height=1, command=assignar_porta)
button26.pack(fill="x", pady=2)
button27=tk.Button(lebl_gates_frame, text="28. Alliberar Porta", width=24, height=1, command=alliberar_porta)
button27.pack(fill="x", pady=2)
button28=tk.Button(lebl_gates_frame, text="29. Portes Nit", width=24, height=1, command=assignar_portes_nit)
button28.pack(fill="x", pady=2)
button29=tk.Button(lebl_visual_frame, text="32. Mapa Portes", width=24, height=1, command=mostrar_mapa_portes)
button29.pack(fill="x", pady=2)
button30=tk.Button(lebl_visual_frame, text="33. Ocupació Diària", width=24, height=1, command=mostrar_ocupacio_dia)
button30.pack(fill="x", pady=2)
button31=tk.Button(lebl_gates_frame,text="30. Simular Hora",width=24,height=1,command=assignar_portes_hora)
button31.pack(fill="x", pady=2)
button32 = tk.Button(aircraft_analysis_frame,text="19. Comptar Sortides",width=24,height=1,command=comptar_sortides_interval)
button32.pack(fill="x", pady=2)
frame_botones_puertas = tk.LabelFrame(lebl_frame, text=" Control de Puertas (LEBL) ", padx=10, pady=5)
frame_botones_puertas.pack(side="top", fill="x", padx=5, pady=5)

# Botón para mostrar la Terminal 1
btn_t1 = tk.Button(frame_botones_puertas,text="Ver Terminal T1",font=("Arial", 10, "bold"),bg="#34495E",fg="white",command=lambda: actualizar_mapa_puertas("T1"))
btn_t1.pack(side="left", expand=True, fill="x", padx=5, pady=2)

# Botón para mostrar la Terminal 2
btn_t2 = tk.Button(frame_botones_puertas,text="Ver Terminal T2",font=("Arial", 10, "bold"),bg="#34495E",fg="white",command=lambda: actualizar_mapa_puertas("T2"))
btn_t2.pack(side="left", expand=True, fill="x", padx=5, pady=2)

tk.Label(lebl_gates_frame,text="Codi aerolínia",bg=COLOR_FRAME,fg=COLOR_TEXT).pack(fill="x", pady=(8,2))

entrada_aerolinia = tk.Entry(lebl_gates_frame)
entrada_aerolinia.pack(fill="x", pady=2)

button33 = tk.Button(lebl_gates_frame,text="31. Comptar aerolínia",width=24,height=1,command=comptar_avions_aerolinia)
button33.pack(fill="x", pady=2)

#Canviem l'estil dels botons
llista_botons = [button1,button2,button3,button4,button5,button6,button7,button8,button9,button10,button11,button12,button13,button14,button15,button16,button17,button18,button19,button20,button21,button22,button23,button24,button25,button26,button27,button28,button29,button30,button31,button32,button33]
for boto in llista_botons:
    boto.configure(bg=COLOR_BOTO,fg="white",activebackground=COLOR_BOTO_HOVER,activeforeground="white",relief="flat",font=("Segoe UI", 9))

# VISOR FITXERS
frame_visor=tk.LabelFrame(main_content,text="Contingut fitxer")
frame_visor.grid(row=0,column=0,sticky="nsew",pady=(0,5))
visor_fitxers=ScrolledText(frame_visor,height=10)
visor_fitxers.pack(expand=True,fill="both")
visor_fitxers.configure(bg="white",fg=COLOR_TEXT,font=("Consolas", 10),relief="flat")

# ZONA FUTURA PLOTS
frame_plots = tk.LabelFrame(main_content, text="Plots i gràfics", height=250)
frame_plots.grid(row=1,column=0,sticky="nsew",pady=5)
frame_plots.grid_propagate(False)
plot_canvas = tk.Canvas(frame_plots, highlightthickness=0)
scrollbar_plots = tk.Scrollbar(frame_plots, orient="vertical", command=plot_canvas.yview)
plot_canvas.configure(yscrollcommand=scrollbar_plots.set)
scrollbar_plots.pack(side="right", fill="y")
plot_canvas.pack(side="left", fill="both", expand=True)

def on_scroll(e):
    plot_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
plot_inner_frame = tk.Frame(plot_canvas)
plot_inner_frame.columnconfigure(0, weight=1)
plot_inner_frame.rowconfigure(0, weight=1)
plot_canvas.create_window((0, 0), window=plot_inner_frame, anchor="nw")
plot_canvas.bind("<Enter>", lambda e: plot_canvas.bind("<MouseWheel>", on_scroll))
plot_canvas.bind("<Leave>", lambda e: plot_canvas.unbind("<MouseWheel>"))

def update_scroll_region(event):
    plot_canvas.configure(scrollregion=plot_canvas.bbox("all"))

canvas_plot = None
def ajustar_figura(event):
    global canvas_plot
    if canvas_plot is None:
        return
    w = event.width / 100
    h = canvas_plot.figure.get_size_inches()[1]
    canvas_plot.figure.set_size_inches(w, h, forward=True)
    canvas_plot.draw_idle()

def on_frame_configure(event):
    update_scroll_region(event)
    ajustar_figura(event)

plot_inner_frame.bind("<Configure>", on_frame_configure)

SetPlotFrame(plot_inner_frame)

# MAPA
frame_mapa = tk.LabelFrame(main_content,text="Mapa interactiu")
frame_mapa.grid(row=2,column=0,sticky="nsew")
map_widget = TkinterMapView(frame_mapa,width=900,height=300,corner_radius=10)
map_widget.pack(fill="both",expand=True)
map_widget.set_position(41.2974, 2.0833)
map_widget.set_zoom(5)

frame_visor.configure(bg=COLOR_FRAME)
frame_plots.configure(bg=COLOR_FRAME)
frame_mapa.configure(bg=COLOR_FRAME)


#Canviem l'estil de les taules
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",background="white",foreground=COLOR_TEXT,rowheight=25,fieldbackground="white")
style.configure("Treeview.Heading",background=COLOR_BOTO,foreground="white",font=("Segoe UI", 9, "bold"))


#Bucle principal que manté la finestra oberta.
finestra.mainloop()