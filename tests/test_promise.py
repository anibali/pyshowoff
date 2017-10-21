import unittest

from pyshowoff.promise import Promise


class TestPromise(unittest.TestCase):
    def test_all(self):
        promises = [Promise.resolve(i) for i in range(5)]
        result = Promise.all(promises).result(1)
        self.assertEqual(result, list(range(5)))

    def test_all_with_exception(self):
        promises = [Promise.reject(ZeroDivisionError()) if i == 2 else Promise.resolve(i)
                    for i in range(5)]
        def get_result():
            Promise.all(promises).result(1)
        self.assertRaises(ZeroDivisionError, get_result)

    def test_race(self):
        promises = [Promise.resolve(i) if i == 2 else Promise() for i in range(5)]
        result = Promise.race(promises).result(1)
        self.assertEqual(result, 2)

    def test_race_with_exception(self):
        promises = [Promise.reject(ZeroDivisionError()) if i == 2 else Promise() for i in range(5)]
        def get_result():
            Promise.all(promises).result(1)
        self.assertRaises(ZeroDivisionError, get_result)
