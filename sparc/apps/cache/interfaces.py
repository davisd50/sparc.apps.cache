from zope.interface import Interface
from zope.interface.interfaces import IObjectEvent

class ICacheAreaPollersAboutToStartEvent(IObjectEvent):
    """An ICacheAreaPollers is about to begin polling"""

class ICompletedCachableSourcePoll(IObjectEvent):
    """An ICachableSource has been polled"""

class ICacheAreaPollers(Interface):
    """A dict based data structure for cache area pollers
    
    {ICacheArea:{ICacheableSource:poll_time_int}}
    
    """