from zope.component.factory import Factory
from zope.interface import implements
from interfaces import ICacheAreaPollers

class CacheAreaPollers(dict):
    implements(ICacheAreaPollers)
cacheAreaPollersFactory = Factory(CacheAreaPollers)