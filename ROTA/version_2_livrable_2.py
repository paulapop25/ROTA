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
T_max= data["time_horizon_len"]
m= data["n_aircraft"]
alpha= data["min_utilisation"]
T= range(T_max)


# Création des vols
avion = Vol(data)
avion.creation_vols()
print(avion.flights[1]["début du vol"])

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

x = LpVariable.dicts("x", 
                     [(k, j, t) for k in range(m) 
                     for j in liste_vols 
                     for t in range(T_max)], 
                     cat="Binary")

print(liste_vols)

#t_j = début du vol j
#t = LpVariable.dicts("t", [avion.flights[j-1]["début du vol"] for j in liste_vols], cat="Integer")
t= LpVariable.dicts("t", liste_vols, cat="Integer")
print(t)

# Objectif
prob += lpSum([x[(k, j, t_val)] * avion.flights[j-1]["profit"][t_val] 
               for j in liste_vols 
               for k in range(data["n_aircraft"]) 
               for t_val in range(data["time_horizon_len"])])


# Contraintes
# somme sur t somme sur j tq dest(j)=i somme sur k x[k,j,t] <= n_flights[i]

for i in range(data["n_destinations"]):
    prob += lpSum([x[(k, j, t_val)] for j in liste_vols if dest(j) == i+1 for k in range(data["n_aircraft"]) for t_val in range(data["time_horizon_len"])]) <= data["destinations"][i]["n_flights"]


# Contrainte : somme sur k somme sur t x[k,j,t] <= 1
for k in range(m):
    for t_val in T:
        prob += lpSum(x[k, j, t_val] for j in liste_vols) <= 1

# somme sur j et somme sur k x[k,j,t] <= slots[t]
for t_val in range(data["time_horizon_len"]):
    prob += lpSum([x[(k, j, t_val)] for j in liste_vols for k in range(data["n_aircraft"])]) <= data["slots"][t_val]

#pour tout j tel que destination(j) = destination fixée, et t :  somme 
# somme sur k (x[k,j,t] + somme sur t<= u< t + delta  x[k,j,u]) <= 1
for j in liste_vols:
    for k in range(m):
        for t_val in range(T_max):
            prob += lpSum(x[k, j, t_val]) + lpSum(x[k, j, u] for u in range(t_val + 1, min(t_val + delta, T_max))) <= 1

"""
for j in liste_vols:
    for t in range(data["time_horizon_len"]):
        prob += lpSum(x[k, j, t] for k in range (m) for u in range(t + 1, min(t + delta, T_max))) <= 1

"""

# Contrainte: t_j = t * x[k,j,t]
#for j in liste_vols:
#    for k in range(m):
#        prob += t[j] == lpSum(t * x[k, j, t] for t in T)
# Renommer T pour éviter le conflit avec la variable de décision t[j]
time_range = range(T_max)




# Contrainte d'affectation de t_j
for j in liste_vols:
    for k in range(m):
        print(j)
        #t[j] = avion.flights[j-1]["début du vol"]
        prob += t[j] == lpSum(t_val * x[k, j, t_val] for t_val in time_range), f"Contrainte d'affectation de t_j pour le vol {j} et l'avion {k}"
        
#pb: TypeError: 'int' object is not subscriptable



# Contrainte : Utilisation minimale des avions
for k in range(m):
    #on récupère la destination du vol j:
    prob += lpSum(x[k, j, t_val]* data["destinations"][dest(j)-1]["flight_time"] for j in liste_vols for t_val in T) >= alpha * T_max

# Contrainte : Espacement minimal entre deux vols
for j in liste_vols:
    for k in range(m):
        for t_val in T:
            prob += x[k, j, t_val] + lpSum(x[k, j2, t2] for j2 in liste_vols for t2 in range(t_val + 1, min(t_val + delta, T_max))) <= 1

#deux vols de la même destination ne sont pas trop proches
for j in liste_vols:
    for j2 in liste_vols:
        if j != j2 and dest(j) == dest(j2):  # Même destination
            for k in range(m):
                for t_val in T:  
                    prob += x[k, j, t_val] + lpSum(x[k, j2, t2] for t2 in range(t_val + 1, min(t_val + delta, T_max))) <= 1


# Contrainte : Temps de vol,  tous les vols terminent avant la fin, t_j + flight_time(j) <= T_max
for j in liste_vols:
    prob += t[j] + data["destinations"][dest(j)-1]["flight_time"] <= T_max



# Résolution

prob.solve()



# Affichage des résultats
print("Status:", LpStatus[prob.status])
print("Profit total:", value(prob.objective))
for j in liste_vols:
    for k in range(m):
        for t in T:
            if x[k, j, t].varValue == 1:
                print(f"Avion {k+1} : Vol {j} à l'instant {t}")
                break



