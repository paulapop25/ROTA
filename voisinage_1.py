import json
import random
import copy
import random

def creer_vols(donnees):
    # Création de la liste des vols triés par profit décroissant
    vols = []
    destinations = donnees["destinations"]
    for dest_index, destination in enumerate(destinations):
        for t, profit in enumerate(destination["profit"]):
            
            vols.append({
                "vol": len(vols) + 1,  # Utilisation d'un indice unique incrémental
                "destination": dest_index,
                "time": t,
                "profit": profit,
                "flight_time": destination["flight_time"]
            })
   
    return vols

def planifier_vols(vols):
    # Initialisation
    solution = []
    slots_disponibles = donnees["slots"]
    m = donnees["n_aircraft"]  # Nombre d'avions
    Tmax = donnees["time_horizon_len"]  # Nombre maximum de créneaux
    planning = [[0] * Tmax for _ in range(m)]  # Matrice de disponibilité des avions
    profit_total = 0
    
    
    # Création de la liste des vols triés par profit décroissant
    vols_tries = sorted(vols, key=lambda v: v["profit"], reverse=True)

    # Parcours des vols triés par profit décroissant
    for vol_info in vols_tries:
        vol = vol_info["vol"]
        t = vol_info["time"]
        duree = vol_info["flight_time"]
        profits = vol_info["profit"]

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
                    solution.append((k, vol, t))  # Ajouter le numéro du vol
                    break

    return solution, profit_total, planning


# Lecture des données depuis le fichier JSON

    
    
    
    
#Fonction évaluation 
    
def obtenir_destination(id_vol, vols):
    # Retourne la destination associée à un vol donné
    for vol in vols:
        if vol["vol"] == id_vol:
            return vol["destination"]
    return None  # Retourne None si le vol n'est pas trouvé


def violation_espacement(vol, donnees, solution, vols):
    id_vol = vol[1]  # ID du vol actuel
    t = vol[2]       # Instant du vol actuel
    destination = obtenir_destination(id_vol, vols)
    min_spacing = donnees["min_spacing"]

    for autre_vol in solution:
        autre_id_vol = autre_vol[1]
        autre_t = autre_vol[2]
        destination_autre = obtenir_destination(autre_id_vol, vols)
        
        if destination_autre == destination:
            if abs(autre_t - t) < min_spacing and id_vol != autre_id_vol:
                violation = min_spacing - abs(autre_t - t)
            
                return violation  # Retourne la valeur de la violation
    return 0  # Pas de violation



def violation_utilisation(avion, donnees, solution, vols):
    # Calculer le temps total d'utilisation de l'avion
    temps_utilisation = 0
    min_utilisation = donnees["min_utilisation"]
    time_horizon_len = donnees["time_horizon_len"]
    destinations = donnees["destinations"]

    for vol in solution:
        autre_avion, id_vol, _ = vol
        destination = obtenir_destination(id_vol, vols)
        if autre_avion == avion:
        
            # Ajouter le temps de vol de la destination
            temps_utilisation += destinations[destination]["flight_time"]
          
    
    # Vérifier si le temps d'utilisation est inférieur au minimum requis
    if temps_utilisation < min_utilisation * time_horizon_len:
        penalite = round(min_utilisation * time_horizon_len - temps_utilisation,2)
        return True, penalite  # Violation détectée
    return False, 0  # Pas de violation


def fonction_evaluation(solution, donnees, lambda_espacement, lambda_utilisation, vols, profit_total):
    penalite_espacement = 0
    penalite_utilisation = 0
  
    for k in range(donnees["n_aircraft"]):
        for vol in solution:
            # Calculer la pénalité d'espacement réelle
            violation = violation_espacement(vol, donnees, solution, vols)
            if violation > 0:
                penalite_espacement += violation

        # Vérification utilisation reste inchangée
        violation, penalite = violation_utilisation(k, donnees, solution, vols)
        if violation:
            penalite_utilisation += penalite

    fonction_eval = profit_total - lambda_espacement * penalite_espacement - lambda_utilisation * penalite_utilisation
    return fonction_eval, profit_total, penalite_espacement, penalite_utilisation


def voisinage_1(solution, planning, profit_total, donnees):
    # Initialisation
    nouvelle_solution = copy.deepcopy(solution)
    nouveau_planning = copy.deepcopy(planning)
    nouveau_profit_total = profit_total
    slots_disponibles = donnees["slots"]
    Tmax = donnees["time_horizon_len"]
    destinations = donnees["destinations"]

    # Sélection aléatoire d'un ou deux vols à retirer
    vols_a_retirer = random.sample(nouvelle_solution, k=min(len(nouvelle_solution), 1))
    print("vol retiré", vols_a_retirer)

    # Retirer les vols sélectionnés
    for vol in vols_a_retirer:
        avion, id_vol, t = vol
        destination = obtenir_destination(id_vol, vols)
        duree = destinations[destination]["flight_time"]
        profit = destinations[destination]["profit"][t]

        # Libérer les créneaux associés dans le planning
        for dt in range(duree):
            nouveau_planning[avion][t + dt] = 0
        slots_disponibles[t] += 1

        # Mettre à jour le profit total
        nouveau_profit_total -= profit

        # Retirer le vol de la solution
        nouvelle_solution.remove(vol)

    # Réaffecter les vols retirés
    for vol in vols_a_retirer:
        print("vol réaffecté", vol)
        avion, id_vol, t = vol
        destination = obtenir_destination(id_vol, vols)
        duree = destinations[destination]["flight_time"]
        profits = destinations[destination]["profit"]
        
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
                        nouvelle_solution.append((k, id_vol, t))  # Utiliser le bon ID de vol
                        break
                break

    return nouvelle_solution, nouveau_profit_total, nouveau_planning


def voisinage_2(solution, planning, profit_total, donnees, vols):
    # Copie des données pour ne pas modifier l'original
    nouvelle_solution = copy.deepcopy(solution)
    nouveau_planning = copy.deepcopy(planning)
    nouveau_profit_total = profit_total

    if not nouvelle_solution:
        return nouvelle_solution, nouveau_profit_total, nouveau_planning

    # Choisir un vol à retirer aléatoirement
    vol_retiré = random.choice(nouvelle_solution)
    nouvelle_solution.remove(vol_retiré)
    avion, vol_id, t_depart = vol_retiré
    t_fin = t_depart + vols[vol_id]["flight_time"]

    print("vol retiré", [vol_retiré])
    print(f"Créneaux libérés pour le vol {vol_id} : {t_depart} à {t_fin}")

    # Libérer le planning
    for t in range(t_depart, t_fin):
        nouveau_planning[avion][t] = 0

    # Mettre à jour le profit
    nouveau_profit_total -= vols[vol_id]["profit"]

    # Essayer de trouver un vol non affecté pouvant être placé dans ce créneau
    vols_ids_solution = {v[1] for v in nouvelle_solution}
    vol_ajoute = None
    for vol_candidat in vols:
        id_candidat = vol_candidat["vol"]
        if id_candidat in vols_ids_solution:
            continue  # Déjà affecté

        t_d = vol_candidat["time"]
        t_f = t_d + vol_candidat["flight_time"]
        avion_candidat = vol_candidat["destination"]

        if t_f <= len(nouveau_planning[avion_candidat]) and all(nouveau_planning[avion_candidat][t] == 0 for t in range(t_d, t_f)):
            # Affectation possible
            for t in range(t_d, t_f):
                nouveau_planning[avion_candidat][t] = 1

            nouvelle_solution.append((avion_candidat, id_candidat, t_d))
            nouveau_profit_total += vol_candidat["profit"]
            vol_ajoute = vol_candidat
            print("vol ajouté :", vol_candidat)
            break

    if not vol_ajoute:
        print("Aucun vol admissible trouvé pour remplacer le vol retiré.")

    return nouvelle_solution, nouveau_profit_total, nouveau_planning







###APPEL DES FONCTIONS 
with open("toy_instance.json", "r") as f:
    donnees = json.load(f)
    min_spacing = donnees["min_spacing"]
    min_utilisation = donnees["min_utilisation"]    



# Appeler la fonction de recuit simulé
if __name__ == "__main__":
    # Appeler les fonctions principales ici
    vols = creer_vols(donnees)

    solution, profit_total, planning = planifier_vols(vols)

    # Affichage des résultats
    print("Solution:", solution)
    print("Profit total:", profit_total)
    print("Planning:")
    for row in planning:
        print(row)

    fonc = fonction_evaluation(solution, donnees, min_spacing, min_utilisation, vols, profit_total)
    print("Évaluation solution initiale:", fonc)

    # Exemple d'appel des voisinages
    nouvelle_solution, nouveau_profit_total, nouveau_planning = voisinage_1(solution, planning, profit_total, donnees)
    print("\nNouvelle Solution après voisinage_1:", nouvelle_solution)
    print("Nouveau Profit Total après voisinage_1:", nouveau_profit_total)

    nouvelle_solution_2, nouveau_profit_total_2, nouveau_planning_2 = voisinage_2(solution, planning, profit_total, donnees, vols)
    print("\nNouvelle Solution après voisinage_2:", nouvelle_solution_2)
    print("Nouveau Profit Total après voisinage_2:", nouveau_profit_total_2)