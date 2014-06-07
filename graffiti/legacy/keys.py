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

from graffiti import util

__author__ = "Michael-Keith Bernard"

def expand_key(key, value, separator="__"):
    """Convert a key in the form 'foo<separator>bar' into the dict
    {"foo": {"bar": `value` } }
    """

    path = key.split(separator)
    return util.assoc_in({}, path, value)

def expand_keys(d, separator="__"):
    """Uses expand_key to expand all keys in `d`"""

    expanded = [expand_key(k, v, separator) for k, v in d.iteritems()]
    acc = {}
    for exp in expanded:
        acc = util.deep_merge_with(lambda _, v: v, acc, exp)
    return acc

def desimplify(coll, separator="__", recursive=False):
    """Applies expand_keys to all dicts in `coll`. If recursive is True, walks
    coll recursively and applies expand_keys to all sub dicts"""

    if recursive:
        return util.prewalk(lambda e: expand_keys(e, separator)
                                      if util.is_dict(e) else e, coll)
    else:
        return expand_keys(coll, separator)


def simplify(d, separator="__"):
    """Flatten nested dicts
    Converts a dict of the form:
        {"a": {"b": 1}}
    to the form:
        {"a__b": 1}
    """

    def _simplifier(d, prefix):
        acc = {}
        for k, v in d.iteritems():
            name = separator.join(prefix + [k])
            if isinstance(v, dict):
                acc = util.merge(acc, _simplifier(v, prefix + [k]))
            else:
                acc[name] = v
        return acc

    return _simplifier(d, [])

