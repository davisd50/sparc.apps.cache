from zope.component.testlayer import ZCMLFileLayer
from zope.component.testlayer import ZCMLLayerBase
import sparc.apps.cache
from sparc.configuration.zcml.configure import configure_vocabulary_registry


import os
import sparc.apps.cache.tests
from zope import component
from sparc.apps.cache.cache import cache as CacheApp
from sparc.apps.cache.cache import getScriptArgumentParser

class SparcCacheLayer(ZCMLFileLayer):
    def setUp(self):
        super(SparcCacheLayer, self).setUp()
        configure_vocabulary_registry()
    def tearDown(self):
        super(SparcCacheLayer, self).tearDown()

SPARC_CACHE_INTEGRATION_LAYER = SparcCacheLayer(sparc.apps.cache,
                                                zcml_file="configure.zcml")

class SparcCacheRuntimeLayer(ZCMLLayerBase):
    def setUp(self):
        super(SparcCacheRuntimeLayer, self).setUp()
        configure_vocabulary_registry()
        parser = getScriptArgumentParser()
        args = parser.parse_args([
                                  os.path.join(os.path.dirname(
                                            sparc.apps.cache.tests.__file__), 
                                                           'config_test.xml')])
        self.cacher = CacheApp(args)
        self.sm = component.getSiteManager()
        
    def tearDown(self):
        super(SparcCacheRuntimeLayer, self).tearDown()
        
    def _load_zcml(self, context):
        pass # nothing to do

SPARC_CACHE_RUNTIME_LAYER = SparcCacheRuntimeLayer(sparc.apps.cache)