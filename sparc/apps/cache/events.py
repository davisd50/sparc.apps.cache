from zope.interface import implements
from zope.interface.interfaces import ObjectEvent
from interfaces import ICacheAreaPollersAboutToStartEvent
from interfaces import ICompletedCachableSourcePoll

class CacheAreaPollersAboutToStartEvent(ObjectEvent):
    implements(ICacheAreaPollersAboutToStartEvent)

class CompletedCachableSourcePoll(ObjectEvent):
    implements(ICompletedCachableSourcePoll)