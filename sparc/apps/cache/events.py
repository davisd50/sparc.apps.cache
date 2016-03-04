from zope.interface import implements
from zope.interface.interfaces import ObjectEvent
from interfaces import ICacheAreaPollersAboutToStartEvent

class CacheAreaPollersAboutToStartEvent(ObjectEvent):
    implements(ICacheAreaPollersAboutToStartEvent)