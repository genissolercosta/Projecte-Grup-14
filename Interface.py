import tkinter as tk  #Importació de la llibreria per crear gràfics a Python.
from tkinter import filedialog, messagebox, simpledialog, ttk
from airport import * #Importar el document airport.py
from aircraft import * #Importar el document aircraft.py
from LEBL import* #Importar el document LEBL.py
from tkinter.scrolledtext import ScrolledText

#Llista global on guardarem els aeroports a la memòria del programa.
llista_aeroports = []
llista_avions=[]
bcn_airport=""

def carregar_fitxer(): #Obre una finestra per realitzar 3 funcions: Perquè l'usuari triï el fitxer.txt; per actualitzar
    # el boleà Schengen; i, finalment, per poder modificar la llista "global llista_aeroports".
    global llista_aeroports
    nom_fitxer = filedialog.askopenfilename(title="Selecciona l'arxiu d'aeroports", filetypes=[("Text files", "*.txt")])
    if nom_fitxer != "":
        llista_aeroports = LoadAirports(nom_fitxer)
        mostrar_fitxer(nom_fitxer)
        missatge = "S'han carregat " + str(len(llista_aeroports)) + " aeroports correctament."
        messagebox.showinfo("Èxit", missatge)

def set_schengen(): #Repassa la llista de la memòria i comprova, un per un, quins aeroports són Schengen.
    i=0
    while i<len(llista_aeroports):
        SetSchengen(llista_aeroports[i])
        i=i+1
    missatge = "S'han configurat els atributs Schengen dels aeroports correctament."
    messagebox.showinfo("Èxit", missatge)

def mostrar_dades(): #Crea una subfinestra nova, hi dibuixa una taula amb columnes, i l'omple/completa amb els
    # aeroports de la llista.
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

    #Afegir scrollbar vertical (ho posem amb # perquè ho afegirem a la última versió)
    #vert_scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    #vert_scrollbar.pack(side="right", fill="y")
    #tree.configure(yscrollcommand=vert_scrollbar.set)

    #Omplir dades dels aeroports
    i=0
    while i<len(llista_aeroports):
        aeroport=llista_aeroports[i]
        tree.insert("", "end", values=(i+1, aeroport.ICAO, aeroport.latitud, aeroport.longitud, aeroport.Schengen))
        i=i+1

def desar_schengen(): #Es fa una comprovació de que es tinguin dades. A continuació, obre una nova finestra i crida a
    # la funció "SaveSchengenAirports".
    if len(llista_aeroports)==0:
        messagebox.showwarning("Avís", "No hi ha aeroports carregats per desar.")
        return
    nom_fitxer=filedialog.asksaveasfilename(defaultextension=".txt", title="Desar aeroports Schengen")

    if nom_fitxer!="":
        resultat = SaveSchengenAirports(llista_aeroports, nom_fitxer)
        if resultat==0:
            messagebox.showinfo("Èxit", "Fitxer desat correctament.")
        else:
            messagebox.showinfo("Error", "No s'ha pogut desar cap fitxer.")
    else:
        messagebox.showinfo("Error", "No s'ha seleccionat cap fitxer.")

def afegir_aeroport(): #Et demana ICAO i coordenades de l'aeroport, crea un objecte "Aeroport", comprova el boleà
    # Schengen, i l'afegeix a la llista en cas que no hi sigui ja.
    codi=simpledialog.askstring("Nou Aeroport", "Introdueix el codi ICAO (ex: LEBL):")
    if not codi:#Si l'usuari cancel·la.
        return

    lat=simpledialog.askstring("Nou Aeroport", "Introdueix la latitud en graus decimals (ex: 41.29):")
    lon=simpledialog.askstring("Nou Aeroport", "Introdueix la longitud en graus decimals (ex: 2.08):")

    if lat and lon:
        nou_aero=Airport(codi.upper(), float(lat), float(lon))
        SetSchengen(nou_aero)  # Comprovem si és Schengen
        AddAirport(llista_aeroports, nou_aero)
        messagebox.showinfo("Èxit", "Aeroport " + codi.upper() + " afegit a la llista.")

def eliminar_aeroport(): #Demana codi ICAO, i l'esborra de la llista mitjançant la funció definida anteriorment en el
    # mateix codi.
    codi=simpledialog.askstring("Eliminar Aeroport", "Introdueix el codi ICAO a eliminar:")
    if codi:
        resultat=RemoveAirport(llista_aeroports, codi.upper())
        if resultat==0:
            messagebox.showinfo("Èxit", "Aeroport eliminat correctament.")
        else:
            messagebox.showerror("Error", "No s'ha trobat cap aeroport amb aquest codi.")

def mostrar_grafic():# Comprova que hi ha dades carregades i, en el cas afirmatiu, carrega/dibuixa el gràfic de barres.
    if len(llista_aeroports)>0:
        PlotAirports(llista_aeroports)
    else:
        messagebox.showwarning("Avís", "Primer has de carregar els aeroports.")

def mostrar_mapa(): #Comprova que hi ha dades carregades i, en el cas afirmatiu, carrega el mapa de Google Earth.
    if len(llista_aeroports)>0:
        MapAirports(llista_aeroports)
    else:
        messagebox.showwarning("Avís", "Primer has de carregar els aeroports.")

def carregar_vols(): #Permet obtenir el llistat de vols a partir d'un document .txt per posteriorment analitzar-lo
    global llista_avions
    nom_fitxer=filedialog.askopenfilename(title="Selecciona l'arxiu d'arribades",filetypes=[("Text files", "*.txt")])

    if nom_fitxer!="":
        llista_avions=LoadArrivals(nom_fitxer)
        mostrar_fitxer(nom_fitxer)
        missatge="S'han carregat " + str(len(llista_avions)) + " vols."
        messagebox.showinfo("Èxit", missatge)

def mostrar_grafic_arribades(): #Mostra la freqüència d'arribades per cada hora del dia a LEBL en un gràfic de barres.
    if len(llista_avions)>0:
        PlotArrivals(llista_avions)
    else:
        messagebox.showwarning("Avís","Primer s'han de carregar els vols.")

def mostrar_grafic_aerolinies(): #Mostra el número de vols per cada aerolínia
    if len(llista_avions)>0:
        PlotAirlines(llista_avions)
    else:
        messagebox.showwarning("Avís","Primer has de carregar els vols.")
def mostrar_tipus_vols(): #Indica els vols que provenen de l'espai Schengen i els que no en provenen, i ho mostra en un
    # gràfic de barres.
    if len(llista_avions)>0:
        PlotFlightsType(llista_avions)
    else:
        messagebox.showwarning("Avís","Primer s'han de carregar els vols.")

def desar_vols():#Permet abocar la llista de vols a un fitxer
    if len(llista_avions)==0:
        messagebox.showwarning("Avís","No hi ha vols")
        return
    nom_fitxer=filedialog.asksaveasfilename(defaultextension=".txt")
    if nom_fitxer!="":
        SaveFlights(llista_avions, nom_fitxer)
        messagebox.showinfo("Èxit","Fitxer desat correctament")
    else:
        messagebox.showinfo("Error", "No s'ha seleccionat cap fitxer.")

def mostrar_mapa_vols(): #Representa els vols a Google Earth, assegurant-se que hi ha tant els vols com els aeroports
    # carregats.
    if len(llista_avions)>0 and len(llista_aeroports)>0:
        MapFlights(llista_avions, llista_aeroports)
    else:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")

def mostrar_vols_llargs(): #Mostra en una llista els aeroports que es troben a més de 2.000km de l'aeroport de
    # Barcelona.
    if len(llista_avions)==0 or len(llista_aeroports)==0:
        messagebox.showwarning("Avís", "Carrega aeroports i vols.")
        return

    llista_llargs=LongDistanceArrivals(llista_avions, llista_aeroports)

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

def carregar_estructura_lebl(): #Llegeix el fitxer de les terminals,
    global bcn_airport
    nom_fitxer = filedialog.askopenfilename(title="Selecciona l'arxiu LEBL",filetypes=[("Text files", "*.txt")])

    if nom_fitxer!="":
        bcn_airport=LoadAirportStructure(nom_fitxer)
        mostrar_fitxer(nom_fitxer)
        if bcn_airport==-1:
            messagebox.showerror("Error", "No s'ha pogut carregar l'estructura.")
        else:
            messagebox.showinfo("Èxit","Estructura de l'aeroport carregada correctament.")

def mostrar_ocupacio_portes(): #Analitza totes les portes de les terminals i genera una taula, la qual indica les
    # portes que estan disponibles i les que no.
    if bcn_airport=="":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return

    dades=GateOccupancy(bcn_airport)

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

def buscar_terminal(): #Et demana el codi d'una companyia, i et diu a veure a quina terminal es troba.
    if bcn_airport=="":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return
    aerolinia = simpledialog.askstring("Buscar terminal","Introdueix el codi ICAO de l'aerolínia:")
    if aerolinia:
        terminal = SearchTerminal(bcn_airport, aerolinia.upper())
        if terminal!="":
            messagebox.showinfo("Terminal trobada","L'aerolínia opera a la terminal " + terminal)
        else:
            messagebox.showwarning("No trobada",
                "No existeix cap terminal per aquesta aerolínia.")

def assignar_porta(): #Demana el codi d'un avió, per buscar-lo a la llista d'avions, per saber de quin país prové i
    # quina companyia és. Amb això, crida a la funció "Assign Gate", perquè busqui la porta correcta i l'ocupi, i,
    # posteriorment ho informa per pantalla.
    global bcn_airport
    if bcn_airport=="":
        messagebox.showwarning("Avís", "Primer carrega l'estructura LEBL.")
        return
    if len(llista_avions)==0:
        messagebox.showwarning("Avís", "Primer carrega els vols.")
        return

    aircraft_id=simpledialog.askstring("Assignar porta","Introdueix el codi de l'avió:")

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
    porta=AssignGate(bcn_airport, avio_trobat)
    if porta==-1:
        messagebox.showwarning("Sense portes","No hi ha portes disponibles.")
    else:
        messagebox.showinfo("Porta assignada","L'avió s'ha assignat a la porta " + porta)

def mostrar_fitxer(path_fitxer): #Aquesta funció ens serveix perquè, cada vegada que carreguem i llegim un arxiu de
    # text, ens mostra tot el seu contingut a la caixa de text de la part de baix de la interfície.
    try:
        F=open(path_fitxer, "r")
        contingut=F.read()
        visor_fitxers.delete("1.0", tk.END)
        visor_fitxers.insert(tk.END, contingut)
        F.close()

    except FileNotFoundError:
        messagebox.showerror("Error", "No s'ha pogut obrir el fitxer.")

#Creació de la finestra a la interfície principal.
finestra = tk.Tk()
finestra.title("Gestor d'Aeroports")#Títol de la finestra.
finestra.geometry("600x1500")#Mida de la finestra.

#Etiqueta de títol.
titol = tk.Label(finestra, text="Menú Principal", font=("Arial", 16))
titol.grid(row=0,column=0,pady=10)

#Finestres de les columnes de la interfaç.
finestra.columnconfigure(0,weight=1)
finestra.rowconfigure(0,weight=1)
finestra.rowconfigure(1,weight=1)
finestra.rowconfigure(2,weight=1)
finestra.rowconfigure(3,weight=1)
finestra.rowconfigure(4,weight=1)

button_aeroports_frame=tk.LabelFrame(finestra,text="Aeroports")
button_aeroports_frame.grid(row=0,column=0,padx=5,pady=5,sticky=tk.W+tk.E+tk.N+tk.S)

button_canvi_frame=tk.LabelFrame(finestra,text="Afegir/Eliminar")
button_canvi_frame.grid(row=1,column=0,padx=5,pady=5,sticky=tk.W+tk.E+tk.N+tk.S)

button_grafics_frame=tk.LabelFrame(finestra,text="Gràfics")
button_grafics_frame.grid(row=2,column=0,padx=5,pady=5,sticky=tk.W+tk.E+tk.N+tk.S)

button_vols_frame=tk.LabelFrame(finestra, text="Vols")
button_vols_frame.grid(row=3,column=0,padx=5,pady=5,sticky=tk.W+tk.E+tk.N+tk.S)

button_lebl_frame = tk.LabelFrame(finestra, text="LEBL")
button_lebl_frame.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

button_aeroports_frame.columnconfigure(0,weight=1)
button_aeroports_frame.rowconfigure(0,weight=1)
button_aeroports_frame.rowconfigure(1,weight=1)
button_aeroports_frame.rowconfigure(2,weight=1)
button_aeroports_frame.rowconfigure(3,weight=1)

button_canvi_frame.columnconfigure(0,weight=1)
button_canvi_frame.rowconfigure(0,weight=1)
button_canvi_frame.rowconfigure(1,weight=1)

button_grafics_frame.columnconfigure(0,weight=1)
button_grafics_frame.rowconfigure(0,weight=1)
button_grafics_frame.rowconfigure(1,weight=1)

button_vols_frame.columnconfigure(0,weight=1)
button_vols_frame.rowconfigure(0,weight=1)
button_vols_frame.rowconfigure(1,weight=1)
button_vols_frame.rowconfigure(2,weight=1)
button_vols_frame.rowconfigure(3,weight=1)
button_vols_frame.rowconfigure(4,weight=1)

button_lebl_frame.columnconfigure(0, weight=1)
button_lebl_frame.rowconfigure(0, weight=1)
button_lebl_frame.rowconfigure(1, weight=1)
button_lebl_frame.rowconfigure(2, weight=1)
button_lebl_frame.rowconfigure(3, weight=1)

#Creem els botons i els enllacem amb les funcions de dalt mitjançant "command".
button1=tk.Button(button_aeroports_frame, text="1. Carregar Aeroports", command=carregar_fitxer)
button1.grid(row=0,column=0, sticky=tk.W+tk.E)
button2=tk.Button(button_aeroports_frame, text="2. Configurar Schengen", command=set_schengen)
button2.grid(row=1,column=0, sticky=tk.W+tk.E)
button3=tk.Button(button_aeroports_frame, text="3. Mostrar Dades Aeroports", command=mostrar_dades)
button3.grid(row=2,column=0, sticky=tk.W+tk.E)
button4=tk.Button(button_aeroports_frame, text="4. Desar Aeroports Schengen", command=desar_schengen)
button4.grid(row=3,column=0, sticky=tk.W+tk.E)

button5=tk.Button(button_canvi_frame, text="5. Afegir un Aeroport", command=afegir_aeroport)
button5.grid(row=0,column=0, sticky=tk.W+tk.E)
button6=tk.Button(button_canvi_frame, text="6. Eliminar un Aeroport", command=eliminar_aeroport)
button6.grid(row=1,column=0, sticky=tk.W+tk.E)

button7=tk.Button(button_grafics_frame, text="7. Veure Gràfic (Plot)", command=mostrar_grafic)
button7.grid(row=0,column=0, sticky=tk.W+tk.E)
button8=tk.Button(button_grafics_frame, text="8. Veure al Mapa (Google Earth)", command=mostrar_mapa)
button8.grid(row=1,column=0, sticky=tk.W+tk.E)

button9=tk.Button(button_vols_frame, text="9. Carregar Vols", command=carregar_vols)
button9.grid(row=0, column=0, sticky=tk.W+tk.E+tk.S+tk.N)
button10=tk.Button(button_vols_frame, text="10. Gràfic Arribades", command=mostrar_grafic_arribades)
button10.grid(row=1, column=0, sticky=tk.W+tk.E)
button11=tk.Button(button_vols_frame, text="11. Gràfic Aerolínies", command=mostrar_grafic_aerolinies)
button11.grid(row=2, column=0, sticky=tk.W+tk.E)
button12=tk.Button(button_vols_frame, text="12. Tipus Vols", command=mostrar_tipus_vols)
button12.grid(row=3, column=0, sticky=tk.W+tk.E)
button13=tk.Button(button_vols_frame, text="13. Desar Vols", command=desar_vols)
button13.grid(row=4, column=0, sticky=tk.W+tk.E)
button14 = tk.Button(button_vols_frame, text="14. Veure Vols al Mapa", command=mostrar_mapa_vols)
button14.grid(row=5, column=0, sticky=tk.W+tk.E)
button15 = tk.Button(button_vols_frame, text="15. Vols Llarga Distància", command=mostrar_vols_llargs)
button15.grid(row=6, column=0, sticky=tk.W+tk.E)
button16 = tk.Button(button_lebl_frame,text="16. Carregar estructura LEBL",command=carregar_estructura_lebl)
button16.grid(row=0, column=0, sticky=tk.W+tk.E)
button17 = tk.Button(button_lebl_frame,text="17. Veure ocupació portes",command=mostrar_ocupacio_portes)
button17.grid(row=1, column=0, sticky=tk.W+tk.E)
button18 = tk.Button(button_lebl_frame,text="18. Buscar terminal aerolínia",command=buscar_terminal)
button18.grid(row=2, column=0, sticky=tk.W+tk.E)
button19 = tk.Button(button_lebl_frame,text="19. Assignar porta",command=assignar_porta)
button19.grid(row=3, column=0, sticky=tk.W+tk.E)

frame_visor = tk.LabelFrame(finestra, text="Contingut del fitxer carregat")
frame_visor.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

visor_fitxers = ScrolledText(frame_visor, height=15)
visor_fitxers.pack(expand=True, fill="both")

finestra.rowconfigure(5, weight=3)

# Bucle principal que manté la finestra oberta.
finestra.mainloop()