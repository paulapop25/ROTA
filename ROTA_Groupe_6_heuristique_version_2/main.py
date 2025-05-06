import json
import os
import numpy as np
import math
import matplotlib.pyplot as plt
import sys

from heuristics.candidate import Candidate
from heuristics.stop import MaxTime, NoImprovement
from heuristics.optimizers import temperature_calibration, simulatedannealing
from heuristics.state import State

from heuristique import planifier_vols, fonction_evaluation, voisinage_1, voisinage_2

def charger_donnees(fichier):
    with open(fichier, 'r') as f:
        return json.load(f)

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

class FlightPlanningModel:
    def __init__(self, donnees, vols, lambda_esp, lambda_util):
        self.donnees = donnees
        self.vols = vols
        self.lambda_esp = lambda_esp
        self.lambda_util = lambda_util

    def cost(self, solution):
        score, _, _, _ = fonction_evaluation(solution, self.donnees, self.lambda_esp, self.lambda_util, self.vols)
        return score  # on maximise

    def initial(self):
        solution, profit, planning = planifier_vols(self.vols, self.donnees)
        return Candidate((solution, planning, profit), self.cost(solution))

    def neighbour(self, candidate, state):
        solution, planning, profit = candidate.x
        new_solution, new_profit, new_planning = voisinage_2(solution, planning, profit, self.donnees, self.vols)
        return Candidate((new_solution, new_planning, new_profit), self.cost(new_solution))

def solve_flight_planning(donnees, vols, lambda_esp, lambda_util, time_limit=60, plot=False):
    model = FlightPlanningModel(donnees, vols, lambda_esp, lambda_util)
    s0 = model.initial()
    T0 = temperature_calibration(s0, model.neighbour, 0.3, 1500)
    temp = lambda t: T0 * np.exp(-t / 5000)
    stop = NoImprovement(10000)
    


    result = simulatedannealing(s0, model.neighbour, temp, stop, minimize=False)
    return result

def convergence(result):
    result.plot_convergence()
    plt.title("Convergence")

def sauvegarder_solution(solution, instance_path):
    base_name = os.path.basename(instance_path).replace(".json", ".txt")
    out_path = os.path.join("Solution", base_name)
    if not os.path.exists("Solution"):
        os.makedirs("Solution")
    with open(out_path, "w") as f:
        for avion, id_vol, t in solution:
            f.write(f"{avion} {id_vol} {t}\n")
    print(f"Solution sauvegardée : {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <instance_file> <time_limit> [--plot]")
        sys.exit(1)

    fichier = sys.argv[1]
    time_limit = int(sys.argv[2])
    plot = "--plot" in sys.argv

    donnees = charger_donnees(fichier)
    vols = creer_vols(donnees)

    # Paramètres des contraintes
    lambda_esp, lambda_util = 20, 20 
    print("λ espacement :", lambda_esp)
    print("λ sous-utilisation :", lambda_util)

    result = solve_flight_planning(donnees, vols, lambda_esp, lambda_util, time_limit, plot)
    solution, _, _ = result.best.x

    score, profit, pen_esp, pen_util = fonction_evaluation(solution, donnees, lambda_esp, lambda_util, vols)
    print(f"\nProfit : {profit}")
    print(f"Score final (avec pénalités) : {score}")
    print(f"Pénalité espacement : {pen_esp}, Pénalité sous-utilisation : {pen_util}\n")

    print("Meilleure solution trouvée :")
    for avion, id_vol, t in solution:
        flight = vols[id_vol - 1]
        print(f"Avion {avion} | Vol {id_vol} | Départ : {t} | Arrivée : {t + flight['flight_time']} | Destination {flight['destination']}")

    sauvegarder_solution(solution, fichier)
    convergence(result)
    plt.show()
