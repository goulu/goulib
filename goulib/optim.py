"""
various optimization algorithms : knapsack, traveling salesman, simulated annealing, differential evolution
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2015, Philippe Guglielmetti"
__credits__ = [
    "http://www.psychicorigami.com/category/tsp/",
    "http://cci.lbl.gov/cctbx_sources/scitbx/differential_evolution.py",
    "https://github.com/fchollet/nelder-mead",
]
__license__ = "LGPL"

import logging
import math
import random
import copy

from .itertools2 import all_pairs, index_min, sort_indexes
from .stats import mean
from .math2 import vecadd, vecsub, vecmul

import copy


class ObjectiveFunction:
    '''class to wrap an objective function and
    keep track of the best solution evaluated'''

    def __init__(self, objective_function):
        self.objective_function = objective_function
        self.best = None
        self.best_score = None

    def __call__(self, solution):
        score = self.objective_function(solution)
        if self.best is None or score > self.best_score:
            self.best_score = score
            self.best = solution
            logging.info('new best score: %f', self.best_score)
        return score


def nelder_mead(f, x_start,
                step=0.1, no_improve_thr=10e-6, no_improv_break=10, max_iter=0,
                alpha=1., gamma=2., rho=-0.5, sigma=0.5):
    """Pure Python implementation of the Nelder-Mead algorithm.

    Also called "downhill simplex method" taken from https://github.com/fchollet/nelder-mead
    Reference: https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method

    :param f: function to optimize, must return a scalar score 
        and operate over a numpy array of the same dimensions as x_start
    :param x_start: (numpy array) initial position
    :param step: (float) look-around radius in initial step
    :param no_improve_thr: (float) threshold for improvement
    :param no_improv_break: (int) break after iterations with no improvement
    :param max_iter: (int) always break after this number of iterations. Set it to 0 to loop indefinitely.
    :param alpha: parameter of the algorithm (float)
    :param gamma: parameter of the algorithm (float)
    :param rho: parameter of the algorithm (float)
    :param sigma: parameter of the algorithm (float)
    """

    # init
    dim = len(x_start)
    prev_best = f(x_start)
    no_improv = 0
    res = [[x_start, prev_best]]

    for i in range(dim):
        x = copy.copy(x_start)
        x[i] = x[i] + step
        score = f(x)
        res.append([x, score])

    # simplex iter
    iters = 0
    while 1:
        # order
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        # break after max_iter
        if max_iter and iters >= max_iter:
            return res[0]
        iters += 1

        # break after no_improv_break iterations with no improvement
        logging.info('...best so far:%s' % best)

        if best < prev_best - no_improve_thr:
            no_improv = 0
            prev_best = best
        else:
            no_improv += 1

        if no_improv >= no_improv_break:
            return res[0]

        # centroid
        x0 = [0.] * dim
        for tup in res[:-1]:
            for i, c in enumerate(tup[0]):
                x0[i] += c / (len(res)-1)

        # reflection
        xr = vecadd(x0, vecmul(alpha, vecsub(x0, res[-1][0])))
        rscore = f(xr)
        if res[0][1] <= rscore < res[-2][1]:
            del res[-1]
            res.append([xr, rscore])
            continue

        # expansion
        if rscore < res[0][1]:
            xe = vecadd(x0, vecmul(gamma, vecsub(x0, res[-1][0])))
            escore = f(xe)
            if escore < rscore:
                del res[-1]
                res.append([xe, escore])
                continue
            else:
                del res[-1]
                res.append([xr, rscore])
                continue

        # contraction
        xc = vecadd(x0, vecmul(rho, vecsub(x0, res[-1][0])))
        cscore = f(xc)
        if cscore < res[-1][1]:
            del res[-1]
            res.append([xc, cscore])
            continue

        # reduction
        x1 = res[0][0]
        nres = []
        for tup in res:
            redx = vecadd(x1, vecmul(sigma*(tup[0] - x1)))
            score = f(redx)
            nres.append([redx, score])
        res = nres


class _Bin():
    def __init__(self, capacity, f=lambda x: x):
        """a container with a limited capacity
        :param capacity: int,float,tuple of whatever defines the capacity of the Bin
        :param f: function f(x) returning the capacity used by item x. Must return the empty capacity when f(0) is called
        """
        self._capacity = capacity
        self._f = f  # functions that return the cached values of an item
        self._used = f(0)

    def __repr__(self):
        try:
            used=sorted(self._used)
        except TypeError:
            used=self._used
        return '%s(%s/%s)' % (self.__class__.__name__, used, self._capacity)

    def _add(self, value, tot=None):
        """update sum when item is added"""
        if not tot:
            tot = self._used
        if isinstance(value, (int, float)):
            return tot + value
        if isinstance(value, set):
            return tot | value
        return list(map(self._add, list(zip(value, tot))))

    def _recalc(self):
        self._used = self._f(0)
        for item in self:
            self._used = self._add(self._f(item))

    def _sub(self, value, tot=None):
        """update sum AFTER item is removed"""
        if not tot:
            tot = self._used
        if isinstance(value, (int, float)):
            return tot - value
        if isinstance(value, set):
            if isinstance(tot, (int, float)):
                return tot - len(value)
            else:
                try:
                    i = self._used(tot)  # index of set
                except:
                    i = None
                self._recalc()
                return self._used[i] if i is not None else self._used

        return list(map(self._sub, list(zip(value, tot))))

    def size(self):
        return self._sub(self._used, self._capacity)

    def _fits(self, value, cap=None):
        """compare value to capacity"""
        if cap is None:
            cap = self._capacity
        if isinstance(value, (int, float)):
            return value <= cap
        if isinstance(value, set):
            return len(value) <= cap
        return all(map(self._fits, list(zip(value, cap))))

    def fits(self, item):
        """:return: bool True if item fits in bin without exceeding capacity"""
        return self._fits(self._add(self._f(item)))

    def __iadd__(self, item):
        """addition of an element : MUST BE OVERLOADED by subclasses"""
        if not self.fits(item):
            raise OverflowError
        self._used = self._add(self._f(item))
        return self

    def __isub__(self, item):
        """removal of an element : MUST BE OVERLOADED by subclasses and called AFTER item is removed"""
        self._used = self._sub(self._f(item))
        return self


class BinDict(_Bin, dict):
    # http://docs.python.org/2/reference/datamodel.html#emulating-container-types

    def __isub__(self, key):
        item = self[key]
        super(BinDict, self).__delitem__(key)  # must be first
        super(BinDict, self).__isub__(item)  # must be next
        return self

    __delitem__ = __isub__

    def __iadd__(self, key, item):
        if key in self:
            del self[key]
        super(BinDict, self).__iadd__(item)  # raises OverflowError if full
        super(BinDict, self).__setitem__(key, item)
        return self

    __setitem__ = __iadd__


class BinList(_Bin, list):
    # http://docs.python.org/2/reference/datamodel.html#emulating-container-types

    def __iadd__(self, item):
        super(BinList, self).__iadd__(item)  # raises OverflowError if full
        super(BinList, self).append(item)
        return self

    append = __iadd__

    def insert(self, i, item):
        super(BinList, self).__iadd__(item)  # raises OverflowError if full
        super(BinList, self).insert(i, item)
        return self

    def extend(self, more):
        for x in more:
            self.append(x)
        return self

    def __isub__(self, item):
        super(BinList, self).remove(item)
        super(BinList, self).__isub__(item)
        return self

    remove = __isub__

    def pop(self, i=-1):
        item = super(BinList, self).pop(i)
        super(BinList, self).__isub__(item)
        return item

    def __setitem__(self, i, item):
        """called when replacing a value in list"""
        old = self[i]
        super(BinList, self).__isub__(old)
        super(BinList, self).__iadd__(item)  # raises OverflowError if full
        super(BinList, self).__setitem__(i, item)

# Bin packing algorithms
# see https://en.wikipedia.org/wiki/Bin_packing_problem


def first_fit_decreasing(items, bins, maxbins=0):
    """ fit items in bins using the "first fit decreasing" method
    :param items: iterable of items
    :param bins: iterable of Bin s. Must have at least one Bin
    :return: list of items that didn't fit. (bins are filled by side-effect)
    """

    nofit = []
    items.sort(key=lambda x: bins[0]._f(x), reverse=True)
    for item in items:
        fit = False
        for b in bins:
            try:
                b += item
                fit = True
                break
            except OverflowError:
                continue  # next bin ?
        if not fit:  # may we add a bin ?
            if len(bins) < maxbins:  # yes
                b = type(bins[0])(bins[0]._capacity, bins[0]._f)
                try:
                    b += item
                    bins.append(b)
                    continue  # next item
                except OverflowError:  # item too large for a bin
                    pass
            nofit.append(item)
    return nofit


def hillclimb(init_function, move_operator, objective_function, max_evaluations):
    '''
    hillclimb until either max_evaluations is reached or we are at a local optima
    '''
    best = init_function()
    best_score = objective_function(best)

    num_evaluations = 1

    logging.info('hillclimb started: score=%f', best_score)

    while num_evaluations < max_evaluations:
        # examine moves around our current position
        move_made = False
        for m in move_operator(best):
            if num_evaluations >= max_evaluations:
                break

            # see if this move is better than the current
            next_score = objective_function(m)
            num_evaluations += 1
            if next_score > best_score:
                best = m
                best_score = next_score
                move_made = True
                break  # depth first search

        if not move_made:
            # we couldn't find a better move (must be at a local maximum)
            break

    logging.info('hillclimb finished: num_evaluations=%d, best_score=%f',
                 num_evaluations, best_score)
    return (num_evaluations, best_score, best)


def hillclimb_and_restart(init_function, move_operator, objective_function, max_evaluations):
    '''
    repeatedly hillclimb until max_evaluations is reached
    '''
    best = None
    best_score = 0

    num_evaluations = 0
    while num_evaluations < max_evaluations:
        remaining_evaluations = max_evaluations - num_evaluations

        logging.info('(re)starting hillclimb %d/%d remaining',
                     remaining_evaluations, max_evaluations)
        evaluated, score, found = hillclimb(
            init_function, move_operator, objective_function, remaining_evaluations)

        num_evaluations += evaluated
        if score > best_score or best is None:
            best_score = score
            best = found

    return (num_evaluations, best_score, best)


def P(prev_score, next_score, temperature):
    if next_score > prev_score:
        return 1.0
    else:
        return math.exp(-abs(next_score - prev_score) / temperature)


def kirkpatrick_cooling(start_temp, alpha):
    T = start_temp
    while True:
        yield T
        T = alpha * T


def anneal(init_function, move_operator, objective_function, max_evaluations, start_temp, alpha):

    # wrap the objective function (so we record the best)
    objective_function = ObjectiveFunction(objective_function)

    current = init_function()
    current_score = objective_function(current)
    num_evaluations = 1

    cooling_schedule = kirkpatrick_cooling(start_temp, alpha)

    logging.info('anneal started: score=%f', current_score)

    for temperature in cooling_schedule:
        done = False
        # examine moves around our current position
        for next in move_operator(current):
            if num_evaluations >= max_evaluations:
                done = True
                break

            next_score = objective_function(next)
            num_evaluations += 1

            # probablistically accept this solution
            # always accepting better solutions
            p = P(current_score, next_score, temperature)
            if random.random() < p:
                current = next
                current_score = next_score
                break
        # see if completely finished
        if done:
            break

    best_score = objective_function.best_score
    best = objective_function.best
    logging.info('final temperature: %f', temperature)
    logging.info('anneal finished: num_evaluations=%d, best_score=%f',
                 num_evaluations, best_score)
    return (num_evaluations, best_score, best)


def reversed_sections(tour):
    '''generator to return all possible variations where the section between two cities are swapped'''
    for i, j in all_pairs(len(tour)):
        if i and j and i < j:
            copy = tour[:]
            copy[i:j + 1] = reversed(tour[i:j + 1])
            yield copy


def swapped_cities(tour):
    '''generator to create all possible variations where two cities have been swapped'''
    for i, j in all_pairs(len(tour)):
        if i < j:
            copy = tour[:]
            copy[i], copy[j] = tour[j], tour[i]
            yield copy


def tour_length(points, dist, tour=None):
    """generator of point-to-point distances along a tour"""
    if not tour:
        tour = list(range(len(points)))  # will generate the closed tour length
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        yield dist(points[tour[i]], points[tour[j]])


def tsp(points, dist, max_iterations=100, start_temp=None, alpha=None, close=True, rand=True):
    """Traveling Salesman Problem
    @see http://en.wikipedia.org/wiki/Travelling_salesman_problem
    @param points : iterable containing all points
    @param dist : function returning the distance between 2 points : def dist(a,b):
    @param max_iterations :max number of optimization steps
    @param start_temp, alpha : params for the simulated annealing algorithm. if None, hill climbing is used
    @param close : computes closed TSP. if False, open TSP starting at points[0]
    @return iterations,score,best : number of iterations used, minimal length found, best path as list of indexes of points
    """
    n = len(points)

    def init_function():
        tour = list(range(1, n))
        if rand:
            random.shuffle(tour)
        return [0] + tour

    def objective_function(tour):
        """total up the total length of the tour based on the dist ance function"""
        return -sum(tour_length(points, dist, tour if close else tour[:-1]))
    if start_temp is None or alpha is None:
        iterations, score, best = hillclimb_and_restart(
            init_function, reversed_sections, objective_function, max_iterations)
    else:
        iterations, score, best = anneal(
            init_function, reversed_sections, objective_function, max_iterations, start_temp, alpha)
    return iterations, score, best


class DifferentialEvolution(object):
    """
    This is a python implementation of differential evolution taken from
    http://cci.lbl.gov/cctbx_sources/scitbx/differential_evolution.py

    It assumes an evaluator class is passed in that has the following functionality:

    Data members:
    - n: The number of parameters
    - domain: a list [(low,high)]*n with approximate upper and lower limits for each parameter
    - x: a place holder for a final solution

    Also a function called 'target' is needed.
    This function should take a parameter vector as input and return the function to be minimized.

    The code below was implemented on the basis of the following sources of information:
    1. http://www.icsi.berkeley.edu/~storn/code.html
    2. http://www.daimi.au.dk/~krink/fec05/articles/JV_ComparativeStudy_CEC04.pdf
    3. http://ocw.mit.edu/NR/rdonlyres/Sloan-School-of-Management/15-099Fall2003/A40397B9-E8FB-4B45-A41B-D1F69218901F/0/ses2_storn_price.pdf

    The developers of the differential evolution method have this advice (taken from ref. 1):

    If you are going to optimize your own objective function with DE, you may try the
    following classical settings for the input file first: Choose method e.g. DE/rand/1/bin,
    set the number of parents NP to 10 times the number of parameters, select weighting
    factor F=0.8, and crossover constant CR=0.9. It has been found recently that selecting
    F from the interval [0.5, 1.0] randomly for each generation or for each difference
    vector, a technique called dither, improves convergence behaviour significantly,
    especially for noisy objective functions. It has also been found that setting CR to a
    low value, e.g. CR=0.2 helps optimizing separable functions since it fosters the search
    along the coordinate axes. On the contrary this choice is not effective if parameter
    dependence is encountered, something which is frequently occuring in real-world optimization
    problems rather than artificial test functions. So for parameter dependence the choice of
    CR=0.9 is more appropriate. Another interesting empirical finding is that rasing NP above,
    say, 40 does not substantially improve the convergence, independent of the number of
    parameters. It is worthwhile to experiment with these suggestions. Make sure that you
    initialize your parameter vectors by exploiting their full numerical range, i.e. if a
    parameter is allowed to exhibit values in the range [-100, 100] it's a good idea to pick
    the initial values from this range instead of unnecessarily restricting diversity.

    Keep in mind that different problems often require different settings for NP, F and CR
    (have a look into the different papers to get a feeling for the settings). If you still
    get misconvergence you might want to try a different method. We mostly use DE/rand/1/... or DE/best/1/... .
    The crossover method is not so important although Ken Price claims that binomial is never
    worse than exponential. In case of misconvergence also check your choice of objective
    function. There might be a better one to describe your problem. Any knowledge that you
    have about the problem should be worked into the objective function. A good objective
    function can make all the difference.

    Note: NP is called population size in the routine below.)
    Note: [0.5,1.0] dither is the default behavior unless f is set to a value other then None.
    """

    def __init__(self,
                 evaluator,
                 population_size=50,
                 f=None,
                 cr=0.9,
                 eps=1e-2,
                 n_cross=1,
                 max_iter=10000,
                 monitor_cycle=200,
                 out=None,
                 show_progress=False,
                 show_progress_nth_cycle=1,
                 insert_solution_vector=None,
                 dither_constant=0.4):
        self.dither = dither_constant
        self.show_progress = show_progress
        self.show_progress_nth_cycle = show_progress_nth_cycle
        self.evaluator = evaluator
        self.population_size = population_size
        self.f = f
        self.cr = cr
        self.n_cross = n_cross
        self.max_iter = max_iter
        self.monitor_cycle = monitor_cycle
        self.vector_length = evaluator.n
        self.eps = eps
        self.population = []
        self.seeded = False
        if insert_solution_vector is not None:
            assert len(insert_solution_vector) == self.vector_length
            self.seeded = insert_solution_vector
        for _ in range(self.population_size):
            self.population.append([0.]*self.vector_length)

        self.scores = [1000]*self.population_size
        self.optimize()
        self.best_score = min(self.scores)
        self.best_vector = self.population[index_min(self.scores)[0]]
        self.evaluator.x = self.best_vector
        if self.show_progress:
            self.evaluator.print_status(
                min(self.scores),
                mean(self.scores),
                self.population[index_min(self.scores)[0]],
                'Final')

    def optimize(self):
        # initialise the population please
        self.make_random_population()
        # score the population please
        self.score_population()
        converged = False
        monitor_score = min(self.scores)
        self.count = 0
        while not converged:
            self.evolve()
            # location,_ = index_min(self.scores)
            if self.show_progress:
                if self.count % self.show_progress_nth_cycle == 0:
                    # make here a call to a custom print_status function in the evaluator function
                    # the function signature should be (min_target, mean_target, best vector)
                    self.evaluator.print_status(
                        min(self.scores),
                        mean(self.scores),
                        self.population[index_min(self.scores)[0]],
                        self.count)

            self.count += 1
            if self.count % self.monitor_cycle == 0:
                if (monitor_score - min(self.scores)) < self.eps:
                    converged = True
                else:
                    monitor_score = min(self.scores)
            rd = (mean(self.scores) - min(self.scores))
            rd = rd * rd / (min(self.scores) * min(self.scores) + self.eps)
            if (rd < self.eps):
                converged = True

            if self.count >= self.max_iter:
                converged = True

    def make_random_population(self):
        for ii in range(self.vector_length):
            delta = self.evaluator.domain[ii][1] - self.evaluator.domain[ii][0]
            offset = self.evaluator.domain[ii][0]
            random_values = [
                random.uniform(offset, offset+delta)
                for _ in range(self.population_size - 1)
            ]
            # now place these values ni the proper places in the
            # vectors of the population we generated
            for vector, item in zip(self.population, random_values):
                vector[ii] = item
        if self.seeded is not False:
            self.population[0] = self.seeded

    def score_population(self):
        for vector, ii in zip(self.population, range(self.population_size)):
            tmp_score = self.evaluator.target(vector)
            self.scores[ii] = tmp_score

    def evolve(self):
        for ii in range(self.population_size):
            rnd = [random.random() for _ in range(self.population_size - 1)]
            permut = sort_indexes(rnd)
            # make parent indices
            i1 = permut[0]
            if (i1 >= ii):
                i1 += 1
            i2 = permut[1]
            if (i2 >= ii):
                i2 += 1
            i3 = permut[2]
            if (i3 >= ii):
                i3 += 1
            #
            x1 = self.population[i1]
            x2 = self.population[i2]
            x3 = self.population[i3]

            if self.f is None:
                use_f = random.random() / 2.0 + 0.5
            else:
                use_f = self.f

            vi = vecadd(x1, vecmul(use_f, vecsub(x2, x3)))
            # prepare the offspring vector
            rnd = [random.random() for _ in range(self.vector_length)]
            permut = sort_indexes(rnd)
            test_vector = copy.copy(self.population[ii])  # deep_copy ?
            # first the parameters that sure cross over
            for jj in range(self.vector_length):
                if (jj < self.n_cross):
                    test_vector[permut[jj]] = vi[permut[jj]]
                else:
                    if (rnd[jj] > self.cr):
                        test_vector[permut[jj]] = vi[permut[jj]]
            # get the score
            test_score = self.evaluator.target(test_vector)
            # check if the score if lower
            if test_score < self.scores[ii]:
                self.scores[ii] = test_score
                self.population[ii] = test_vector
