from __future__ import print_function
import numba.unittest_support as unittest
import itertools
import numpy as np
from numba.compiler import compile_isolated, Flags
from numba import types, utils
from numba.tests import usecases

enable_pyobj_flags = Flags()
enable_pyobj_flags.set("enable_pyobject")

force_pyobj_flags = Flags()
force_pyobj_flags.set("force_pyobject")


class TestUsecases(unittest.TestCase):
    def test_andor(self):
        pyfunc = usecases.andor
        cr = compile_isolated(pyfunc, (types.int32, types.int32))
        cfunc = cr.entry_point

        # Argument boundaries
        xs = -1, 0, 1, 9, 10, 11
        ys = -1, 0, 1, 9, 10, 11

        for args in itertools.product(xs, ys):
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args), "args %s" % (args,))

    def test_sum1d(self):
        pyfunc = usecases.sum1d
        cr = compile_isolated(pyfunc, (types.int32, types.int32))
        cfunc = cr.entry_point

        ss = -1, 0, 1, 100, 200
        es = -1, 0, 1, 100, 200

        for args in itertools.product(ss, es):
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

    def test_sum1d_pyobj(self):
        pyfunc = usecases.sum1d
        cr = compile_isolated(pyfunc, (types.int32, types.int32),
                              flags=force_pyobj_flags)
        cfunc = cr.entry_point

        ss = -1, 0, 1, 100, 200
        es = -1, 0, 1, 100, 200

        for args in itertools.product(ss, es):
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

        args = 0, 500

        def bm_python():
            pyfunc(*args)

        def bm_numba():
            cfunc(*args)

        print(utils.benchmark(bm_python, maxsec=.1))
        print(utils.benchmark(bm_numba, maxsec=.1))

    def test_sum2d(self):
        pyfunc = usecases.sum2d
        cr = compile_isolated(pyfunc, (types.int32, types.int32))
        cfunc = cr.entry_point

        ss = -1, 0, 1, 100, 200
        es = -1, 0, 1, 100, 200

        for args in itertools.product(ss, es):
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

    def test_while_count(self):
        pyfunc = usecases.while_count
        cr = compile_isolated(pyfunc, (types.int32, types.int32))
        cfunc = cr.entry_point

        ss = -1, 0, 1, 100, 200
        es = -1, 0, 1, 100, 200

        for args in itertools.product(ss, es):
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

    def test_copy_arrays(self):
        pyfunc = usecases.copy_arrays
        arraytype = types.Array(types.int32, 1, 'A')
        cr = compile_isolated(pyfunc, (arraytype, arraytype))
        cfunc = cr.entry_point

        nda = 0, 1, 10, 100

        for nd in nda:
            a = np.arange(nd, dtype='int32')
            b = np.empty_like(a)
            args = a, b

            print("case", args)
            cfunc(*args)
            self.assertTrue(np.all(a == b))

    def test_copy_arrays2d(self):
        pyfunc = usecases.copy_arrays2d
        arraytype = types.Array(types.int32, 2, 'A')
        cr = compile_isolated(pyfunc, (arraytype, arraytype))
        cfunc = cr.entry_point

        nda = (0, 0), (1, 1), (2, 5), (4, 25)

        for nd in nda:
            d1, d2 = nd
            a = np.arange(d1 * d2, dtype='int32').reshape(d1, d2)
            b = np.empty_like(a)
            args = a, b

            print("case", args)
            cfunc(*args)
            self.assertTrue(np.all(a == b))

    def test_ifelse1(self):
        self.run_ifelse(usecases.ifelse1)

    def test_ifelse2(self):
        self.run_ifelse(usecases.ifelse2)

    def test_ifelse3(self):
        self.run_ifelse(usecases.ifelse3)

    def run_ifelse(self, pyfunc):
        cr = compile_isolated(pyfunc, (types.int32, types.int32))
        cfunc = cr.entry_point

        xs = -1, 0, 1
        ys = -1, 0, 1

        for x, y in itertools.product(xs, ys):
            args = x, y
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

    def test_string_concat(self):
        pyfunc = usecases.string_concat
        cr = compile_isolated(pyfunc, (types.int32, types.int32),
                              flags=enable_pyobj_flags)
        cfunc = cr.entry_point

        xs = -1, 0, 1
        ys = -1, 0, 1

        for x, y in itertools.product(xs, ys):
            args = x, y
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

    def test_string_len(self):
        pyfunc = usecases.string_len
        cr = compile_isolated(pyfunc, (types.pyobject,),
                              flags=enable_pyobj_flags)
        cfunc = cr.entry_point

        test_str = '123456'
        self.assertEqual(pyfunc(test_str), cfunc(test_str))
        test_str = '1'
        self.assertEqual(pyfunc(test_str), cfunc(test_str))
        test_str = ''
        self.assertEqual(pyfunc(test_str), cfunc(test_str))

    def test_string_slicing(self):
        pyfunc = usecases.string_slicing
        cr = compile_isolated(pyfunc, (types.pyobject,),
                              flags=enable_pyobj_flags)
        cfunc = cr.entry_point

        test_str = '123456'
        self.assertEqual(pyfunc(test_str, 0, 3), cfunc(test_str, 0, 3))
        self.assertEqual(pyfunc(test_str, 1, 5), cfunc(test_str, 1, 5))
        self.assertEqual(pyfunc(test_str, 2, 3), cfunc(test_str, 2, 3))
        
    def test_string_conversion(self):
        pyfunc = usecases.string_conversion

        cr = compile_isolated(pyfunc, (types.int32,),
                              flags=enable_pyobj_flags)
        cfunc = cr.entry_point
        self.assertEqual(pyfunc(1), cfunc(1))

        cr = compile_isolated(pyfunc, (types.float32,),
                              flags=enable_pyobj_flags)
        cfunc = cr.entry_point
        self.assertEqual(pyfunc(1.1), cfunc(1.1))

    def test_string_comparisons(self):
        import operator
        pyfunc = usecases.string_comparison
        cr = compile_isolated(pyfunc, (types.pyobject, types.pyobject),
                              flags=enable_pyobj_flags)
        cfunc = cr.entry_point

        test_str1 = '123'
        test_str2 = '123'
        op = operator.eq
        self.assertEqual(pyfunc(test_str1, test_str2, op),
            cfunc(test_str1, test_str2, op))

        test_str1 = '123'
        test_str2 = '456'
        op = operator.eq
        self.assertEqual(pyfunc(test_str1, test_str2, op),
            cfunc(test_str1, test_str2, op))

        test_str1 = '123'
        test_str2 = '123'
        op = operator.ne
        self.assertEqual(pyfunc(test_str1, test_str2, op),
            cfunc(test_str1, test_str2, op))

        test_str1 = '123'
        test_str2 = '456'
        op = operator.ne
        self.assertEqual(pyfunc(test_str1, test_str2, op),
            cfunc(test_str1, test_str2, op))

    def test_blackscholes_cnd(self):
        pyfunc = usecases.blackscholes_cnd
        cr = compile_isolated(pyfunc, (types.float32,))
        cfunc = cr.entry_point

        ds = -0.5, 0, 0.5

        for d in ds:
            args = (d,)
            print("case", args)
            self.assertEqual(pyfunc(*args), cfunc(*args))

    def test_array_slicing(self):
        pyfunc = usecases.slicing

        arraytype = types.Array(types.int32, 1, 'C')
        argtys = (arraytype, types.intp, types.intp, types.intp)
        cr = compile_isolated(pyfunc, argtys, flags=enable_pyobj_flags)
        cfunc = cr.entry_point

        a = np.arange(10, dtype='i4')

        cases = [
            (a, 0, 10, 1),
            (a, 0, 10, 2),
            (a, 0, 10, -1),
            (a, 2, 3, 1),
            (a, 10, 0, 1),
        ]
        for args in cases:
            self.assertTrue(np.all(pyfunc(*args) == cfunc(*args)))

        arraytype = types.Array(types.int32, 2, 'C')
        argtys = (arraytype, types.intp, types.intp, types.intp)
        cr = compile_isolated(pyfunc, argtys, flags=enable_pyobj_flags)
        cfunc = cr.entry_point

        a = np.arange(100, dtype='i4').reshape(10, 10)

        cases = [
            (a, 0, 10, 1),
            (a, 0, 10, 2),
            (a, 0, 10, -1),
            (a, 2, 3, 1),
            (a, 10, 0, 1),
        ]
        for args in cases:
            self.assertTrue(np.all(pyfunc(*args) == cfunc(*args)))


if __name__ == '__main__':
    unittest.main()

