class Gate:
    def __init__(self,name,occupied,aircraft_id):
        self.name=name
        self.occupied=occupied
        self.aircraft_id=aircraft_id

class BoardingArea:
    def __init__(self,name,area_type):
        self.name=name
        self.area_type=area_type
        self.gates=[]

class Terminal:
    def __init__(self,name):
        self.name=name
        self.boarding_areas=[]
        self.airlines=[]

class BarcelonaAP:
    def __init__(self,code):
        self.code=code
        self.terminals=[]

class Aircraft:
    def __init__(self,aircraft_id,company,airport_origin):
        self.aircraft_id=aircraft_id
        self.company=company
        self.airport_origin=airport_origin

def SetGates(area,init_gate,end_gate,prefix):
    if end_gate<=init_gate:
        return -1

    area.gates=[]
    i=init_gate

    while i<=end_gate:
        gate_name=prefix + str(i)
        new_gate=Gate(gate_name,False,"")
        area.gates.append(new_gate)
        i=i+1
    return 0

def LoadAirlines(terminal,t_name):
    filename = t_name + "_Airlines.txt"
    try:
        F=open(filename,"r")
        new_airlines=[]
        line=F.readline()
        while line!="":
            elements=line.split("\t")
            if len(elements)>=2:
                code = elements[-1].strip()
                new_airlines.append(code)
            line=F.readline()
        F.close()
        terminal.airlines=new_airlines
        return 0
    except FileNotFoundError:
        return -1

def LoadAirportStructure(filename):
    try:
        F=open(filename,"r")
        line=F.readline().strip()
        elements=line.split()
        airport_code=elements[0]
        airport=BarcelonaAP(airport_code)
        num_terminals=int(elements[1])

        t=0
        while t<num_terminals:
            line=F.readline().strip()
            elements=line.split()
            terminal_name=elements[1]
            num_areas=int(elements[2])
            terminal=Terminal(terminal_name)
            # Load airlines
            result=LoadAirlines(terminal, terminal_name)

            if result==-1:
                F.close()
                return -1

            i=0
            while i<num_areas:
                line=F.readline().strip()
                elements=line.split()
                area_name=elements[1]
                area_type=elements[2]
                init_gate=int(elements[4])
                end_gate=int(elements[6])
                area=BoardingArea(area_name,area_type)
                prefix=terminal_name + area_name + "G"
                result=SetGates(area,init_gate,end_gate,prefix)
                if result==-1:
                    F.close()
                    return -1
                terminal.boarding_areas.append(area)
                i=i+1
            airport.terminals.append(terminal)
            t=t+1
        F.close()
        return airport

    except FileNotFoundError:
        return -1

def GateOccupancy(bcn):
    result=[]
    i=0
    while i<len(bcn.terminals):
        terminal=bcn.terminals[i]
        j=0
        while j<len(terminal.boarding_areas):
            area=terminal.boarding_areas[j]
            k=0
            while k<len(area.gates):
                gate=area.gates[k]
                gate_info=[]
                gate_info.append(gate.name)
                if gate.occupied:
                    gate_info.append("Occupied")
                    gate_info.append(gate.aircraft_id)
                else:
                    gate_info.append("Free")
                    gate_info.append("-")
                result.append(gate_info)
                k=k+1
            j=j+1
        i=i+1
    return result

def IsAirlineInTerminal(terminal,name):
    if name=="":
        return False

    if len(terminal.airlines)==0:
        return False
    i=0
    while i<len(terminal.airlines):
        if terminal.airlines[i]==name:
            return True
        i=i+1
    return False

def SearchTerminal(bcn,name):
    if name=="":
        return ""

    i=0
    while i<len(bcn.terminals):
        terminal=bcn.terminals[i]
        found=IsAirlineInTerminal(terminal,name)
        if found:
            return terminal.name
        i=i+1
    return ""

def AssignGate(bcn,aircraft):
    terminal_name=SearchTerminal(bcn,aircraft.company)
    if terminal_name=="":
        return -1

    schengen_list=['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY',
    'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']

    prefix=aircraft.airport_origin[:2]
    schengen=False
    i=0
    encontrado=False
    while i<len(schengen_list) and not encontrado:
        if prefix==schengen_list[i]:
            encontrado=True
            schengen=True
        i+=1
    i=0
    while i<len(bcn.terminals):
        terminal=bcn.terminals[i]
        if terminal.name==terminal_name:
            j=0
            while j<len(terminal.boarding_areas):
                area=terminal.boarding_areas[j]
                correct_area=False
                if schengen and area.area_type=="Schengen":
                    correct_area=True
                if not schengen and area.area_type=="non-Schengen":
                    correct_area=True
                if correct_area:
                    k=0
                    while k<len(area.gates):
                        gate=area.gates[k]
                        if gate.occupied==False:
                            gate.occupied=True
                            gate.aircraft_id=aircraft.aircraft_id
                            return gate.name
                        k=k+1
                j=j+1
        i=i+1
    return -1

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