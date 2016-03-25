import os
import unittest
import zope.testrunner
from zope import component
from sparc.testing.fixture import test_suite_mixin
from sparc.apps.cache.testing import SPARC_CACHE_RUNTIME_LAYER

import time
import threading
from zope.component.eventtesting import getEvents, clearEvents
from sparc.apps.cache import ICompletedCachableSourcePoll

class SparcAppsCacheTestCase(unittest.TestCase):
    layer = SPARC_CACHE_RUNTIME_LAYER
    
    def tearDown(self):
        clearEvents()
    
    def _get_poller_config(self, cs_id, ca_id):
        """Return poller configuration matching given ids
        """
        cacher = self.layer.cacher
        pc = cacher.poller_configurations()
        for config in pc:
            if config['cacheablesource'].attrib['id'] == cs_id and \
                                    config['cachearea'].attrib['id'] == ca_id:
                return config
    
    def test_poller_configurations(self):
        cacher = self.layer.cacher
        pc = cacher.poller_configurations()
        self.assertEquals(len(pc), 6)
    
    def test_poll(self):
        cacher = self.layer.cacher
        config = self._get_poller_config('3', 'c') # poll time 0, should loop once
        config.update({'exit_': threading.Event()})
        
        # poll once
        t1 = threading.Thread(target=cacher.poll, kwargs=(config))
        t1.start()
        t1.join(.1)
        self.assertFalse(t1.is_alive())
        self.assertEquals(len(getEvents(
                            ICompletedCachableSourcePoll)), 1)
        
        # poll again
        t2 = threading.Thread(target=cacher.poll, kwargs=(config))
        t2.start()
        t2.join(.1)
        self.assertFalse(t2.is_alive())
        self.assertEquals(len(getEvents(
                            ICompletedCachableSourcePoll)), 2)



class test_suite(test_suite_mixin):
    package = 'sparc.apps.cache'
    module = 'cache'
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(SparcAppsCacheTestCase))
        return suite


if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])