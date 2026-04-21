import matplotlib.pyplot as plt
import os
import math

class Aircraft:#Aquesta classe, serveix perquè, cada vegada que llegim el fitxer, crearà un aerport per cada línia, amb la seva respectiva informació.
    def __init__(self, aircraft_id, company, airport_origin, land_time):
        self.aircraft_id=aircraft_id
        self.company=company
        self.airport_origin=airport_origin
        self.land_time=land_time

def format_temps_valid(temps_str):
    if ":" not in temps_str:
        return False

    partstemps=temps_str.split(":")
    if len(partstemps) != 2:
        return False

    try:
        hores = int(partstemps[0])
        minuts = int(partstemps[1])
        if 0 <= hores <= 23 and 0 <=minuts<=59:
            return True
        else:
            return False
    except ValueError:#Per si, en comptes de números, hi haguessin lletres per error, per exemple.
        return False

def LoadArrivals (filename):#Permet carregar el fitxer amb els vols i classificar-ne el contingut
    aircrafts = []

    try:
        F = open(filename, "r")
        F.readline()
        linea = F.readline()
        while linea != "":
            elements = linea.split(" ")

            if len(elements) == 4:#Comprovem que la línia tingui exactament les 4 columnes esperades
                codi_avio = elements[0]
                origen = elements[1]
                hora_arribada = elements[2]
                aerolinia = elements[3].strip()

                if format_temps_valid(hora_arribada):#Comprovem que l'hora sigui vàlida amb la nostra funció d'ajuda

                    #Si l'hora és, per exemple, "0:04", li afegim un 0 al davant, per tal que quedi: ("00:04"), ja que l'enunciat demana que hi hagi un total de 5 caràcters, en format (hh:mm).
                    if len(hora_arribada) == 4:
                        hora_arribada = "0" + hora_arribada

                    #Creem l'avió i l'afegim a la llista
                    nou_avio = Aircraft(codi_avio, aerolinia, origen, hora_arribada)
                    aircrafts.append(nou_avio)

            linea = F.readline()

        F.close()
        return aircrafts

    except FileNotFoundError:
        return []#Si el fitxer no existeix, doncs retorna una llista buida.

def PlotArrivals (aircrafts):#Grafiquem la freqüència d'arribada per cada hora
    if len(aircrafts) == 0:    #Comprovació d'error, com ens demana l'enunciat, per si la llista està buida.
        print("Error. La llista d'avions està buida, i, per tant, NO es pot generar el gràfic.")
        return -1

    vols_cada_hora = [0] * 24#Creem una llista amb 24 zeros per comptar els vols de cada hora (posicions 0 a 23).

    for aircraft in aircrafts:
        hora_avio = int(aircraft.land_time[:2])#L'hora la tenim en format "hh:mm" (ex: "03:14"). Tallem els dos primers caràcters [:2] i els convertim a número enter, a través de int.
        vols_cada_hora[hora_avio]+= 1#Sumem 1 a la posició corresponent d'aquella hora.

    hores_del_dia = list(range(24))#Generació del gràfic. Crea una llista del 0 al 23 per a l'eix X (eix de les hores).

    plt.bar(hores_del_dia, vols_cada_hora, color="skyblue", edgecolor="black")
    plt.title("Freqüència d'arribades per hora a LEBL")
    plt.xlabel("Hora del dia (00h - 23h)")
    plt.ylabel("Nombre d'avions")
    plt.xticks(hores_del_dia)#Força que es mostrin tots els números del 0 al 23 a sota

    plt.show()

    return 0

def SaveFlights(aircrafts,filename):
    if len(aircrafts)==0:
        print("La llista està buida")
        return -1
    try:
        F = open(filename, "w")

        i=0
        while i < len(aircrafts):
            if (aircrafts[i].aircraft_id != "" and
                    aircrafts[i].airport_origin != "" and
                    aircrafts[i].land_time != "" and
                    aircrafts[i].company != ""):

                codi_avio = aircrafts[i].aircraft_id
                origen = aircrafts[i].airport_origin
                hora_arribada = aircrafts[i].land_time
                aerolinia = aircrafts[i].company

                F.write(codi_avio + " " + origen + " " + hora_arribada + " " + aerolinia + "\n")

            else:
                #Aquesta part de comprovar que existeixin els 4 camps no caldria, ja hem descartat les línies errònies a la funció LoadAirports
                F.write("- - - -\n")

            i = i + 1
        F.close()

    except FileNotFoundError:
        print("no existeix el fitxer")

    return 0

def PlotAirlines(aircrafts):#Grafiquem el nombre de vols per aerolinia.

    if len(aircrafts) == 0:
        print("La llista està buida, no es pot fer el gràfic.")
        return -1

    aerolinies = []#Llista de noms d'aerolínies
    comptador = []#Llista amb el nombre de vols per aerolínia

    i = 0
    while i < len(aircrafts):
        companyia = aircrafts[i].company
        encontrado = False
        j = 0

        while j < len(aerolinies):
            if aerolinies[j] == companyia:
                comptador[j] = comptador[j] + 1
                encontrado = True
            j = j + 1

        if not encontrado:
            aerolinies.append(companyia)
            comptador.append(1)

        i = i + 1

    plt.bar(aerolinies, comptador)
    plt.title("Nombre de vols per aerolínia")
    plt.xlabel("Aerolínia")
    plt.xticks(rotation=90, fontsize=8)
    plt.ylabel("Nombre de vols")
    plt.show()

    return 0

def PlotFlightsType(aircrafts):#Graficar i classificar els vols en funció de que provinguin de l'espai schengen o no.
    if len(aircrafts) == 0:
        print("Error. La llista està buida.")
        return -1

    schengen_list = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
'BI','LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES',
'LS']

    vols_schengen = 0
    vols_no_schengen = 0

    i=0
    while i < len(aircrafts):
        origen = aircrafts[i].airport_origin
        prefix=origen[:2]

        if prefix in schengen_list:
            vols_schengen += 1
        else:
            vols_no_schengen += 1

        i+=1

    #Gràfic de barres apilades
    etiquetes = ["Arribades"]

    plt.bar(etiquetes, [vols_schengen], label="Schengen")
    plt.bar(etiquetes, [vols_no_schengen], bottom=[vols_schengen], label="No Schengen")

    plt.title("Tipus de vols (Schengen vs No Schengen)")
    plt.ylabel("Nombre de vols")
    plt.legend()

    plt.show()

    return 0

def MapFlights(aircrafts, airports):#Mostra els vols els vols al Google Earth
    if len(aircrafts) == 0 or len(airports) == 0:
        print("Error. No hi ha prou dades.")
        return -1

    try:
        F = open("flights.kml", "w")

        F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
        F.write("<Document>\n")

        lat_lebl = 0
        lon_lebl = 0

        i = 0
        while i < len(airports):
            if airports[i].ICAO == "LEBL":
                lat_lebl = airports[i].latitud
                lon_lebl = airports[i].longitud
            i = i + 1

        schengen_list = ['LO','EB','LK','LC','EK','EE','EF','LF','ED','LG','EH','LH',
                         'BI','LI','EV','EY','EL','LM','EN','EP','LP','LZ','LJ','LE','ES','LS']

        #A continuació, recorrem els vols.
        i = 0
        while i < len(aircrafts):
            origen = aircrafts[i].airport_origin

            #Buscar coordenades d'origen
            j = 0
            lat_origen = 0
            lon_origen = 0

            while j < len(airports):
                if airports[j].ICAO == origen:
                    lat_origen = airports[j].latitud
                    lon_origen = airports[j].longitud
                j += 1

            #Color
            prefix = origen[:2]

            if prefix in schengen_list:
                color = "ff00ff00"   # Color verd
            else:
                color = "ff0000ff"   # Color vermell

            #Escriure línies relacionades amb Google Earth
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

            i = i + 1

        #Tancar KML
        F.write("</Document>\n")
        F.write("</kml>\n")

        F.close()

        print("Fitxer flights.kml creat correctament.")
        os.startfile('flights.kml')

    except:
        print("Error escrivint el fitxer.")

def Haversine(lat1, lon1, lat2, lon2):

    R = 6371  #Radi de la Terra (en quilòmetres)

    #Passar latituds i longituds a Radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distancia = R * c

    return distancia

def LongDistanceArrivals(aircrafts, airports):#Classifica els vols que tenen una distància superior als 2000km respecte LEBL

    resultat = []

    if len(aircrafts) == 0 or len(airports) == 0:
        return resultat

    #Busca LEBL
    lat_lebl = 0
    lon_lebl = 0

    i = 0
    while i < len(airports):
        if airports[i].ICAO == "LEBL":
            lat_lebl = airports[i].latitud
            lon_lebl = airports[i].longitud
        i+=1

    #Recórre els vols
    i = 0
    while i < len(aircrafts):
        origen = aircrafts[i].airport_origin

        #Busca coordenades de l'origen
        j = 0
        encontrado = False
        lat_origen = 0
        lon_origen = 0

        while j < len(airports) and not encontrado:
            if airports[j].ICAO == origen:
                lat_origen = airports[j].latitud
                lon_origen = airports[j].longitud
                encontrado = True
            j+=1

        #Càlcul de la distància
        dist = Haversine(lat_origen, lon_origen, lat_lebl, lon_lebl)

        #Si la distància és major a 2000 km s'afegeix a la llista.
        if dist > 2000:
            resultat.append(aircrafts[i])

        i = i + 1

    return resultat

#Secció de prova (test_aircraft)
import airport
if __name__ == "__main__":
    aircrafts = LoadArrivals ("arrivals.txt") #Crea la llista de aircrafts a partir del fitxer
    PlotArrivals (aircrafts) #Executa el gràfic de freüència d'arrivades per hora
    SaveFlights(aircrafts, "arrivals_out.txt") #Comprovem que crea un nou fitxer sense errors
    PlotAirlines(aircrafts) #Fa el gràfic dels vols per aerolínia
    PlotFlightsType(aircrafts) #Realitza un gràfic dels vols que arriven de països Schengen o No Schengen
    airports = airport.LoadAirports("Airports.txt")
    MapFlights(aircrafts, airports)
    aircrafts_mes_2000=LongDistanceArrivals(aircrafts, airports)
    print(aircrafts_mes_2000)