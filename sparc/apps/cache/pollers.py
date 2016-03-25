from zope.component.factory import Factory
from zope.interface import implements
from interfaces import ICachableSourcePollerConfigurations

class CachableSourcePollerConfigurations(list):
    implements(ICachableSourcePollerConfigurations)
cacheAreaPollersFactory = Factory(CachableSourcePollerConfigurations)