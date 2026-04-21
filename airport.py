import matplotlib.pyplot as plt#Permet dibuixar gràfics (per poder fer el gràfic de barres que necessitem.    #Permet generar arxius en el format que utilitza Google Earth, per tal de poder-los anar ficant al mapa.
import os#Permet interactuar amb els nostres respectius ordinadors, de manera virutal (internament).

xml_init = '''\
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="1">
        <Style id="1">
            <IconStyle id="5">
                <color>ffff0000</color>
                <colorMode>normal</colorMode>
                <scale>1</scale>
                <heading>0</heading>
                <Icon id="6">
                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
        </Style>
        <Style id="2">
            <IconStyle id="10">
                <color>ff0000ff</color>
                <colorMode>normal</colorMode>
                <scale>1</scale>
                <heading>0</heading>
                <Icon id="11">
                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
        </Style>
'''


class Airport:#Aquesta classe, serveix perquè, cada vegada que llegim el fitxer, crearà un aerport per cada línia, amb la seva respectiva informació.
    def __init__(self, ICAO, latitud, longitud):
        self.ICAO=ICAO
        self.latitud=float(latitud)
        self.longitud=float(longitud)
        self.Schengen=False

def IsSchengenAirport(ICAO):#Rep un codi ICAO, i busca si les 2 primeres lletres d'aquest codi formen part de la Schengenlist.
    Schengenlist = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM','EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
    prefix=ICAO[:2]
    i=0
    encontrado=False
    while i<len(Schengenlist) and not encontrado:
        if prefix==Schengenlist[i]:
            encontrado=True
        else:
            i=i+1
    return encontrado

def SetSchengen(airport):#Actualitza el boleà Schengen d'un aeroport en concret.
    airport.Schengen=IsSchengenAirport(airport.ICAO)

def PrintAirport(airport):#Mostra per pantalla totes les dades de l'aeroport en qüestió.
    print("Dades de l'aeroport:")
    print("ICAO:", airport.ICAO)
    print("Coordenades:", (airport.latitud,airport.longitud))
    print("Schengen:", airport.Schengen)

def latitud_decimal(coord_str):#Conversió de les coordenades (latitud), a decimal.
    hemisferi = coord_str[0]
    graus = float(coord_str[1:3])
    minuts = float(coord_str[3:5])
    segons = float(coord_str[5:7])

    decimal = graus + (minuts / 60.0) + (segons / 3600.0)
    if hemisferi == 'S':
        decimal = -decimal
    return decimal

def longitud_decimal(coord_str):#Conversió de les coordenades (longitud), a decimal.
    hemisferi = coord_str[0]
    graus = float(coord_str[1:4])
    minuts = float(coord_str[4:6])
    segons = float(coord_str[6:8])

    decimal = graus + (minuts / 60.0) + (segons / 3600.0)
    if hemisferi == 'W':
        decimal = -decimal
    return decimal

def latitud_string(decimal):#Conversió de les coordenades (latitud), des de decimal cap a format original (text).
    if decimal >= 0:
        hemisferi = "N"
    else:
        hemisferi = "S"

    decimal = abs(decimal)
    graus = int(decimal)
    resta = (decimal - graus) * 60
    minuts = int(resta)
    segons = int(round((resta - minuts) * 60))

    return hemisferi + str(graus).zfill(2) + str(minuts).zfill(2) + str(segons).zfill(2)


def longitud_string(decimal):#Conversió de les coordenades (longitud), des de decimal cap a format original (text).
    if decimal >= 0:
        hemisferi = "E"
    else:
        hemisferi = "W"

    decimal = abs(decimal)
    graus = int(decimal)
    resta = (decimal - graus) * 60
    minuts = int(resta)
    segons = int(round((resta - minuts) * 60))

    return hemisferi + str(graus).zfill(3) + str(minuts).zfill(2) + str(segons).zfill(2)

def LoadAirports(filename):#Obre el fitxer amb tots els aeroports, llegeix cada línia, i va separant les dades.
    airports = []
    try:
        F = open(filename, "r")
        linea = F.readline()
        linea = F.readline()

        while linea != "":
            elements = linea.split()#Elements és el nom que li fiquem a cadascuna de les columnes del fitxer de text.
            if len(elements) == 3:
                codi = elements[0]
                lat = latitud_decimal(elements[1])
                lon = longitud_decimal(elements[2])

                nou_aeroport = Airport(codi, lat, lon)
                airports.append(nou_aeroport)

            linea = F.readline()

        F.close()
        return airports
    except FileNotFoundError:#Si el fitxer no existeix, es retorna una llista buida per evitar que el programa es bloquegi.
        return []

def SaveSchengenAirports(airports, filename):#Obre un fitxer nou em mode "write", repassa la llista d'aeroports, i, en el cas que siguin de l'espai Schengen, converteix les seves coordenades decimals a text de nou.
    if len(airports) == 0:
        return -1

    R = open(filename, "w")
    R.write("CODE LAT LON\n")

    for aeroport in airports:
        if aeroport.Schengen == True:
            lat_str = latitud_string(aeroport.latitud)
            lon_str = longitud_string(aeroport.longitud)
            R.write(aeroport.ICAO + " " + lat_str + " " + lon_str + "\n")

    R.close()
    return 0

def AddAirport(airports,airport):#Busca si l'aeroport ja pertany a la llista i, en cas negatiu, l'afageix a la llista.
    encontrado=False
    i=0
    while i<len(airports) and not encontrado:
        if airports[i].ICAO==airport.ICAO:
            encontrado=True
        else:
            i=i+1

    if not encontrado:
        airports.append(airport)

def RemoveAirport(airports,code):#Busca l'aeroport a la llista. En cas que el trobi, l'esborra, amb la funció "delete".
    i=0
    encontrado=False
    while i<len(airports) and not encontrado:
        if airports[i].ICAO==code:
            encontrado=True
        else:
            i+=1

    if encontrado:
        """
        for j in range(i,len(airports)-1):
            airports[j]=airports[j+1]
        airports=airports[:-1]
        """
        del airports[i]#Per evitar-nos una variable local i haver de redefinir tot el codi, utilitzem delete, tot i que també ho podríem fer com està comentat a dalt
        return 0

    return -1

def PlotAirports(airports):#Fa un recompte de quants aeroports formen part de l'espai Schengen i quants no. Després del bucle "for", s'utilitzen una sèrie de funcions per generar un gràfic de barres.
    schengen=0
    noschengen=0

    for i in airports:
        if i.Schengen:
            schengen = schengen + 1
        else:
            noschengen = noschengen + 1

    plt.bar(["Schengen","No Schengen"], [schengen,noschengen], color=["blue","red"])
    plt.title("Schengen Airports")
    plt.ylabel("Count")
    plt.xlabel("Airports")
    plt.show()

def MapAirports(airports):
    f_out = open("Airports.kml", "w")
    f_out.write(xml_init)

    i=1
    for airport in airports:
        f_out.write('        <Placemark id="' + str(i) + '">\n')
        f_out.write('            <name>' + airport.ICAO + '</name>\n')
        if airport.Schengen:
            f_out.write('            <styleUrl>#1</styleUrl>\n')
        else:
            f_out.write('            <styleUrl>#2</styleUrl>\n')
        f_out.write('            <Point id="' + str(i) + '">\n')
        f_out.write('                <coordinates>' + str(airport.longitud) +',' + str(airport.latitud) + ',0.0</coordinates>\n')
        f_out.write('            </Point>\n')
        f_out.write('        </Placemark>\n')
        i+=1
    f_out.write('    </Document>\n')
    f_out.write('</kml>')
    f_out.close()
    os.startfile('Airports.kml')#Executa Google Earth a l'ordinador.