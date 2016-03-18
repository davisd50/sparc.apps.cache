from zope.component.testlayer import ZCMLLayerBase
import sparc.apps.cache
from sparc.configuration.zcml.configure import configure_vocabulary_registry

class SparcCacheLayer(ZCMLLayerBase):
    def setUp(self):
        super(SparcCacheLayer, self).setUp()
        configure_vocabulary_registry()
    def tearDown(self):
        super(SparcCacheLayer, self).tearDown()
    
    def _load_zcml(self, context):
        pass # app is responsible to do this

SPARC_CACHE_INTEGRATION_LAYER = SparcCacheLayer(sparc.apps.cache)