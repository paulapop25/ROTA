This small library provides utilities to set up local search based (meta)heuristics. Currently, only a strict descent and a simulated annealing are available. The main entry points are functions `descent` and `simulatedannealing` which solve a problem, given an initial solution and a procedure to build a neighbour (including its cost).

You will probably want to:
```python
from heuristics import *
```
at the beginning of your file, however you can be more picky if you want to be sure the names don't collide with other names in your program. You can navigate the full documentation with the table of contents on the left. To get you started, we present here a full-fledged example of how to use this library, that also serves as a remainder of how to proceed and how to enhance your models. Let's get started!

# Three (or more?) flavours of the TSP

The travelling salesman problem (TSP) consists, given a set of *n* places to visit, in finding the shortest path that goes through all cities once and returns to the departure point. We feature the TSP as an example of how to use the heuristics library, as well as to show some classic tricks to enhance the performance of optimisation models. The complete source code around this description can be found on e-campus as `tsp.py`.

## Instances of the TSP

First and foremost, we need a simple description of the (no less simple) instances of the
problem, so as to be aware of what exactly we are dealing with. An instance consists in a
list of places, each of which is an object of a `Point` class that describes 2D points by
their position and a `distance` method. Here's what you need to know about this class:

```python
class Point:

    ...

    def distance(self, other): # returns the distance between 2 points
        ...
```

Well, that was easy![^1] Now let's get to the fun part of modelling and solving.

[^1]: Instances are described in text files (you can find one instance on e-campus) and imported as `Point` lists by a `read` function that we had to write, however this is out of interest here.

## Start simple and easy

This should be you motto for all your modelling work out there! Start with the simplest model you can think of, implement it, then build upon it.

Before jumping into the model, let's remember what we need in order to set up a local search:
1. a cost function, a.k.a. optimisation criterion
2. an initial (good?) solution
3. a neighbourhood, that is, a way to build "close" solution(s)

We will pack those 3 elements in a Python class because... hum... that's what we do in Python, don't we? Let's create a class for this first model, that we initialise by providing it with the instance (a list of `Point`s, remember?). We adventurously call this class `Model1`:

```python
class Model1:

    def __init__(self, places):
        self.places = places
        self.size = len(places)
```

It is quite practical that the model holds the instance (the `places` attribute) as well as the instance's `size`.

Now let's focus on our first requirement and write a cost function. First we need to address a simple question: how do we represent a solution? For the TSP, a solution can be any permutation of the places we have to visit, so the simplest way is to model this by an array (we will use `numpy` arrays, specifically) where the element at index *i* points to the *i*<sup>th</sup> place to be visited.

Given this representation, the cost of a solution (i.e. the length of the travel) is simply the sum of the distances of consecutive points in the sequence (and don't forget: we need to get back where we started!):
$$\sum_{i = 1}^{size-1} distance(p_i, p_{i+1}) \; + \; distance(p_{size}, p_1)$$
which translates to the following Python method:
```python
    def cost(self, x):
        return sum(self.places[x[i - 1]].distance(self.places[x[i]])
                   for i in range(self.size))
```
This might not be the most efficient way to do it (why?), but we will fix it later in the (not so) glorious `Model2`.

Now let's turn our heads to finding an initial solution. We said earlier that a solution to the TSP was basically just a permutation of the places. That's exactly what we're going to do in this model: construct a (random) permutation. Thanks to `numpy` (here imported as `np`), this is trivial:
```python
    def initial(self):
        x = np.arange(self.size)
        np.random.shuffle(x)
        cost_x = self.cost(x)
        return Candidate(x, cost_x)
```
"Wait, what's `Candidate`!?" I hear you say. The way we handle candidate solutions in the `heuristics` library is to have them wrapped with their cost in a `Candidate`[^2] object that has two attributes:
- `x`, the solution itself, which can be of any type you'd like
- `cost`, which speaks for itself, and must be of any numeric type (int, float, etc.)

This will come in handy later on. For now, you just need to remember to encapsulate your solution and its cost in such an object.

[^2]: We could have called this class `Solution`, but you probably have a class with that name somewhere in your project already, which might bring confusion.

So we have an initial solution. Which is not that great (take a few minutes to think of a simple way to build a better starting solution). But we have it and thus we met our second requirement. Let's look at the third and last one!

We will use a random walk algorithm to solve the TSP, either a strict descent or a simulated annealing. For that, we need a way to jump from one solution to the next, staying relatively "close" in the search space. As a first approach (remember: "start simple and easy"!), we build a neighbour solution by just swapping two places in the travel sequence. In Python, we randomly pick `i` and `j`, swap them in our array, and recompute the cost:
```python
    def neighbour(self, s, state):
        i, j = np.random.choice(len(s.x), size=2, replace=False)
        x = s.x.copy()
        x[i], x[j] = x[j], x[i]
        return Candidate(x, self.cost(x))
```
Here, parameter `s` is the solution for which we want to produce a neighbour. Parameter `state` is unused here but could be of interest in your model: it holds the state of the search algorithm (elapsed time and iterations, best solution so far, etc.).

And there we have it! With this third requirement fulfilled, we have our `Model1` complete! Now let's put it to use.

## Getting some results!

We instantiate our model within a `solve` function, then solve it with a strict descent algorithm, imposing a time limit of 1 minute (or 60 seconds):
```python
from heuristics import descent, MaxTime

def solve(instance):
    model = Model1(instance)
    start = model.initial()
    stop = MaxTime(60)
    return descent(start, model.neighbour, stop)
```
The `descent` function needs an initial solution, a neighbourhood function and a stop criterion. The return object of type `.state.State` is the state of the search at the end of the execution. Among other things, it contains the best candidate solution encountered during the search, and provides a few methods to plot the convergence of your model.

We launch our program, wait for 1 minute, and collect the results:
```shell
> python tsp.py tsp.data
Elapsed time: 0:01:00.000071
Iterations performed: 346,979
Best solution: 138113.42128395537
```
A bit less than 350,000 iterations were performed, leading to a tour of 138km. Which is not so bad in comparison with a poorly set up simulated annealing, as you will see next.

If we take a look at how the algorithm converged, we see that after the first 50,000 iterations, it is stuck in a local minimum and cannot find any better solution:
![Convergance of Model1!](fig/convergence0.png)
The solution that is produced has quite a lot of loops and crossings in it that should be removed to enhance the travelling cost:
![Solution of Model1!](fig/tsp0.png)

The TSP is highly combinatorial, so we are not likely to find the global optimum with strict descent only.

## Warming things up. Literally!

Let's try a simulated annealing instead. Well, not so fast! For that we need a temperature profile! We propose an exponential decay for this problem, defined as:
```python
def temp(T0, k, t):
    return T0 * np.exp(-t/k)
```
where `T0` is the initial temperature, `t` is the number of the current iteration and `k` is the iteration at which we want the temperature to be about a third of `T0`.
Without diving into details here, we choose `T0` = 2000 and `k` = 1 million. You sure will have lots to experiment and discuss in order to find a suitable temperature profile for your own optimisation problem. But hey! that's the price to pay for being able to escape local minima!

We can now set up our simulated annealing:
```python
from heuristics import simulatedannealing

def solve(instance):
    model = Model1(instance)
    s0 = model.initial()
    T0 = 2000 # look for the temperature_calibration function to do better
    k = 1000000
    stop = MaxTime(60)
    return simulatedannealing(s0, model.neighbour, lambda t: temp(T0, k, t), stop)
```

And here are results!

```shell
> python tsp.py tsp.data
Elapsed time: 0:01:00.000178
Iterations performed: 286,124
Best solution: 286288.60456763074
```

Let's look at the convergence first. The blue curve represents the solutions that were accepted during the search, while the orange shows the cost of the best solution so far:
![Convergance of Model1, if I can say so!](fig/convergence1.png)
No very convincing, if you ask me! Maybe reducing the value for *k* might help a little, however the issue is rather that we were only able to perform less than 300,000 iterations within one minute, which is really scarce to explore a 100!-sized search space.

The corresponding tour goes accordingly:
![Solution of Model1!](fig/tsp1.png)
Not far from what the initial, random solution might look like.

As we can see, there is margin for progress here.

## Cutting (fixed) costs

A first, simple improvement we can achieve is the cost function. In our `Model1`, we keep computing the same distances again and again. However, those distances are fixed, and we don't have so many of them: only *n*<sub>2</sub> for *n* places to visit. We could pre-compute all distances, store them (e.g. in an *n*x*n* matrix) and access the pre-computed distance whenever needed.

This is an easy fix if we inherit from `Model1` to create... `Model2` (what did you expect?):
```python
class Model2(Model1):

    def __init__(self, places):
        super().__init__(places)
        self.distances = np.array([[pi.distance(pj) for pj in places] for pi in places])

    def cost(self, x):
        return sum(self.distances[x[i - 1], x[i]] for i in range(self.size))
```
Don't forget to change `Model1` by `Model2` in your `solve` function when you create the `model` object, and you will get enhanced results:

```shell
> python tsp.py tsp.data
Elapsed time: 0:01:00.000043
Iterations performed: 1,231,903
Best solution: 196348.26890073498
```
Wow, we could perform 4 times as many iterations, and reduced the optimal cost by a bit more than 30%!

We can see on the convergence plot that the algorithm indeed starts to converge:
![Convergance of Model2!](fig/convergence2.png)
The solution found starts to untangle.
![Solution of Model2!](fig/tsp2.png)
With the 1.2 millions iterations, our temperature scheme does not have the time to fully cool down.
With some `numpy` trickery, we can do yet better by defining the cost method a bit differently (note that we inherit from `Model2` to profit from the pre-computation of distances):
```python
class Model3(Model2):

    def cost(self, x):
        return sum(self.distances[x, np.concatenate((x[1:], x[:1]))])
```
with the following results:
```shell
> python tsp.py tsp.data
Elapsed time: 0:01:00.000012
Iterations performed: 1,911,754
Best solution: 139831.50035791812
```
We gained another 30% on the best solution, as we're beginning to truly converge, as shown here:
![Convergance of Model3!](fig/convergence3.png)
![Solution of Model3!](fig/tsp3.png)
This tour can almost be called... a tour! There are still some loops to unroll, but with one more minute, we would probably reach a decent solution (you can try it!).

Nice! However, it looks like we forgot some inefficiencies on the way...

## Cutting (fixed) costs: reloaded

Look closely at how we compute a neighbour: we take two places out of *n* in the sequence, swap them, and recompute the entire sum to get the cost of the new solution. How efficient is that? Not much! Most of the distances (*n* - 4 in the general case) are untouched, but still we recompute their sum as if they changed. Here comes to help *Delta Evaluation*. She only computes what's changed.

In our case, if we swapped places *i* and *j*, we changed the distances between *i* and its neighbours and between *j* and its neighbours, so we might as well just subtract from the cost these 4 distances and add back the new distances. With some careful arithmetic to deal with the last segment and a special case where *i* and *j* are adjacent in the solution, this leads to the following `Model4` (of course inherited from `Model3`):
```python
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
```
Remember when we said that packaging the solution and its cost in a `Candidate` object would come in handy? That's where it is! The fact that we exchange them as a whole makes it easy to perform delta evaluation without changing anything to the rest of the code.

Buckle up for the results:
```shell
> python tsp.py tsp.data
Elapsed time: 0:01:00.000011
Iterations performed: 5,777,207
Best solution: 93212.45648860329
```
What a difference! Within the same amount of time, we performed about 3 times more iterations than with the previous model, and gained another 33% on the cost of the best solution!

The following graph shows that the algorithm fully converged:
![Convergance of Model4!](fig/convergence5.png)
The solution provided looks pretty convincing, probably not that far from an optimal solution:
![Solution of Model4!](fig/tsp5.png)

## Summary

There could be many more upgrades to the model (check `tsp.py` for the complete code, with an extra model and some solution plotting). One thing to remember is that you can proceed incrementally, which is easier to handle and less error prone, as you can compare your new methods to your previous ones to ensure the sophisticated stuff you introduced behaves as well as the simple basic stuff (hopefully in a more efficient manner!). Also, don't hesitate to refer to the detailed documentation of the library, which contains a bit more than what is showcased in this extended example.
