import itertools
import math

class Vol():
    def __init__(self, data):
        self.data = data
        self.flights = []
    
    def creation_vols(self):
        av=0
        dest=0 
        for i in range(self.data["n_destinations"]):
            dest+=1
            for j in range(self.data["destinations"][i]["n_flights"]):
                av+=1
                self.flights.append({
                    "destination": dest,
                    "vol": av,
                    "début du vol": math.inf,
                    "profit": self.data["destinations"][i]["profit"]
                    
                })

# Données
data = {
    "n_destinations": 3,
    "n_aircraft": 2,
    "time_horizon_len": 8,
    "min_utilisation": 0.75,
    "min_spacing": 3,
    "destinations": [
        {"n_flights": 4, "flight_time": 3, "profit": [1, 4, 5, 1, 1, 2, 1, 1]},
        {"n_flights": 4, "flight_time": 2, "profit": [2, 4, 2, 4, 6, 5, 1, 1]},
        {"n_flights": 3, "flight_time": 4, "profit": [1, 7, 1, 4, 1, 2, 1, 1]}
    ],
    "slots": [1, 1, 2, 1, 2, 1, 1, 0]
}

# Exécution
vols = Vol(data)
vols.creation_vols()
print("vols:", vols.flights)



