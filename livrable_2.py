from creation_flotte import Vol
from pulp import *
import numpy as np

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

# Création des vols
avion = Vol(data)
avion.creation_vols()

# Stocker les vols dans une liste
liste_vols = [vol["vol"] for vol in avion.flights]





prob = LpProblem("Maximisation du profit", pulp.LpMaximize)



# Variables
#x = LpVariable.dicts("x", [(k, j, t) for vol in avion.flights 
#                           for k in range(data["n_aircraft"]) 
#                           for j in liste_vols 
#                           for t in range(data["time_horizon_len"])], 
#                          cat="Binary")

x= LpVariable.dicts("x", 
                    [(k, j, t) for vol in avion.flights 
                     for k in range(data["n_aircraft"]) 
                     for j in liste_vols 
                     for t in range(data["time_horizon_len"])], 
                    cat="Binary")

#t_j = début du vol j
t= LpVariable.dicts("t",
                    [j for j in liste_vols],
                    lowBound=0,
                    upBound=data["time_horizon_len"],
                    cat="Continuous")


                     
# Objectif
prob += lpSum([x[(k, j, t)] * avion.flights[j-1]["profit"][t] 
               for j in liste_vols 
               for k in range(data["n_aircraft"]) 
               for t in range(data["time_horizon_len")])


# Contraintes




