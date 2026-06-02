import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#FUNCIONS EXTRA
PLOT_FRAME=None
def SetPlotFrame(frame):
    global PLOT_FRAME
    PLOT_FRAME = frame

def mostrar_plot_en_frame(fig):
    global PLOT_FRAME
    if PLOT_FRAME is None:
        return

    # esborrar plot anterior
    for widget in PLOT_FRAME.winfo_children():
        widget.destroy()
    # inserir nou plot
    canvas = FigureCanvasTkAgg(fig, master=PLOT_FRAME)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

class Gate:
    def __init__(self, name, occupied, aircraft_id):
        self.name=name
        self.occupied=occupied
        self.aircraft_id=aircraft_id

class BoardingArea:
    def __init__(self, name, type):
        self.name=name
        self.type=type
        self.gates=[]

class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas=[]
        self.airlines=[]

class BarcelonaAP:
    def __init__(self, code):
        self.code=code
        self.terminals=[]

class Aircraft:
    def __init__(self, aircraft_id, company, airport_origin):
        self.aircraft_id = aircraft_id
        self.company = company
        self.airport_origin = airport_origin

def SetGates(area,init_gate,end_gate,prefix):
    if end_gate<=init_gate:#Forcem a que la porta final sigui major a la inicial
        return-1
    area.gates=[]#Creem la llista de portes de l'aera
    i=init_gate
    while i<=end_gate:
        gate_name=prefix+str(i)
        new_gate=Gate(gate_name,False,"")#Creem cada una de les portes de classe Gate de la llista
        area.gates.append(new_gate)
        i=i+1
    return 0

def LoadAirlines(terminal, t_name):
    filename=t_name+"_Airlines.txt"
    errors=[]
    try:
        F=open(filename,"r") #obrim el fitxer T1_Airlines i T2_Airlines
        new_airlines=[]
        line=F.readline() #Llegim la primera línia del fitxer
        line_num=1
        while line!="": #Mentres el fitxer té línies es va repetint el bucle
            elements=line.split() #els elements estant seperats per un espai
            if len(elements)<2: #Comprovem que no hi hagi errors (línia massa curta)
                errors.append(f"{filename} línia {line_num}: format incorrecte")
                line=F.readline()
                line_num+=1
                continue
            code=elements[-1].strip().upper() #El codi és l'últim element de la llista
            if len(code)!=3:
                errors.append(f"{filename} línia {line_num}: aerolínia invàlida ({code})")
            else:
                new_airlines.append(code) #Si no hi ha error, l'afegim
            line=F.readline() #Llegim la següent línia i tornem a començar el bucle
            line_num+=1
        F.close()
        terminal.airlines=new_airlines
        return errors
    except FileNotFoundError:
        return -1

def LoadAirportStructure(filename):
    errors=[] #Afegirem els error que trobem en la estructura del fitxer
    try:
        F=open(filename, "r")
        linia=F.readline()
        if not linia:
            return None, ["Fitxer buit"]

        elements=linia.split()
        if len(elements)<2:
            return None, ["Línia 1 incorrecta: falta informació base"]

        airport_code = elements[0].upper() #Validació ICAO
        if len(airport_code) != 4 or not airport_code.isalpha():
            errors.append("Línia 1: codi aeroport invàlid")

        try:
            num_terminals=int(elements[1])
        except:
            return None, ["Línia 1: nombre de terminals no vàlid"]

        airport=BarcelonaAP(airport_code)
        t=0
        while t<num_terminals: #Recorrem les terminals
            linia=F.readline()
            if not linia:
                errors.append("Fitxer incomplet (terminals faltants)")
                break

            elements=linia.split()
            if len(elements)<3:
                errors.append(f"Línia terminal {t+2}: format incorrecte")
                continue

            terminal_name=elements[1].upper()
            terminal = Terminal(terminal_name)
            if len(terminal_name)!=2 or terminal_name[0]!="T":
                errors.append(f"Línia terminal {t + 2}: nom terminal invàlid ({terminal_name})")
            try:
                num_areas=int(elements[2])
            except:
                errors.append(f"Línia terminal {t + 2}: num àrees invàlid")
                num_areas=0

            #airlines
            airline_errors = LoadAirlines(terminal, terminal_name)
            i=0
            while i<len(airline_errors):
                errors.append(airline_errors[i])
                i+=1

            try:
                num_areas=int(num_areas)
            except:
                errors.append(f"Terminal {terminal_name}: num àrees invàlid")
                num_areas=0
            i=0
            while i<num_areas: #Recorrem totes les àrees
                linia=F.readline()
                if not linia:
                    errors.append(f"Terminal {terminal_name}: falta info d’àrees")
                    break

                elements=linia.split()
                if len(elements)<7:
                    errors.append(f"Àrea mal formatada a terminal {terminal_name}")
                    i+=1
                    continue

                area_name=elements[1]
                type_area=elements[2]

                if type_area!="Schengen" and type_area!="non-Schengen": #Validació tipus
                    errors.append(f"Àrea {area_name}: tipus invàlid")

                try:
                    init_gate=int(elements[4]) #Agafem les portes inicial i final
                    end_gate=int(elements[6])
                except:
                    errors.append(f"Àrea {area_name}: gates invàlides")
                    i+=1
                    continue

                area=BoardingArea(area_name, type_area)
                prefix=terminal_name + "BA" + area_name + "G"

                result=SetGates(area, init_gate, end_gate, prefix)
                if result==-1:
                    errors.append(f"Àrea {area_name}: rang de gates incorrecte")

                terminal.boarding_areas.append(area)
                i+=1
            airport.terminals.append(terminal)
            t+=1
        F.close()
        return airport, errors

    except FileNotFoundError:
        return None, ["Fitxer no trobat"]

def GateOccupancy(bcn):
    result=[] #Llista on veurem l'estat de de cada porta (lliure o ocupada)
    i=0
    while i<len(bcn.terminals):
        terminal=bcn.terminals[i]
        j=0
        while j<len(terminal.boarding_areas):
            area=terminal.boarding_areas[j]
            k=0
            while k<len(area.gates):
                gate=area.gates[k]
                gate_info=[] #llista on s'apunten els estat de cada porta si estan ocupats o lliures
                gate_info.append(gate.name) #visualitzem el nom de cada porta
                if gate.occupied: #i valorem si es troba ocupada per un avió o no
                    gate_info.append("Ocupat") #de ser així afegim ocupat a la llista
                    gate_info.append(gate.aircraft_id) #i el nom de l'avió
                else:
                    gate_info.append("Lliure") #En canvi, de no estar-ho afegim lliure a la llista
                    gate_info.append("-") #I en el lloc (on hi hauria l'avió) hi posem un guió
                result.append(gate_info)
                k=k+1
            j=j+1
        i=i+1
    return result

def IsAirlineInTerminal(terminal,name):
    if name=="": #si el nom és una cadena buida es retrona False
        return False
    if len(terminal.airlines)==0: #igual si el terminal té una llista buida d'aerolínies
        return False
    i=0
    encontrado=False
    while i<len(terminal.airlines) and not encontrado:
        if terminal.airlines[i]==name: #si l'aerolinia es troba a la terminal retorna la cerca és verdadera
            encontrado=True
        i=i+1
    if encontrado: #si és verdadera retrona True
        return True
    else: #en cas contrari retrona False
        return False

def SearchTerminal(bcn,name):
    if name=="":
        return ""
    i=0
    encontrado=False
    while i<len(bcn.terminals) and not encontrado:
        terminal=bcn.terminals[i] #guarda les terminals de llista i les valora
        if IsAirlineInTerminal(terminal,name): #si el nom de l'aerolinia consta en una terminal:
            encontrado=True #surt del bucle amb trobat=True
        i=i+1
    if encontrado:
        return terminal.name #si el troba retorna el nom de la terminal
    else:
        return "" #no obstant, si no el troba retorna una llista buida

def AssignGate(bcn,aircraft):
    terminal_name=SearchTerminal(bcn,aircraft.company)
    if terminal_name=="":
        return -1
    schengen_list = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY',
                     'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
    if aircraft.airport_origin != None and aircraft.airport_origin != "":
        prefix = aircraft.airport_origin[:2]#S'han de complir mínim una d'aquestes dues condicions per continuar amb
        # la funció
    elif aircraft.destination_airport != None and aircraft.destination_airport != "":
        prefix = aircraft.destination_airport[:2]
    else:
        return -1
    schengen=False
    i=0
    while i<len(schengen_list) and not schengen: #determinem si el tipus d'embarcament, si és schengen o no
        if prefix==schengen_list[i]:
            schengen=True
        i=i+1
    i=0
    while i<len(bcn.terminals):
        if bcn.terminals[i].name==terminal_name:
            j=0
            while j<len(bcn.terminals[i].boarding_areas):
                area=bcn.terminals[i].boarding_areas[j]
                correct_area=False
                if schengen and area.type=="Schengen": #Valorem que l'aera sigui la que toca pels vols
                    correct_area=True
                if not schengen and area.type=="non-Schengen":
                    correct_area=True
                if correct_area:
                    k=0
                    while k<len(area.gates):
                        if area.gates[k].occupied==False: #canviem l'estat de la porta a l'afegir un avió
                            area.gates[k].occupied=True
                            area.gates[k].aircraft_id=aircraft.aircraft_id
                            return area.gates[k].name
                        k=k+1
                j=j+1
        i=i+1
    return -1

def FreeGate(bcn, id):
    i = 0
    encontrado=False
    #Recorrem terminals -> àrees -> portes amb el teu estil de bucles fins a trobar l'avió
    while i<len(bcn.terminals) and not encontrado:
        j=0
        while j<len(bcn.terminals[i].boarding_areas) and not encontrado:
            area=bcn.terminals[i].boarding_areas[j]
            k=0
            while k<len(area.gates) and not encontrado:
                gate=area.gates[k]
                #Si la porta està ocupada i té la matrícula de l'avió que busquem:
                if gate.occupied and gate.aircraft_id == id:
                    gate.occupied = False#Alliberem la porta
                    gate.aircraft_id = ""#Netegem l'identificador
                    encontrado = True#Marquem com a trobat per sortir dels bucles
                k=k+1
            j=j+1
        i=i+1

    if encontrado:
        return 0#S'ha trobat i alliberat correctament.
    else:
        return -1#L'avió amb aquesta matrícula no s'ha trobat en cap porta

def TimeToMinutes(time_str):
    if not time_str or len(time_str)!=5:  # Si hi ha un error amb els minuts no s'executa
        return -1
    hores=int(time_str[:2])
    minuts=int(time_str[3:])

    return hores * 60 + minuts


def AssignGatesAtTime(bcn, aircrafts, time):
    if len(aircrafts)==0:
        return [],0

    #Liberar todas las puertas
    i=0
    while i<len(bcn.terminals):
        j=0
        while j<len(bcn.terminals[i].boarding_areas):
            area=bcn.terminals[i].boarding_areas[j]
            k=0
            while k<len(area.gates):
                area.gates[k].occupied=False
                area.gates[k].aircraft_id=""
                k=k+1
            j=j+1
        i=i+1

    current_time=TimeToMinutes(time)
    assigned=[]
    not_assigned=0

    i=0
    while i<len(aircrafts):
        aircraft=aircrafts[i]
        present=False
        if aircraft.land_time != None and aircraft.departure_time != None:#Valorem el cas de sortida i arrivada
            arrival=TimeToMinutes(aircraft.land_time)
            departure=TimeToMinutes(aircraft.departure_time)
            if arrival<=current_time and current_time<=departure+60:#Contem una hora despres del departure time per si
                # fos al cap de 5 o 10 minuts del current time.
                present=True
        elif aircraft.land_time != None and aircraft.departure_time == None:#Valorem el cas de tenir només arrivada
            arrival=TimeToMinutes(aircraft.land_time)
            if current_time>=arrival:
                present=True
        elif aircraft.land_time == None and aircraft.departure_time != None:#El cas d'avió nocturn amb només sortida
            departure=TimeToMinutes(aircraft.departure_time)
            if current_time<departure+60:
                present=True

        if present:#Si es troba correctament li assigna porta amb la funció AssignGate
            gate=AssignGate(bcn, aircraft)
            if gate != -1:
                aircraft.gate=gate
                assigned.append(aircraft)
            else:
                not_assigned+=1#En el cas que no hi hagin portes disponibles pel seu espai
        i=i+1
    return assigned, not_assigned

def AssignNightGates(bcn, aircrafts):
    #Si la llista que prové de NightAircraft està buida o és un error, retornem -1
    if len(aircrafts) == 0:
        return -1
    i=0
    #Recorrem la llista d'avions de la nit un per un amb un bucle while
    while i<len(aircrafts):
        aircraft=aircrafts[i]
        #Nomes aircraft nocturns
        only_departure=(aircraft.airport_origin == "" and aircraft.land_time == "" and
                          aircraft.airport_destination != "" and aircraft.departure_time != "")
        if only_departure:
            AssignGate(bcn, aircraft)
        i=i+1
    return 0

def PlotDayOccupancy(bcn, aircrafts):

    hores=[]
    ocupacio_t1=[]
    ocupacio_t2=[]
    no_assignats=[]
    h=0
    while h<24:
        current_time=h*60
        #Reiniciar portes
        i=0
        while i<len(bcn.terminals):
            j=0
            while j<len(bcn.terminals[i].boarding_areas):
                area=bcn.terminals[i].boarding_areas[j]
                k=0
                while k<len(area.gates):
                    area.gates[k].occupied=False
                    area.gates[k].aircraft_id = ""
                    k=k+1
                j=j+1
            i=i+1
        t1_count=0
        t2_count=0
        unassigned=0
        i=0
        while i<len(aircrafts):
            aircraft=aircrafts[i]
            present=False
            # ARRIBADA + SORTIDA
            if aircraft.land_time != "" and aircraft.departure_time != "":
                arrival=TimeToMinutes(aircraft.land_time)
                departure=TimeToMinutes(aircraft.departure_time)
                if arrival<=current_time+60 and departure>current_time:
                    present=True
            # NOMÉS ARRIBADA
            elif aircraft.land_time != None:
                arrival=TimeToMinutes(aircraft.land_time)
                if arrival<=current_time+60:
                    present=True
            # NOMÉS SORTIDA (avió nocturn)
            elif aircraft.departure_time != None:
                departure=TimeToMinutes(aircraft.departure_time)
                if departure>current_time:
                    present=True
            if present:
                gate=AssignGate(bcn, aircraft)
                if gate == -1:
                    unassigned+=1
                else:
                    if gate.startswith("T1"):
                        t1_count+=1
                    elif gate.startswith("T2"):
                        t2_count+=1
            i += 1
        hores.append(h)
        ocupacio_t1.append(t1_count)
        ocupacio_t2.append(t2_count)
        no_assignats.append(unassigned)
        h += 1
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(hores,ocupacio_t1,marker="o",label="Terminal T1")
    ax.plot(hores,ocupacio_t2,marker="o",label="Terminal T2")
    ax.plot(hores,no_assignats,marker="o",label="No assignats")
    ax.set_title("Ocupació diària de portes")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Nombre d'avions")
    ax.set_xticks(range(24))
    etiquetes = []
    i = 0
    while i < 24:
        etiquetes.append(f"{i:02d}:00")
        i += 1
    ax.set_xticklabels(etiquetes, rotation=45)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.show()
    return fig

#Secció de Tests
if __name__ == "__main__":

    gate=Gate("T1A1", False, "")
    area=BoardingArea("A", "Schengen")
    terminal=Terminal("T1")
    airport=BarcelonaAP("BCN")

    SetGates(area, 1, 3, "T1AG")

    terminal.airlines=["IB", "VY", "LH"]
    print(IsAirlineInTerminal(terminal, "IB"))

    terminal2=Terminal("T2")
    terminal2.airlines=["FR", "U2"]
    airport.terminals.append(terminal)
    airport.terminals.append(terminal2)
    print(SearchTerminal(airport, "IB"))

    schengen_area=BoardingArea("A", "Schengen")
    non_schengen_area=BoardingArea("B", "non-Schengen")

    SetGates(schengen_area, 1, 2, "T1AG")
    SetGates(non_schengen_area, 1, 2, "T1BG")

    terminal.boarding_areas=[]
    terminal.boarding_areas.append(schengen_area)
    terminal.boarding_areas.append(non_schengen_area)

    aircraft1=Aircraft("IB123", "IB", "LEMD")
    assigned_gate1=AssignGate(airport, aircraft1)
    print("Assigned gate:", assigned_gate1)
    aircraft2=Aircraft("IB789", "IB", "KJFK")
    assigned_gate2=AssignGate(airport, aircraft2)
    print("Assigned gate:", assigned_gate2)

    occupancy=GateOccupancy(airport)
    i=0
    while i<len(occupancy):
        print(occupancy[i])
        i=i+1


#FUNCIONALITAT EXTRA:
import matplotlib.patches as patches

def PlotLEBLGates(bcn, terminal_filtro="T1"):
    #Configuració de colors estil panelL d'aeroport
    COLOR_BG = "#F4F6F7"  #Fons de la imagen general
    COLOR_BARRA_AZUL = "#2B5B84"  #Blau corporatiu per a les ramificacions
    COLOR_FREE = "#2ECC71"  #Verd suau per a portes lliures
    COLOR_OCCUPIED = "#E74C3C"  #Vermell per a portes ocupades
    COLOR_TEXT_GATE = "white"  #Text dins dels rectangles

    # Creem la figura
    fig, ax = plt.subplots(figsize=(5, 5), facecolor=COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    # Buscar la terminal seleccionada
    target_terminal = None
    for terminal in bcn.terminals:
        if terminal.name == terminal_filtro:
            target_terminal = terminal
            break

    if target_terminal is None:
        ax.text(0.5, 0.5, f"No se encontraron datos para la {terminal_filtro}",
                ha="center", va="center", fontsize=12, color="#2C3E50")
        ax.axis("off")
        mostrar_plot_en_frame(fig)
        return fig

    # Posicionament vertical inicial
    y_offset = 0

    for area in target_terminal.boarding_areas:
        if not area.gates:
            continue

        # Calculem les subfiles necessàries
        max_gates_per_row = 7
        num_puertas = len(area.gates)
        num_rows_used = (num_puertas - 1) // max_gates_per_row + 1

        # Dimensions de la barra blava del fons
        barra_alto = 0.55 + (num_rows_used - 1) * 0.7
        barra_ancho = 11.5

        #Fons blau de la ramificació
        rect_barra = patches.Rectangle((0, y_offset - barra_alto + 0.4),
            barra_ancho,barra_alto,linewidth=0,facecolor=COLOR_BARRA_AZUL,zorder=1)
        ax.add_patch(rect_barra)

        # Texto identificador de la zona (en blanco, arriba a la izquierda de su barra azul)
        ax.text(0.2, y_offset + 0.15, f"Zona {area.name} — {area.type}",
                fontsize=10, fontweight="bold", color="white", va="center", zorder=2)

        # 2. DIBUJAR LOS RECTÁNGULOS DE LAS GATES DENTRO DE LA BARRA
        x_gate = 0
        row_shift = 0

        for gate in area.gates:
            if x_gate >= max_gates_per_row:
                x_gate = 0
                row_shift -= 0.7  #Salt de línia si hi ha moltes moltes portes a la mateixa zona

            #Coordenades i proporcions del rectangle de la porta
            rect_w = 1.3
            rect_h = 0.45
            gate_x = 0.2 + (x_gate * 1.6)
            gate_y = y_offset - 0.35 + row_shift

            # Color de fons del rectangle segons l'estat d'ocupació
            color_rect = COLOR_OCCUPIED if gate.occupied else COLOR_FREE


            rect_gate = patches.Rectangle((gate_x, gate_y),rect_w,rect_h,linewidth=1,edgecolor="white",
                                          facecolor=color_rect,zorder=3)
            ax.add_patch(rect_gate)

            # 3. TEXTO DEL NOMBRE DE LA GATE DENTRO DEL RECTÁNGULO
            #text del nom de la gate dins del rectangle: Si per exemple és T1BAG1 passa a G1
            display_name = gate.name.split("G")[-1] if "G" in gate.name else gate.name
            display_name = f"G{display_name}"

            # Colocar el text de la porta just en el centre
            ax.text(gate_x + (rect_w / 2),gate_y + (rect_h / 2),display_name,fontsize=8,fontweight="bold",
                color=COLOR_TEXT_GATE,ha="center",va="center",zorder=4)

            if gate.occupied and gate.aircraft_id:
                ax.text(gate_x + (rect_w / 2),gate_y - 0.15,gate.aircraft_id,fontsize=7,fontweight="bold",
                    color="#FFFFCC",  # Amarillo claro para que resalte sobre el fondo azul oscuro
                    ha="center",va="top",zorder=4)

            x_gate += 1

        y_offset -= (barra_alto + 0.4)

    #Configuració final de límits i estètica del llenç gràfic
    ax.set_xlim(-0.3, 11.8)
    ax.set_ylim(y_offset + 0.2, 1.2)
    ax.axis("off")

    # Títol principal de la part superior
    ax.text(0, 0.92, f"PANELL DE PORTES — TERMINAL {terminal_filtro}",
            fontsize=12, fontweight="bold", color="#2C3E50", va="center")

    fig.tight_layout()
    mostrar_plot_en_frame(fig)
    return fig