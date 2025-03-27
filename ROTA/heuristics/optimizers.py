'''
This module provides random walk based heuristics. Currently, a strict descent
and a simulated annealing are available, through the corresponding functions.
To use either of them, you have to provide the following elements:
- an initial solution (of type `.candidate.Candidate`)
- a neighbour function which, given a solution and the state of the search
 (of type `.state.State`), builds a new solution that is "close" to the original
- (optionally) a stop criterion (of type `.stop.Stop`) to indicate when to terminate
the search.

If you choose the simulated annealing, you will also need to provide a
temperature profile, *i.e.* a function that returns a temperature (`float`)
at a given iteration (`int`).
'''

import numpy as np
from typing import Callable
from .state import State
from .candidate import Candidate
from .stop import *


class MonteCarlo:
    '''@private'''

    def __init__(self, minimize=True) -> None:
        self.state = None
        self.minimize = minimize

    def accept(self, candidate : Candidate) -> bool: return True

    def step(self, candidate):
        '''@private'''
        self.state.update(candidate, self.accept(candidate))


class Descent(MonteCarlo):
    '''@private'''

    def accept(self, candidate): return self.state.is_better(candidate)


class SimulatedAnnealing(MonteCarlo):
    '''@private'''

    def __init__(self, temp, minimize):
        super().__init__(minimize)
        self.temp = temp

    def accept(self, candidate):
        if self.state.current is None: return True
        delta = candidate.cost - self.state.current.cost
        if not self.minimize: delta = -delta
        return (delta < 0 or
                np.exp(-delta / self.temp(self.state.iterations)) > np.random.rand())


class CleanExit:
    '''@private'''
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is KeyboardInterrupt:
            return True
        return exc_type is None


def optimize(initial_candidate : Candidate,
             neighbour : Callable[[Candidate, State], Candidate],
             heuristic : MonteCarlo,
             stop : Stop | None = None) -> State:
    '''@private'''
    if stop is None: stop = lambda _: False
    with State(heuristic.minimize) as st:
        with CleanExit():
            heuristic.state = st
            heuristic.step(initial_candidate)
            while not stop(st):
                heuristic.step(neighbour(st.current, st))
        return st

def descent(initial : Candidate,
            neighbour : Callable[[Candidate, State], Candidate],
            stop : Stop | None = None,
            minimize : bool = True) -> State:
    '''
    Launch a strict descent, starting at `initial` candidate solution,
    using the `neighbour` function to step from one candidate to the next,
    and stopping as indicated by the `stop` criterion
    (if not provided, you will have to interrupt manually with Ctrl+C).
    If you maximize your function, you need to set `minimize = False`.
    '''
    return optimize(initial, neighbour, Descent(minimize), stop)

def simulatedannealing(initial : Candidate,
                       neighbour : Callable[[Candidate, State], Candidate],
                       temperature : Callable[[int], float],
                       stop : Stop | None = None,
                       minimize : bool = True) -> State:
    '''
    Same as `descent`, except it uses a simulated annealing process.
    You have to provide an additional `temperature` function that describes the
    temperature decreasing profile as a function of the number of iterations.
    '''
    return optimize(initial, neighbour, SimulatedAnnealing(temperature, minimize), stop)


def temperature_calibration(s0, neigh, target_accept, n):
    s = s0
    l = []
    for _ in range(n):
        new = neigh(s, None)
        l.append(abs(new.cost - s.cost))
        s = new
    return -np.mean(np.array(l)) / np.log(target_accept)
