'''
This module provides a class to represent potential solutions to the optimization problem.
Such objects contain:
- a representation of the candidate solution, that can be of any kind;
- the cost of the candidate solution, that must be of any numerical type.

A basic use of this class, if you already defined an optimization function `f` that works
on objects `x` of the kind you like, is to simply wrap `x` and `f(x)`:
```python
solution = Candidate(x, f(x))
```
'''

from typing import Any


class Candidate:
    '''
    Represents a candidate solution to the optimization problem.
    '''

    def __init__(self, x : Any, cost : int | float) -> None:
        '''
        Create a candidate with given vector `x` and its `cost`.
        '''
        self.x : Any = x
        '''The representation of the candidate solution.'''
        self.cost : int | float = cost
        '''The cost, w.r.t. the optimization criterion, of the candidate solution.'''

    def __repr__(self) -> str:
        return f'{self.x} - cost = {self.cost}'
