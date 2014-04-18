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

from functools import partial

__author__ = "Michael-Keith"

def identity(e):
    """The identity function, returns `e` exactly"""

    return e

def is_dict(d):
    """Returns true if `d` is a subclass of dict"""

    return isinstance(d, dict)

def group_by(fn, l):
    """Group elements in `l` by a keying function `fn`"""

    acc = {}
    for e in l:
        key = fn(e)
        if key not in acc:
            acc[key] = []
        acc[key].append(e)
    return acc

def select_keys(fn, d):
    """Returns a new dict with keys where the predicate function is truthy"""

    return { k: v for k, v in d.iteritems() if fn(k, v) }

def assoc(d, k, v):
    """Adds key `k` with value `v` to dicts `d`. If `d` is None, a new dict is
    created instead.
    """

    if d is None:
        d = {}
    d[k] = v
    return d

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
        return assoc(d, key, assoc_in(d.get(key), rest, v))

def merge(*dicts):
    """Merges any number of dicts together, replacing repeated keys"""

    return { k: v for d in dicts for k, v in d.iteritems() }

def deep_merge_with(fn, *dicts):
    """Like merge, but preserves shared key paths recursively. `fn` is applied
    to values of dicts when collisions occur.
    """

    def _merge(d1, d2):
        for k, v in d2.iteritems():
            if k in d1:
                if is_dict(d1[k]) and is_dict(v):
                    d1[k] = _merge(d1[k], v)
                else:
                    d1[k] = fn(d1[k], v)
            else:
                d1[k] = v
        return d1
    return reduce(_merge, dicts, {})

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

