from zope.interface import implements
from zope.interface.interfaces import ObjectEvent
from interfaces import ICachableSourcePollersAboutToStartEvent
from interfaces import ICompletedCachableSourcePoll

class CachableSourcePollersAboutToStartEvent(ObjectEvent):
    implements(ICachableSourcePollersAboutToStartEvent)

class CompletedCachableSourcePoll(ObjectEvent):
    implements(ICompletedCachableSourcePoll)