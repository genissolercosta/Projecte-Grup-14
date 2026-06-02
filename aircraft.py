import matplotlib.pyplot as plt
import os
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#FUNCIONALITAT EXTRA
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

class Aircraft:#Aquesta classe, serveix perquè, cada vegada que llegim el fitxer, crearà un aerport per cada línia, amb la seva respectiva informació.
    def __init__(self, aircraft_id, company, airport_origin, land_time, destination_airport, departure_time):
        self.aircraft_id=aircraft_id
        self.company=company
        self.airport_origin=airport_origin
        self.land_time=land_time
        self.destination_airport=destination_airport
        self.departure_time=departure_time

#Amb aquestes funcions comprovarem que el format de totes les dades dels fitxers siguin correctes
def format_codi_valid(aircraft):
    if (len(aircraft)==5 or len(aircraft)==6) and aircraft.upper():
        return True
    else:
        return False

def format_airport_valid(airport):
    if len(airport)==4 and airport.isupper():
        return True
    else:
        return False

def format_temps_valid(temps_str):
    if ":" not in temps_str:
        return False
    partstemps=temps_str.split(":")
    if len(partstemps)!=2:
        return False
    try:
        hores=int(partstemps[0])
        minuts=int(partstemps[1])
        if 0<=hores<=23 and 0<=minuts<=59:
            return True
        else:
            return False
    except ValueError:#Per si, en comptes de números, hi haguessin lletres per error, per exemple.
        return False

def format_aerolinia_valid(aerolinia):
    if len(aerolinia)==3 and aerolinia.upper():
        return True
    else:
        return False

def LoadArrivals (filename):#Permet carregar el fitxer amb els vols i classificar-ne el contingut
    arrivals=[]
    errors=[]
    try:
        F=open(filename, "r")#Obril el fitxer
        F.readline()#Obiem la primera fila
        linea=F.readline()#Llegim la primera fila
        linea_num=2
        while linea != "":#Llegim les linies en bucle fins al final de l'arxiu
            elements=linea.split(" ")
            if len(elements) != 4: #Comprovem que la línia tingui exactament les 4 columnes esperades
                errors.append("Línia mal format ignorada: " + linea.strip())
                linea = F.readline()
                linea_num += 1
                continue
            codi_avio=elements[0]
            origen=elements[1]
            hora_arribada=elements[2]
            aerolinia=elements[3].strip()
            if format_temps_valid(hora_arribada):#Comprovem que l'hora sigui vàlida amb la nostra funció d'ajuda
                #Si l'hora és, per exemple, "0:04", li afegim un 0 al davant, per tal que quedi: ("00:04"), ja que l'enunciat demana que hi hagi un total de 5 caràcters, en format (hh:mm).
                if len(hora_arribada)==4:
                    hora_arribada="0"+hora_arribada
                if not format_codi_valid(codi_avio):
                    errors.append(f"Línia {linea_num}: codi avió invàlid: {codi_avio}")
                    codi_avio=""
                if not format_airport_valid(origen):
                    errors.append(f"Línia {linea_num}: aeroport origen invàlid: {origen}")
                    origen=""
                if not format_aerolinia_valid(aerolinia):
                    errors.append(f"Línia {linea_num}: aerolínia invàlida: {aerolinia}")
                    aerolinia=""
                #Creem l'avió i l'afegim a la llista
                nou_avio = Aircraft(codi_avio, aerolinia, origen, hora_arribada, None, None)
                arrivals.append(nou_avio)
            linea=F.readline()
            linea_num += 1
        F.close()#Tanquem el fitxer
        return arrivals, errors

    except FileNotFoundError:
        return []#Si el fitxer no existeix, doncs retorna una llista buida.

def PlotArrivals (aircrafts):#Grafiquem la freqüència d'arribada per cada hora
    if len(aircrafts) == 0:    #Comprovació d'error, com ens demana l'enunciat, per si la llista està buida.
        print("Error. La llista d'avions està buida, i, per tant, NO es pot generar el gràfic.")
        return -1

    vols_cada_hora=[0]*24#Creem una llista amb 24 zeros per comptar els vols de cada hora (posicions 0 a 23).

    for i in range (len(aircrafts)):
        aircraft=aircrafts[i]
        if aircraft.land_time!="":
            hora_avio=int(aircraft.land_time[:2])#L'hora la tenim en format "hh:mm" (ex: "03:14"). Tallem els dos primers caràcters [:2] i els convertim a número enter, a través de int.
            vols_cada_hora[hora_avio]+= 1#Sumem 1 a la posició corresponent d'aquella hora.
    hores_del_dia=list(range(24))#Generació del gràfic. Crea una llista del 0 al 23 per a l'eix X (eix de les hores).
    fig, ax=plt.subplots(figsize=(6,3))
    fig.tight_layout()
    ax.bar(hores_del_dia,vols_cada_hora,color="skyblue",edgecolor="black")
    ax.set_title("Freqüència d'arribades per hora a LEBL")
    ax.set_xlabel("Hora del dia (00h - 23h)")
    ax.set_ylabel("Nombre d'avions")
    ax.set_xticks(hores_del_dia)
    fig.tight_layout()
    mostrar_plot_en_frame(fig)
    plt.show()
    return fig

def SaveFlights(aircrafts,filename):
    if len(aircrafts)==0:
        print("La llista està buida")
        return -1
    try:
        F=open(filename, "w")#Obrim el fitxer desitjat per escriure-hi
        i=0
        while i<len(aircrafts): #Només afegim les dades que estiguin en el format esperat per evitar errors
            if (aircrafts[i].aircraft_id != "" and aircrafts[i].airport_origin != "" and
                    aircrafts[i].land_time != "" and aircrafts[i].company != ""):
                codi_avio=aircrafts[i].aircraft_id
                origen=aircrafts[i].airport_origin
                hora_arribada=aircrafts[i].land_time
                aerolinia=aircrafts[i].company
            F.write(codi_avio + " " + origen + " " + hora_arribada + " " + aerolinia + "\n")
            i = i + 1
        F.close()#Tanquem el fitxer

    except FileNotFoundError:
        print("no existeix el fitxer")
    return 0

def PlotAirlines(aircrafts):#Grafiquem el nombre de vols per aerolinia.

    if len(aircrafts)==0:
        print("La llista està buida, no es pot fer el gràfic.")
        return -1

    aerolinies=[]#Llista de noms d'aerolínies
    comptador=[]#Llista amb el nombre de vols per aerolínia
    i=0
    while i<len(aircrafts):
        companyia=aircrafts[i].company
        encontrado=False
        j=0
        while j<len(aerolinies):
            if aerolinies[j]==companyia:#Si troba la companyia a la llista afegix +1 vol
                comptador[j]=comptador[j]+1
                encontrado=True
            j=j+1
        if not encontrado:
            aerolinies.append(companyia)#Si no hi ha l'aerolinia anteriorment a la llista l'afegeix i li fa un vol
            comptador.append(1)
        i=i+1

    fig, ax = plt.subplots(figsize=(6, 3))#Generem el gràfic
    fig.tight_layout()
    ax.bar(aerolinies, comptador)
    ax.set_title("Nombre de vols per aerolínia")
    ax.set_xlabel("Aerolínia")
    ax.set_ylabel("Nombre de vols")
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=8)
    fig.tight_layout()
    mostrar_plot_en_frame(fig)
    plt.show()
    return fig

def PlotFlightsType(aircrafts):#Graficar i classificar els vols en funció de que provinguin de l'espai schengen o no.
    if len(aircrafts)==0:
        print("Error. La llista està buida.")
        return -1

    schengen_list = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
'BI','LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']

    vols_schengen=0
    vols_no_schengen=0
    i=0
    while i<len(aircrafts):
        origen=aircrafts[i].airport_origin#L'indicador del schengen son les 2 primeres lletres del codi
        prefix=origen[:2]
        encontrado=False
        j=0
        while j<len(schengen_list) and not encontrado:#Búsqueda per veure si està en schengen
            if prefix==schengen_list[j]:
                encontrado=True
            j=j+1
        if encontrado:
            vols_schengen+=1
        else:
            vols_no_schengen+=1
        i+=1

    #Gràfic de barres apilades
    etiquetes = ["Arribades"]

    fig, ax = plt.subplots(figsize=(6, 3))
    fig.tight_layout()
    ax.bar(etiquetes,[vols_schengen],label="Schengen")
    ax.bar(etiquetes,[vols_no_schengen],bottom=[vols_schengen],label="No Schengen")
    ax.set_title("Tipus de vols (Schengen vs No Schengen)")
    ax.set_ylabel("Nombre de vols")
    ax.legend()
    fig.tight_layout()
    mostrar_plot_en_frame(fig)
    plt.show()
    return fig

def MapFlights(aircrafts, airports):#Mostra els vols els vols al Google Earth
    if len(aircrafts)==0 or len(airports)==0:
        print("Error. No hi ha prou dades.")
        return -1

    try:
        F=open("flights.kml", "w")
        F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
        F.write("<Document>\n")

        lat_lebl=0
        lon_lebl=0
        i=0
        while i<len(airports):
            if airports[i].ICAO=="LEBL":
                lat_lebl=airports[i].latitud
                lon_lebl=airports[i].longitud
            i=i+1

        schengen_list=['LO','EB','LK','LC','EK','EE','EF','LF','ED','LG','EH','LH',
                         'BI','LI','EV','EY','EL','LM','EN','EP','LP','LZ','LJ','LE','ES','LS']

        #A continuació, recorrem els vols.
        i=0
        while i<len(aircrafts):
            origen=aircrafts[i].airport_origin
            #Buscar coordenades d'origen
            j=0
            lat_origen=0
            lon_origen=0
            while j<len(airports):
                if airports[j].ICAO==origen:
                    lat_origen=airports[j].latitud
                    lon_origen=airports[j].longitud
                j=j+1
            #Color
            prefix=origen[:2]
            encontrado=False
            j=0
            while j<len(schengen_list) and not encontrado:
                if prefix==schengen_list[j]:
                    encontrado=True
                j=j+1
            if encontrado:
                color = "ff00ff00"#Color verd
            else:
                color = "ff0000ff"#Color vermell

            #Escriure línies relacionades amb Google Earth
            F.write("<Placemark>\n")
            F.write("<Style><LineStyle><color>" + color + "</color></LineStyle></Style>\n")
            F.write("<LineString>\n")
            F.write("<coordinates>\n")

            #(Longitud i Latitud)
            F.write(str(lon_origen) + "," + str(lat_origen) + ",0 ")
            F.write(str(lon_lebl) + "," + str(lat_lebl) + ",0\n")

            F.write("</coordinates>\n")
            F.write("</LineString>\n")
            F.write("</Placemark>\n")
            i=i+1
        #Tancar KML
        F.write("</Document>\n")
        F.write("</kml>\n")
        F.close()
        print("Fitxer flights.kml creat correctament.")
        os.startfile('flights.kml')

    except:
        print("Error escrivint el fitxer.")

def Haversine(lat1, lon1, lat2, lon2):

    R = 6371 #Radi de la Terra (en quilòmetres)
    #Passar latituds i longituds a Radians
    lat1=math.radians(lat1)
    lon1=math.radians(lon1)
    lat2=math.radians(lat2)
    lon2=math.radians(lon2)

    dlat=lat2-lat1
    dlon=lon2-lon1
    a=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c=2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    distancia=R*c

    return distancia

def LongDistanceArrivals(aircrafts, airports):#Classifica els vols que tenen una distància superior als 2000km respecte LEBL

    resultat=[]
    if len(aircrafts)==0 or len(airports)==0:
        return resultat

    #Busca LEBL
    lat_lebl=0
    lon_lebl=0

    i=0
    while i<len(airports):
        if airports[i].ICAO == "LEBL":
            lat_lebl=airports[i].latitud
            lon_lebl=airports[i].longitud
        i+=1

    #Recórre els vols
    i=0
    while i<len(aircrafts):
        origen=aircrafts[i].airport_origin
        #Busca coordenades de l'origen
        j=0
        encontrado=False
        lat_origen=0
        lon_origen=0

        while j<len(airports) and not encontrado:
            if airports[j].ICAO==origen:
                lat_origen=airports[j].latitud
                lon_origen=airports[j].longitud
                encontrado=True
            j+=1

        #Càlcul de la distància
        dist=Haversine(lat_origen, lon_origen, lat_lebl, lon_lebl)
        #Si la distància és major a 2000 km s'afegeix a la llista.
        if dist>2000:
            resultat.append(aircrafts[i])
        i=i+1

    return resultat


def MapLongDistanceFlights(aircrafts, airports):#Mostra els vols de llarga distància (>2000km) al Google Earth
    if len(aircrafts)==0 or len(airports)==0:
        print("Error. No hi ha prou dades.")
        return -1

    try:
        #Canviem el nom del fitxer a un de específic per a llarga distància
        F=open("long_distance_flights.kml", "w")
        F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
        F.write("<Document>\n")
        #Buscar coordenades de Barcelona (LEBL)
        lat_lebl=0
        lon_lebl=0
        i=0
        while i<len(airports):
            if airports[i].ICAO == "LEBL":
                lat_lebl=airports[i].latitud
                lon_lebl=airports[i].longitud
            i=i+1

        schengen_list = ['LO','EB','LK','LC','EK','EE','EF','LF','ED','LG','EH','LH',
                         'BI','LI','EV','EY','EL','LM','EN','EP','LP','LZ','LJ','LE','ES','LS']

        #Recorrem els vols
        i=0
        while i<len(aircrafts):
            origen=aircrafts[i].airport_origin

            #Buscar coordenades d'origen
            j=0
            lat_origen=0
            lon_origen=0

            while j<len(airports):
                if airports[j].ICAO==origen:
                    lat_origen=airports[j].latitud
                    lon_origen=airports[j].longitud
                j=j+1

            #Calculem la distància entre l'origen i LEBL fent servir Haversine
            distancia=Haversine(lat_origen, lon_origen, lat_lebl, lon_lebl)

            #Només escrivim al KML si la distància és superior a 2000 km
            if distancia>2000:
                # Color
                prefix=origen[:2]
                encontrado=False
                j=0
                while j<len(schengen_list) and not encontrado:
                    if prefix==schengen_list[j]:
                        encontrado=True
                    j=j+1
                if encontrado:
                    color="ff00ff00"#Color verd (Schengen > 2000km, ex: Canàries, etc.)
                else:
                    color="ff0000ff"#Color vermell (Internacionals llunyans)
                # Escriure línies relacionades amb Google Earth
                F.write("<Placemark>\n")
                F.write("<Style><LineStyle><color>" + color + "</color></LineStyle></Style>\n")
                F.write("<LineString>\n")
                F.write("<coordinates>\n")

                # Part important (Longitud i Latitud)
                F.write(str(lon_origen) + "," + str(lat_origen) + ",0 ")
                F.write(str(lon_lebl) + "," + str(lat_lebl) + ",0\n")

                F.write("</coordinates>\n")
                F.write("</LineString>\n")
                F.write("</Placemark>\n")

            i=i+1

        # Tancar KML
        F.write("</Document>\n")
        F.write("</kml>\n")

        F.close()

        print("Fitxer long_distance_flights.kml creat correctament.")
        os.startfile('long_distance_flights.kml')

    except:
        print("Error escrivint el fitxer.")

def LoadDepartures(filename):#De la mateixa manera que hem carregat els arrivals, carreguem els departures
    departures=[]
    errors=[]
    try:
        F=open(filename, "r")#Obrim el fitzer de departures
        F.readline()#Obiem la primea línia
        linea=F.readline()#Llegim la primera línia
        linea_num=2
        while linea != "":#Mentres no estem al final del fitxer llegim les llínies
            elements = linea.split(" ")
            if len(elements) != 4:  # Comprovem que la línia tingui exactament les 4 columnes esperades
                errors.append("Línia mal format ignorada: " + linea.strip())
                linea = F.readline()
                linea_num += 1
                continue
            codi_avio=elements[0]
            destinacio=elements[1]
            hora_sortida=elements[2]
            aerolinia=elements[3].strip()

            if format_temps_valid(hora_sortida):#Comprovem que l'hora sigui vàlida amb la nostra funció d'ajuda
                #Si l'hora és, per exemple, "0:04", li afegim un 0 al davant, per tal que quedi: ("00:04"), ja que
                #l'enunciat demana que hi hagi un total de 5 caràcters, en format (hh:mm).
                if len(hora_sortida)==4:
                    hora_sortida="0"+hora_sortida
                if not format_codi_valid(codi_avio):
                    errors.append(f"Línia {linea_num}: codi avió invàlid: {codi_avio}")
                    codi_avio = ""
                if not format_airport_valid(destinacio):
                    errors.append(f"Línia {linea_num}: aeroport origen invàlid: {destinacio}")
                    destinacio = ""
                if not format_aerolinia_valid(aerolinia):
                    errors.append(f"Línia {linea_num}: aerolínia invàlida: {aerolinia}")
                    aerolinia = ""

                # Creem l'avió i l'afegim a la llista
                nou_avio = Aircraft(codi_avio, aerolinia, None, None, destinacio, hora_sortida)
                departures.append(nou_avio)
            linea=F.readline()
            linea_num+=1
        F.close()#Tanquem el fitxer
        return departures, errors

    except FileNotFoundError:
        return []#Si el fitxer no existeix, doncs retorna una llista buida.

def TempsArribadaSortidaCompatible(temps_arribada,temps_sortida):#Verifiquem que els temps d'arribada i sortida siguin
    #compatibles
    hora_arribada=int(temps_arribada[:2])
    hora_sortida=int(temps_sortida[:2])
    minuts_arribada=int(temps_arribada[3:])
    minuts_sortida=int(temps_sortida[3:])
    arribada=float(hora_arribada+(minuts_arribada/60))
    sortida=float(hora_sortida+(minuts_sortida/60))
    if arribada<sortida:#Comprobem que l'arribada es doni abans de la sortida, ja que ambdues dades son del mateix dia
        return True
    else:
        return False

def MergeMovements(arrivals, departures):
    if arrivals==[] or departures==[]:
        return -1

    aircrafts=[]
    for i in range(len(arrivals)):
        codi_avio=arrivals[i].aircraft_id
        origen=arrivals[i].airport_origin
        temps_arribada=arrivals[i].land_time
        aerolinia=arrivals[i].company

        j=0
        encontrado=False
        while j<len(departures) and not encontrado:#Busquem els arrivals que també tinguin departure
            if codi_avio==departures[j].aircraft_id:
                destinacio=departures[j].destination_airport
                temps_sortida=departures[j].departure_time
                encontrado=True
            if not encontrado:
                j+=1
        if encontrado and TempsArribadaSortidaCompatible(temps_arribada,temps_sortida):#Imposem que les hores siguin compatibles
            nou_avio=Aircraft(codi_avio,aerolinia,origen,temps_arribada,destinacio,temps_sortida)
            aircrafts.append(nou_avio)

        if not encontrado:#Avió sense sortida el mateix dia
            nou_avio=Aircraft(codi_avio,aerolinia,origen,temps_arribada,None,None)
            aircrafts.append(nou_avio)

    for i in range(len(departures)):
        codi_avio=departures[i].aircraft_id
        destinacio=departures[i].destination_airport
        temps_sortida=departures[i].departure_time
        aerolinia=departures[i].company

        j=0
        encontrado=False
        while j<len(arrivals) and not encontrado:
            if codi_avio==arrivals[j].aircraft_id:
              encontrado=True
            if not encontrado:
                j=j+1

        if not encontrado:#Afegim els avions sense arrivada el mateix dia
            nou_avio=Aircraft(codi_avio, aerolinia, None, None, destinacio, temps_sortida)
            aircrafts.append(nou_avio)

    return aircrafts

def NightAircraft(aircrafts):
    if len(aircrafts)==0:
        return -1

    only_departure_aircrafts=[]
    i=0
    while i<len(aircrafts):
        if aircrafts[i].land_time==None and aircrafts[i].departure_time!=None: #Avions només amb informació de sortida
            only_departure_aircrafts.append(aircrafts[i])
        i=i+1

    return only_departure_aircrafts

#Secció de prova (test_aircraft)
import airport
if __name__ == "__main__":
    arrivals,errors = LoadArrivals ("arrivals.txt") #Crea la llista de aircrafts a partir del fitxer
    PlotArrivals (arrivals) #Executa el gràfic de freüència d'arrivades per hora
    SaveFlights(arrivals, "arrivals_out.txt") #Comprovem que crea un nou fitxer sense errors
    PlotAirlines(arrivals) #Fa el gràfic dels vols per aerolínia
    PlotFlightsType(arrivals) #Realitza un gràfic dels vols que arriven de països Schengen o No Schengen
    airports,errors_airports = airport.LoadAirports("Airports.txt")
    MapFlights(arrivals, airports)
    aircrafts_mes_2000=LongDistanceArrivals(arrivals, airports)
    print(aircrafts_mes_2000)
    departures,error = LoadDepartures("departures.txt")
    aircrafts = MergeMovements(arrivals, departures)
    print(aircrafts)
    night_aircrafts = NightAircraft(aircrafts)
    print(night_aircrafts)