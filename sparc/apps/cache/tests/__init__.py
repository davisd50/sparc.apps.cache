"""
In order to properly test the Cache application, we need to create some
cachable sources and cachable areas.  The implementations here are simply
for basic testing purposes only...don't model any real-world implementations
on these mock-ups.
"""

from zope.component.factory import Factory
from zope.component.interfaces import IFactory
from zope.interface import implements
from sparc.cache import ICachableItem
from sparc.cache import ICachableSource
from sparc.cache import ICacheArea

class CachableSourceMixin(object):
    def __init__(self, *args, **kwargs):
        pass
    def items(self):
        return []

class CachableSource1(CachableSourceMixin):
    implements(ICachableSource)
cachableSource1Factory = Factory(CachableSource1)

class CachableSource2(CachableSourceMixin):
    implements(ICachableSource)
cachableSource2Factory = Factory(CachableSource2)

class CachableSource3(CachableSourceMixin):
    implements(ICachableSource)
cachableSource3Factory = Factory(CachableSource3)

class CacheAreasMixin(object):
    count = 0
    def __init__(self, *args, **kwargs):
        pass
    def import_source(self, source):
        self.count += 1
        return 0
    def initialize(self):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass

class CacheArea1(CacheAreasMixin):
    implements(ICacheArea)
cacheArea1Factory = Factory(CacheArea1)

class CacheArea2(CacheAreasMixin):
    implements(ICacheArea)
cacheArea2Factory = Factory(CacheArea2)

class CacheArea3(CacheAreasMixin):
    implements(ICacheArea)
cacheArea3Factory = Factory(CacheArea3)
