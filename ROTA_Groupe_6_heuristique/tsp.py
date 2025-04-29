import sys
import numpy as np
import matplotlib.pyplot as plt
from heuristics.optimizers import *


class Point:

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __sub__(self, other):
        return Point(other.x - self.x, other.y - self.y)

    def __abs__(self):
        return np.sqrt(self.x * self.x + self.y * self.y)

    def distance(self, other):
        return abs(other - self)


class Model1:

    def __init__(self, places):
        self.places = places
        self.size = len(places)

    def cost(self, x):
        return sum(self.places[x[i - 1]].distance(self.places[x[i]]) for i in range(self.size))

    def initial(self):
        x = np.arange(self.size)
        np.random.shuffle(x)
        return Candidate(x, self.cost(x))

    def neighbour(self, s, state):
        i, j = np.random.choice(len(s.x), size=2, replace=False)
        x = s.x.copy()
        x[i], x[j] = x[j], x[i]
        return Candidate(x, self.cost(x))

    def plot(self, solution):
        s = [place for place in solution.x]
        s.append(s[0])
        return plt.plot([self.places[si].x for si in s],
                        [self.places[si].y for si in s],
                        marker='o', color='teal')


class Model2(Model1):

    def __init__(self, places):
        super().__init__(places)
        self.distances = np.array([[pi.distance(pj) for pj in places] for pi in places])

    def cost(self, x):
        return sum(self.distances[x[i - 1], x[i]] for i in range(self.size))


class Model3(Model2):

    def cost(self, x):
        return sum(self.distances[x, np.concatenate((x[1:], x[:1]))])


class Model4(Model3):

    def neighbour(self, s, state):
        i, j = np.random.choice(len(s.x), size=2, replace=False)
        x = s.x.copy()
        i1 = (i + 1) % self.size
        j1 = (j + 1) % self.size
        cost = s.cost
        cost -= (self.distances[x[i-1], x[i]] + self.distances[x[i], x[i1]])
        cost -= (self.distances[x[j-1], x[j]] + self.distances[x[j], x[j1]])
        cost += self.distances[x[i-1], x[j]] + self.distances[x[j], x[i1]]
        cost += self.distances[x[j-1], x[i]] + self.distances[x[i], x[j1]]
        if i == j1 or j == i1:
            cost += self.distances[x[i], x[j]] + self.distances[x[j], x[i]]
        x[i], x[j] = x[j], x[i]
        return Candidate(x, cost)


class Model5(Model3):
    '''This model implements the classic 2-opt move.'''

    best = None
    graph = None

    def plot_dyn(self, state):
        if state is None: return
        if self.graph is None:
            self.graph = self.plot(state.best)[0]
            plt.pause(1e-12)
        elif self.best is None or state.best.cost < self.best:
            self.best = state.best.cost
            self.graph.remove()
            self.graph = self.plot(state.best)[0]
            plt.pause(1e-12)

    def neighbour(self, s, state):
        self.plot_dyn(state)
        i = np.random.randint(0, self.size - 1)
        j = np.random.randint(i + 1, self.size)
        j1 = (j + 1) % self.size
        x = s.x.copy()
        cost = s.cost
        if i != 0 or j != self.size - 1:
            cost -= self.distances[x[i-1], x[i]] + self.distances[x[j], x[j1]]
            cost += self.distances[x[i-1], x[j]] + self.distances[x[i], x[j1]]
        if i == 0: x[i:j+1] = x[j::-1]
        else: x[i:j+1] = x[j:i-1:-1]
        return Candidate(x, cost)


def read(filename):
    with open(filename) as f:
        places = []
        for line in f:
            x, y = line.strip().split()
            places.append(Point(x, y))
        return places


def temp(T0, k, t): return T0 * np.exp(-t/k)


def solve(instance, Model):
    model = Model(instance)
    s0 = model.initial()
    T0 = temperature_calibration(s0, model.neighbour, 0.5, 10000)
    k = 9000000
    stop = MaxTime(60)
    stop = None
    return simulatedannealing(s0, model.neighbour, lambda t: temp(3*T0, k, t), stop)


# def solve(instance, Model):
#     model = Model(instance)
#     return descent(model.initial(), model.neighbour, stop=MaxTime(60))


if __name__ == '__main__':
    filename = sys.argv[1]
    places = read(filename)
    try: size = int(sys.argv[2])
    except: size = len(places)
    instance = places[:size]

    plt.ion()
    solution = solve(instance, Model5)

    plt.show()
    plt.close()
    plt.ioff()
    solution.plot_convergence()
    solution.plot_best()
    plt.show()

    # models = [Model1, Model2, Model3, Model4, Model5]
    # solutions = [solve(instance, Model) for Model in models]
    # for i, (statei, modeli) in enumerate(zip(solutions, models)):
    #     i += 10
    #     plt.gcf().set_size_inches(10, 4)
    #     statei.plot_convergence()
    #     statei.plot_best()
    #     plt.savefig(f'figs/convergence{i+1}.png', bbox_inches='tight')
    #     plt.close()
    #     plt.gcf().set_size_inches(10, 10)
    #     modeli(instance).plot(statei.best)
    #     plt.savefig(f'figs/tsp{i+1}.png', bbox_inches='tight')
    #     plt.close()
