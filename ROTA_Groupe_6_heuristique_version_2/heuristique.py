import json
import random
import copy

# Charger les données depuis un fichier JSON
def charger_donnees(fichier):
    with open(fichier, 'r') as f:
        return json.load(f)

# Créer la liste des vols avec leur profit, durée, etc.
def creer_vols(donnees):
    vols = []
    for dest_index, destination in enumerate(donnees["destinations"]):
        for t, profit in enumerate(destination["profit"]):
            vols.append({
                "vol": len(vols) + 1,
                "destination": dest_index,
                "time": t,
                "profit": profit,
                "flight_time": destination["flight_time"]
            })
    return vols

# Planification initiale gloutonne
def planifier_vols(vols, donnees):
    solution = []
    slots_disponibles = donnees["slots"][:]
    m = donnees["n_aircraft"]
    Tmax = donnees["time_horizon_len"]
    planning = [[0] * Tmax for _ in range(m)]
    profit_total = 0
    vols_planifiés = set()  # Pour éviter les doublons

    vols_tries = sorted(vols, key=lambda v: v["profit"], reverse=True)

    for vol_info in vols_tries:
        vol_id = vol_info["vol"]
        if vol_id in vols_planifiés:
            continue
        t, duree, profits = vol_info["time"], vol_info["flight_time"], vol_info["profit"]
        if t + duree <= Tmax and slots_disponibles[t] > 0:
            for k in range(m):
            # Vérification de l'espacement avant de planifier
                if all(planning[k][t + dt] == 0 for dt in range(duree)):
                    violation = violation_espacement((k, vol_id, t), donnees, solution, vols)
                    if violation == 0:  # Si aucune violation d'espacement
                    # Vérification de l'espacement avec les autres vols du même avion
                        for autre_vol in solution:
                            if autre_vol[0] == k:  # Vérifie les vols du même avion
                                t_autre, duree_autre = autre_vol[2], donnees["destinations"][obtenir_destination(autre_vol[1], vols)]["flight_time"]
                                if abs(t - t_autre) < donnees["min_spacing"]:  # Violations d'espacement entre vols du même avion
                                # Déplacer le vol actuel ou ajuster l'horaire
                                    t = t_autre + donnees["min_spacing"]
                                    break
                        if violation == 0:  # Si l'espacement est respecté
                        # Affecter le vol
                            if t + duree > Tmax:
                                continue
                            else:
                                for dt in range(duree):
                                    planning[k][t + dt] = 1
                                slots_disponibles[t] -= 1
                                profit_total += profits
                                solution.append((k, vol_id, t))
                                vols_planifiés.add(vol_id)
                                break

    # Vérification de l'utilisation minimale
    for k in range(m):
        temps_utilisé = sum(planning[k])
        while temps_utilisé < donnees["min_utilisation"] * Tmax:  # tant que l'avion n'est pas assez utilisé 
            for vol_info in vols_tries:
                vol_id = vol_info["vol"]
                if vol_id in vols_planifiés:
                    continue
                t, duree, profits = vol_info["time"], vol_info["flight_time"], vol_info["profit"]
                if t + duree <= Tmax and slots_disponibles[t] > 0:
                    if all(planning[k][t + dt] == 0 for dt in range(duree)):
                        violation = violation_espacement((k, vol_id, t), donnees, solution, vols)
                        if violation == 0:  # Si aucune violation d'espacement
                            for dt in range(duree):
                                planning[k][t + dt] = 1
                            slots_disponibles[t] -= 1
                            profit_total += profits
                            solution.append((k, vol_id, t))
                            temps_utilisé += duree
                            break
            else:
                break  # Aucun vol possible, on arrête

    return solution, profit_total, planning



# Utilitaire pour trouver la destination d’un vol
def obtenir_destination(id_vol, vols):
    for vol in vols:
        if vol["vol"] == id_vol:
            return vol["destination"]
    return None

# Vérifie les violations d’espacement entre les vols d’une même destination
# Vérifie les violations d’espacement entre les vols d’une même destination
def violation_espacement(vol, donnees, solution, vols):
    id_vol, t = vol[1], vol[2]
    destination = obtenir_destination(id_vol, vols)  # obtenir la destination du vol
    min_spacing = donnees["min_spacing"]  # espacement minimum
    violations = 0  # compteur des violations

    # Parcours de tous les autres vols dans la solution pour vérifier les violations d'espacement
    for autre_vol in solution:
        if autre_vol[1] == id_vol:  
            continue
        autre_destination = obtenir_destination(autre_vol[1], vols)  # obtenir la destination du vol autre
        if autre_destination == destination:  # Vérifie si c'est le même avion (ou même destination)
            # Calcul de l'écart entre les horaires d'arrivée du vol 1 et de départ du vol 2
            ecart = abs(t + donnees["destinations"][destination]["flight_time"] - autre_vol[2])
            print(f"Comparaison de vols {vol[1]} (t={t}) et {autre_vol[1]} (t={autre_vol[2]}) avec espacement min {min_spacing}")
            print(f"Écart calculé : {ecart}")
            if ecart < min_spacing:  # Si l'écart est inférieur à l'espacement minimum
                violations += min_spacing - ecart  # Ajoute la violation d'espacement
                print(f"Violation détectée ! (pénalité : {min_spacing - ecart})")

    return violations


# Vérifie si un avion est sous-utilisé
def violation_utilisation(avion, donnees, solution, vols):
    temps_utilisation = 0
    min_utilisation = donnees["min_utilisation"]
    Tmax = donnees["time_horizon_len"]

    for vol in solution:
        if vol[0] == avion:
            destination = obtenir_destination(vol[1], vols)
            temps_utilisation += donnees["destinations"][destination]["flight_time"]

    if temps_utilisation < min_utilisation * Tmax:
        return True, round(min_utilisation * Tmax - temps_utilisation, 2)
    return False, 0

# Fonction d’évaluation de la solution (à maximiser)
def fonction_evaluation(solution, donnees, lambda_espacement, lambda_utilisation, vols, profit_total=None):
    if profit_total is None:
        profit_total = sum(vol["profit"] for _, id_vol, _ in solution for vol in vols if vol["vol"] == id_vol)

    penalite_espacement = sum(
        violation_espacement(vol, donnees, solution, vols) for vol in solution 
    )

    penalite_utilisation = 0
    for k in range(donnees["n_aircraft"]):
        violation, penalite = violation_utilisation(k, donnees, solution, vols)
        if violation:
            penalite_utilisation += penalite

    score = profit_total - lambda_espacement * penalite_espacement - lambda_utilisation * penalite_utilisation
    return score, profit_total, penalite_espacement, penalite_utilisation

# Voisinage 1 : suppression et réinsertion d’un vol
def voisinage_1(solution, planning, profit_total, donnees):
    nouvelle_solution = copy.deepcopy(solution)
    nouveau_planning = copy.deepcopy(planning)
    nouveau_profit_total = profit_total
    slots_disponibles = donnees["slots"][:]
    Tmax = donnees["time_horizon_len"]
    vols = creer_vols(donnees)

    if not nouvelle_solution:
        return solution, profit_total, planning

    vol_a_retirer = random.choice(nouvelle_solution)
    nouvelle_solution.remove(vol_a_retirer)
    avion, id_vol, t = vol_a_retirer
    destination = obtenir_destination(id_vol, vols)
    duree = donnees["destinations"][destination]["flight_time"]
    profit = donnees["destinations"][destination]["profit"][t]

    for dt in range(duree):
        nouveau_planning[avion][t + dt] = 0
    slots_disponibles[t] += 1
    nouveau_profit_total -= profit

    # Essayer de réinsérer un vol
    for t_nouveau in range(Tmax - duree + 1):
        if slots_disponibles[t_nouveau] > 0:
            for k in range(len(nouveau_planning)):
                if all(nouveau_planning[k][t_nouveau + dt] == 0 for dt in range(duree)):
                    # Vérification de l'espacement avant d'ajouter le vol
                    violation = violation_espacement((k, id_vol, t_nouveau), donnees, nouvelle_solution, vols)
                    if violation == 0:  # Si pas de violation, on peut ajouter le vol
                        for dt in range(duree):
                            nouveau_planning[k][t_nouveau + dt] = 1
                        slots_disponibles[t_nouveau] -= 1
                        nouveau_profit_total += donnees["destinations"][destination]["profit"][t_nouveau]
                        nouvelle_solution.append((k, id_vol, t_nouveau))
                        return nouvelle_solution, nouveau_profit_total, nouveau_planning

    return nouvelle_solution, nouveau_profit_total, nouveau_planning

# Voisinage 2 : remplacement d’un vol par un autre non encore planifié
def voisinage_2(solution, planning, profit_total, donnees, vols):
    nouvelle_solution = copy.deepcopy(solution)
    nouveau_planning = copy.deepcopy(planning)
    nouveau_profit_total = profit_total

    if not nouvelle_solution:
        return solution, profit_total, planning

    vol_retiré = random.choice(nouvelle_solution)
    nouvelle_solution.remove(vol_retiré)
    avion, id_vol, t_depart = vol_retiré
    destination = obtenir_destination(id_vol, vols)
    duree = donnees["destinations"][destination]["flight_time"]
    profit_retiré = donnees["destinations"][destination]["profit"][t_depart]

    # Libération du créneau horaire
    for t in range(t_depart, t_depart + duree):
        if t < donnees["time_horizon_len"]:
            nouveau_planning[avion][t] = 0

    nouveau_profit_total -= profit_retiré

    # Interdire de replanifier un vol déjà dans la solution
    vols_ids_solution = {v[1] for v in nouvelle_solution}

    # Essayer de trouver un nouveau vol à insérer à la place
    vols_non_planifies = [v for v in vols if v["vol"] not in vols_ids_solution]
    random.shuffle(vols_non_planifies)

    for vol_candidat in vols_non_planifies:
        t_cand = vol_candidat["time"]
        duree_cand = vol_candidat["flight_time"]
        if t_cand + duree_cand > donnees["time_horizon_len"]:
            continue

        for k in range(donnees["n_aircraft"]):
            if all(nouveau_planning[k][t_cand + dt] == 0 for dt in range(duree_cand)):
                violation = violation_espacement((k, vol_candidat["vol"], t_cand), donnees, nouvelle_solution, vols)
                if violation == 0:
                    # Planification du nouveau vol
                    for dt in range(duree_cand):
                        nouveau_planning[k][t_cand + dt] = 1
                    nouveau_profit_total += vol_candidat["profit"]
                    nouvelle_solution.append((k, vol_candidat["vol"], t_cand))
                    return nouvelle_solution, nouveau_profit_total, nouveau_planning

    # Aucun vol de remplacement valide trouvé : on garde la solution partielle
    return nouvelle_solution, nouveau_profit_total, nouveau_planning


def voisinage_3(solution, planning, profit_total, donnees, vols):
    nouvelle_solution = copy.deepcopy(solution)
    nouveau_planning = copy.deepcopy(planning)
    nouveau_profit_total = profit_total
    Tmax = donnees["time_horizon_len"]
    vols_ids_solution = {v[1] for v in nouvelle_solution}
    random.shuffle(vols)

    for vol in vols:
        if vol["vol"] in vols_ids_solution:
            continue
        t, duree = vol["time"], vol["flight_time"]
        if t + duree > Tmax:
            continue
        for k in range(donnees["n_aircraft"]):
            if all(nouveau_planning[k][t + dt] == 0 for dt in range(duree)):
                violation = violation_espacement((k, vol["vol"], t), donnees, nouvelle_solution, vols)
                if violation == 0:
                    for dt in range(duree):
                        nouveau_planning[k][t + dt] = 1
                    nouveau_profit_total += vol["profit"]
                    nouvelle_solution.append((k, vol["vol"], t))
                    return nouvelle_solution, nouveau_profit_total, nouveau_planning
    return nouvelle_solution, nouveau_profit_total, nouveau_planning
