from zope.component.testlayer import ZCMLFileLayer
import sparc.apps.cache
from sparc.configuration.zcml.configure import configure_vocabulary_registry

class SparcCacheLayer(ZCMLFileLayer):
    def setUp(self):
        super(SparcCacheLayer, self).setUp()
        configure_vocabulary_registry()
    def tearDown(self):
        super(SparcCacheLayer, self).tearDown()

SPARC_CACHE_INTEGRATION_LAYER = SparcCacheLayer(sparc.apps.cache,
                                                zcml_file="configure.zcml")