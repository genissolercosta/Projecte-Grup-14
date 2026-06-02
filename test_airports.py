from airport import *

airport = Airport ("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport (airport)

airports,errors = LoadAirports("Airports.txt")

for i in range (len(airports)):
    airport=airports[i]
    SetSchengen(airport)

SaveSchengenAirports(airports, 'SchengenAirports.txt')
airport_existe = Airport ("LEBL", 41.297445, 2.0832941)

print(len(airports))
AddAirport(airports,airport_existe)
print(len(airports))

RemoveAirport(airports,"LEBL")
print(len(airports))
RemoveAirport(airports, "ZZFR")
print(len(airports))

PlotAirports(airports)
MapAirports(airports)