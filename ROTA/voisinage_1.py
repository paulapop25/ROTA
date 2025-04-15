import json
import random
import copy
from Solution_initiale import planifier_vols  # Importer la fonction planifier_vols

# Lecture des données depuis le fichier JSON
with open("toy_instance.json", "r") as f:
    donnees = json.load(f)

# Générer la solution initiale
solution, profit_total, planning = planifier_vols(donnees)

# Définition de la fonction voisinage
def voisinage(solution, planning, profit_total, data):
    # Initialisation
    nouvelle_solution = copy.deepcopy(solution)
    nouveau_planning = copy.deepcopy(planning)
    nouveau_profit_total = profit_total
    slots_disponibles = data["slots"]
    Tmax = data["time_horizon_len"]
    destinations = data["destinations"]

    # Sélection aléatoire d'un ou deux vols à retirer
    vols_a_retirer = random.sample(nouvelle_solution, k=min(len(nouvelle_solution), 2))

    # Retirer les vols sélectionnés
    for vol in vols_a_retirer:
        avion, destination, t = vol
        duree = destinations[destination - 1]["flight_time"]
        profits = destinations[destination - 1]["profit"][t]

        # Libérer les créneaux associés dans le planning
        for dt in range(duree):
            nouveau_planning[avion][t + dt] = 0
        slots_disponibles[t] += 1

        # Mettre à jour le profit total
        nouveau_profit_total -= profits

        # Retirer le vol de la solution
        nouvelle_solution.remove(vol)

    # Réaffecter les vols retirés
    for vol in vols_a_retirer:
        _, destination, _ = vol
        duree = destinations[destination - 1]["flight_time"]
        profits = destinations[destination - 1]["profit"]

        # Recherche d'un créneau disponible
        for t in range(Tmax - duree + 1):
            if slots_disponibles[t] > 0:
                for k in range(len(nouveau_planning)):
                    # Vérification des créneaux libres pour l'avion k
                    if all(nouveau_planning[k][t + dt] == 0 for dt in range(duree)):
                        # Réaffecter le vol à l'avion k à l'instant t
                        for dt in range(duree):
                            nouveau_planning[k][t + dt] = 1
                        slots_disponibles[t] -= 1
                        nouveau_profit_total += profits[t]
                        nouvelle_solution.append((k, destination, t))
                        break
                break

    return nouvelle_solution, nouveau_profit_total, nouveau_planning    

# Utilisation de la fonction voisinage sur la solution initiale
nouvelle_solution, nouveau_profit_total, nouveau_planning = voisinage(solution, planning, profit_total, donnees)

# Affichage des résultats après application du voisinage
print("\nNouvelle Solution après voisinage:", nouvelle_solution)
print("Nouveau Profit Total après voisinage:", nouveau_profit_total)
print("Nouveau Planning après voisinage:")
for row in nouveau_planning:
    print(row)
    
    