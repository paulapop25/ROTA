'''
This module provides helpers to create stop criterion for iterative algorithms,
as well as a few standard ones.

### Using standard criteria
As an example, if you want your heuristic to stop after 10000 iterations, you would use the following:
```python
stopper = MaxIteration(10000)
```

Sometimes, you need to combine several criteria. Say you want to stop after 1 minute, or 100 iterations without improvement, whichever occurs first. In that case you would use the following:
```python
stopper = MaxTime(60) | NoImprovement(100)
```
You can also combine with the `&` operator if you want both criteria to be met before terminating.

The complete documentation of the module follows

---

The `Stop` class is a parent class of all the others. You don't use it directly
 (however, it is needed to implement the general mechanics...).

The currently available constructors are:
- `MaxTime`
- `MaxIteration`
- `NoImprovement`
- `Custom`

.. note::
   If you find interesting, generic criteria, feel free to suggest them
   for inclusion in future versions!

'''

from datetime import datetime
from typing import Callable
from .state import State


class Stop:

    def __call__(self, state): raise NotImplementedError
    def __or__(self, other):
        def stop(state): return self(state) or other(state)
        return Custom(stop)
    def __and__(self, other):
        def stop(state): return self(state) and other(state)
        return Custom(stop)


class MaxIteration(Stop):

    def __init__(self, n):
        '''Stopper that triggers after `n` iterations.'''
        self.n = n
        '''@private'''

    def __call__(self, state): return state.iterations >= self.n


class MaxTime(Stop):

    def __init__(self, seconds : int):
        '''Stopper that triggers after the provided amount of `seconds`'''
        self.maxtime = seconds
        '''@private'''

    def __call__(self, state):
        return state.elapsed.total_seconds() > self.maxtime


class NoImprovement(Stop):

    def __init__(self, n : int):
        '''Stopper that triggers if `n` iterations occur without improvement.'''
        self.n = n
        '''@private'''

    def __call__(self, state): return state.iterations_without_improvement >= self.n


class Custom(Stop):

    def __init__(self, stop : Callable[[State], bool]) -> None:
        '''
        Creates a `Stop` object that behaves as the `stop` function provided as argument.
        The `stop` function must take as input a search state (of type `.state.State`)
        and return a boolean (type `bool`).
        '''
        super().__init__()
        self.stopper = stop
    def __call__(self, state): return self.stopper(state)
