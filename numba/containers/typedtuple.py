import numba as nb
from numba import *
from numba import typesystem
from numba.containers import orderedcontainer

import numpy as np

INITIAL_BUFSIZE = 5

def notimplemented(msg):
    raise NotImplementedError("'%s' method of type 'typedtuple'" % msg)

_tuple_cache = {}

def typedtuple(item_type, iterable=None, _tuple_cache=_tuple_cache):
    """
    >>> typedtuple(int_)
    ()
    >>> ttuple = typedtuple(int_, range(10))
    >>> ttuple
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    >>> ttuple[5]
    5L

    >>> typedtuple(float_, range(10))
    (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
    """
    if item_type in _tuple_cache:
        return _tuple_cache[item_type](item_type, item_type.get_dtype(), iterable)

    item_type_t = typesystem.CastType(item_type)
    dtype_t = typesystem.NumpyDtypeType(item_type)

    methods = orderedcontainer.container_methods(item_type, notimplemented)

    @jit(warn=False)
    class typedtuple(object):
        @void(item_type_t, dtype_t, object_)
        def __init__(self, item_type, dtype, iterable):
            # self.item_type = item_type
            item_type
            self.dtype = dtype
            self.size = 0

            # TODO: Use length hint of iterable for initial buffer size
            self.buf = np.empty(INITIAL_BUFSIZE, dtype=dtype)

            if iterable != None:
                self.__extend(iterable)

        __getitem__ = methods['getitem']
        __append = methods['append']
        index = methods['index']
        count = methods['count']

        @void(object_)
        def __extend(self, iterable):
            for obj in iterable:
                self.__append(obj)

        @Py_ssize_t()
        def __len__(self):
            return self.size

        @nb.c_string_type()
        def __repr__(self):
            buf = ", ".join([str(self.buf[i]) for i in range(self.size)])
            return "(" + buf + ")"

    _tuple_cache[item_type] = typedtuple
    return typedtuple(item_type, item_type.get_dtype(), iterable)


if __name__ == "__main__":
    import doctest
    doctest.testmod()