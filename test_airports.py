from airport import *

airport=Airport ("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport (airport)

airports=LoadAirports("Airports.txt")

i=0
while i<len(airports):
    SetSchengen(airports[i])
    i+=1

SaveSchengenAirports(airports, 'SchengenAirports.txt')

airport_existe=Airport ("LEBL", 41.297445, 2.0832941)

print(len(airports))
AddAirport(airports,airport_existe)
print(len(airports))

RemoveAirport(airports,"LEBL")
print(len(airports))
RemoveAirport(airports, "ZZFR")
print(len(airports))

PlotAirports(airports)
MapAirports(airports)