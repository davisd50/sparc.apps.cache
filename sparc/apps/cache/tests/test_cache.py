import unittest
from sparc.testing.fixture import test_suite_mixin
from sparc.apps.cache.testing import SPARC_CACHE_INTEGRATION_LAYER


class test_suite(test_suite_mixin):
    package = 'sparc.apps.cache'
    module = 'cache'
    layer = SPARC_CACHE_INTEGRATION_LAYER


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')