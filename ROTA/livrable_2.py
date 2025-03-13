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

delta= 3

# Création des vols
avion = Vol(data)
avion.creation_vols()

# Stocker les vols dans une liste
liste_vols = [vol["vol"] for vol in avion.flights]




def dest(j):
    return avion.flights[j-1]["destination"]

print(dest(8))

# Création du problème
prob = LpProblem("Problème de tournées", LpMaximize)


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
               for t in range(data["time_horizon_len"])])


# Contraintes
# somme sur t somme sur j tq dest(j)=i somme sur k x[k,j,t] <= n_flights[i]

for j in liste_vols:
    prob += lpSum([x[(k, j, t)] for k in range(data["n_aircraft"]) for t in range(data["time_horizon_len"])]) <= avion.flights[j-1]["n_flights"]




# somme sur j et somme sur k x[k,j,t] <= slots[t]
for t in range(data["time_horizon_len"]):
    prob += lpSum([x[(k, j, t)] for j in liste_vols for k in range(data["n_aircraft"])]) <= data["slots"][t]

#pour tout j tel que destination(j) = destination fixée, et t :  somme 
# somme sur k (x[k,j,t] + somme sur t<= u< t + delta  x[k,j,u]) <= 1
for j in liste_vols:
    for t in range(data["time_horizon_len"]):
        prob += lpSum(x[k, j, t] for k in range (data["nb_aircaft"])  + lpSum(x[k, j, u] for k in range (data["nb_aircaft"]) for u in range(t + 1, min(t + delta, T_max))) <= 1



# Contrainte : Utilisation minimale des avions
