'''
Random walk algorithms need to maintain some technical information up-to-date
for a correct behaviour. This module provides a `State` class containing such
information. This state is returned at the end of the optimization process,
so you can access all the history of the random walk, and plot interesting
information.
'''

import matplotlib.pyplot as plt
from datetime import datetime
from typing import Optional
from .candidate import Candidate


class State:
    '''
    Represents the search state of random walks.
    '''

    def __init__(self, minimize: bool) -> None:
        '''@private'''
        self.start: datetime = datetime.now()
        '''Start time of the optimization process.'''
        self.minimize: bool = minimize
        '''@private `True` if trying to minimize,
        `False` if trying to maximize'''
        self.current: Optional[Candidate] = None
        '''Current position (candidate solution) in the random walk.'''
        self.best: Optional[Candidate] = None
        '''Best candidate solution since beginning of the random walk.'''
        self.iterations: int = -1
        '''Number of iterations performed.'''
        self.last_improved: int = -1
        '''Iteration at which the last improvement occured.'''
        # self._candidates = []
        self._accepted: list[tuple[int, int | float]] = []
        self._convergence: list[tuple[int, int | float]] = []

    def __enter__(self):
        '''@private'''
        print('Search started')
        return self

    def __exit__(self, *exn):
        '''@private'''
        print('Elapsed time:', self.elapsed)
        print('Iterations performed:', f'{self.iterations:,}')
        print('Best solution:', self.best.cost, '\n')

    @property
    def iterations_without_improvement(self) -> int:
        '''Number of iterations since the last improvement.'''
        return self.iterations - self.last_improved

    @property
    def elapsed(self):
        '''@private'''
        return datetime.now() - self.start

    def is_better(self, candidate: Candidate) -> bool:
        '''@private'''
        if self.best is None:
            return True
        elif self.minimize:
            return candidate.cost < self.best.cost
        else:
            return candidate.cost > self.best.cost

    def update(self, candidate: Candidate, accepted: bool) -> None:
        '''@private'''
        self.iterations += 1
        # self._candidates.append(candidate)
        if accepted:
            self._accepted.append((self.iterations, candidate.cost))
            self.current = candidate
        if self.is_better(candidate):
            self._convergence.append((self.iterations, candidate.cost))
            self.best = candidate
            self.last_improved = self.iterations

    def plot_best(self, **kwargs) -> None:
        '''
        Adds a plot to the current `matplolib.pyplot` graph showing the cost of
        the best candidate solution so far.
        '''
        xs, ys = zip(*self._convergence)
        plt.step(xs, ys, **kwargs)

    def plot_convergence(self, **kwargs) -> None:
        '''
        Adds a plot to the current `matplolib.pyplot` graph showing the cost of
        accepted candidate solutions.
        '''
        xs, ys = zip(*self._accepted)
        plt.step(xs, ys, **kwargs)
