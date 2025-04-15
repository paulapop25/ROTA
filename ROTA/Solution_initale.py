import json

def planifier_vols(donnees):
    # Initialisation
    solution = []
    slots_disponibles = donnees["slots"]
    destinations = donnees["destinations"]
    m = donnees["n_aircraft"]  # Nombre d'avions
    Tmax = donnees["time_horizon_len"]  # Nombre maximum de créneaux
    planning = [[0] * Tmax for _ in range(m)]  # Matrice de disponibilité des avions
    profit_total = 0

    # Création de la liste des vols triés par profit décroissant
    vols_tries = []
    for dest_index, destination in enumerate(destinations):
        for t, profit in enumerate(destination["profit"]):
            vols_tries.append({
                "destination": dest_index + 1,
                "time": t,
                "profit": profit,
                "flight_time": destination["flight_time"]
            })
    vols_tries = sorted(vols_tries, key=lambda v: v["profit"], reverse=True)
    print(vols_tries)

    # Parcours des vols triés par profit décroissant
    for vol in vols_tries:
        destination = vol["destination"]
        t = vol["time"]
        duree = vol["flight_time"]
        profits = vol["profit"]

        # Recherche d'un créneau disponible
        if t + duree <= Tmax and slots_disponibles[t] > 0:
            for k in range(m):
                # Vérification des créneaux libres pour l'avion k
                if all(planning[k][t + dt] == 0 for dt in range(duree)):
                    # Affectation du vol à l'avion k à l'instant t
                    for dt in range(duree):
                        planning[k][t + dt] = 1  # Marquer les créneaux comme occupés
                    slots_disponibles[t] -= 1
                    profit_total += profits
                    solution.append((k, destination, t))
                    break

    return solution, profit_total, planning


# Lecture des données depuis le fichier JSON
with open("toy_instance.json", "r") as f:
    donnees = json.load(f)

# Appel de la fonction avec les données du fichier
solution, profit_total, planning = planifier_vols(donnees)

# Affichage des résultats
print("Solution:", solution)
print("Profit total:", profit_total)
print("Planning:")
for row in planning:
    print(row)