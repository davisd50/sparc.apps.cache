import unittest
from doctest import DocTestSuite
from doctest import DocFileSuite

import sparc.apps.cache

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('cache.txt',
                     package=sparc.apps.cache),))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')