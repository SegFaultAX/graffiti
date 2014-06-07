# Copyright (c) 2014 Michael-Keith Bernard

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import copy
import inspect
from functools import partial

__author__ = "Michael-Keith"

def identity(e):
    """The identity function, returns `e` exactly"""

    return e

def is_dict(d):
    """Returns true if `d` is a subclass of dict"""

    return isinstance(d, dict)

def fninfo(fn):
    """Gathers argument information about a function.
    Returns the tuple `(required arguments, optional arguments)`
    """

    args, varargs, keywords, defaults = inspect.getargspec(fn)
    defaults = defaults or []

    required = args[:-len(defaults)] if defaults else args
    optional = dict(zip(args[-len(defaults):], defaults))

    return {
        "fn": fn,
        "args": args,
        "required": set(required),
        "optional": optional,
    }

def get(c, k, default=None):
    try:
        return c[k]
    except (KeyError, TypeError, IndexError, ValueError):
        return default

def get_in(c, ks, default=None):
    for k in ks:
        c = get(c, k, default)
        if c is default:
            break
    return c

def concat(*lists):
    """Concatenate multiple lists together"""

    return (e for l in lists for e in l)

def concat1(it):
    """Like concat, but accepts a single iterator"""

    return (e for es in it for e in es)

def iterate(fn, init):
    """Prodcue values of fn by repeatedly applying it to init, yielding:
        init, fn(init), fn(fn(init)), fn(fn(fn(init))), ...
    """

    while True:
        yield init
        init = fn(init)

def fixpoint(fn, inputs, cmp=None, max_iter=10000):
    """Find fixpoint for a function and set of starting inputs. `cmp` tests if a
    fixpoint has been computed. If `max_iter` is None, the algorithm will run
    indefinitely
    """

    if cmp is None:
        cmp = lambda a, b: a == b

    it = iterate(fn, inputs)
    prev = next(it)

    for idx, e in enumerate(it):
        if cmp(prev, e):
            return e
        if max_iter and idx >= max_iter:
            msg = "Unable to determine fixpoint after {} iterations".format(
                max_iter)
            raise ValueError(msg)
        prev = e

def categorize(fn, l):
    acc = {}
    for e in l:
        for key in fn(e):
            acc.setdefault(key, []).append(e)
    return acc

def group_by(fn, l):
    return categorize(lambda e: [fn(e)], l)

def select_keys(fn, d):
    """Returns a new dict with keys where the predicate function is truthy"""

    return { k: v for k, v in d.iteritems() if fn(k, v) }

def mapkv(fn, d):
    """Apply `fn` to each k/v pair of `d`
    `fn` should return a new (k, v) pair
    """

    return dict(fn(k, v) for k, v in d.iteritems())

def map_keys(fn, d):
    """Applies `fn` to all keys of `d`
    `fn` should return a new key for pair
    """

    return mapkv(lambda k, v: (fn(k), v), d)

def map_vals(fn, d):
    """Applies `fn` to all values of `d`
    `fn` should return a new value for pair
    """

    return mapkv(lambda k, v: (k, fn(v)), d)

def assoc(d, k, v):
    """Adds key `k` with value `v` to dicts `d`. If `d` is None, a new dict is
    created instead.
    """

    if d is None:
        d = {}
    d2 = copy.copy(d)
    d2[k] = v
    return d2

def assoc_in(d, key_path, v):
    """Adds a value `v` into the dict `d` by traversing key_path recursively. If
    any key is not found, a new dict will be created.
    """

    if not key_path:
        raise ValueError("Cannot provide empty key path")
    key, rest = key_path[0], key_path[1:]
    if not rest:
        return assoc(d, key, v)
    else:
        return assoc(d, key, assoc_in(get(d, key), rest, v))

def merge_with(fn, *dicts):
    """Merge 2 or more dicts, using `fn` for conflicting values"""

    def _merge(d1, d2):
        for k, v in d2.iteritems():
            if k in d1:
                d1[k] = fn(d1[k], v)
            else:
                d1[k] = v
        return d1
    return reduce(_merge, dicts, {})

def merge(*dicts):
    """Like `merge_with`, but last value always wins"""

    return merge_with(lambda _, v: v, *dicts)

def deep_merge_with(fn, *dicts):
    """Like `merge_with`, but nested dicts are merged recursively"""

    def _merge(v1, v2):
        if is_dict(v1) and is_dict(v2):
            return deep_merge_with(fn, v1, v2)
        else:
            return fn(v1, v2)
    return merge_with(_merge, *dicts)

def deep_merge(*dicts):
    """Like `deep_merge_with`, but last value wins for non-dict conflicts"""

    return deep_merge_with(lambda _, v: v, *dicts)

def walk(inner, outer, coll):
    """Walks `coll` calling `inner` on each element and `outer` on each
    collection. Currently only lists, dicts, and tuples are walked.
    """

    if isinstance(coll, list):
        return outer([inner(e) for e in coll])
    elif isinstance(coll, dict):
        return outer(dict([inner(e) for e in coll.iteritems()]))
    elif isinstance(coll, tuple):
        return outer([inner(e) for e in coll])
    else:
        return outer(coll)

def prewalk(fn, coll):
    """Pre-order walk over `coll`"""

    return walk(partial(prewalk, fn), identity, fn(coll))

