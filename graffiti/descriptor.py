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

import util

__author__ = "Michael-Keith Bernard"

def thrush(v, *fns):
    return reduce(lambda v, f: f(v), fns, v)

def thunkify(e):
    return lambda: e

def build_fn_meta(descriptor):
    """Pre-compilation phase of graph descriptor"""

    def _compile(e):
        if isinstance(e, dict):
            return build_fn_meta(e)
        if callable(e):
            return util.fninfo(e)

        return util.fninfo(thunkify(e))

    return { k: _compile(v) for k, v in descriptor.iteritems() }

def compile_graph(descriptor):
    return thrush(descriptor,
        build_fn_meta)

if __name__ == "__main__":
    desc = {
        "a": 1,
        "b": lambda a: a + 1,
        "c": {
            "d": 2,
            "e": lambda d: d + 2,
        },
    }

    import pprint
    pprint.pprint(compile_graph(desc))
