from zope.interface import Interface
from zope.interface.interfaces import IObjectEvent

class ICachableSourcePollersAboutToStartEvent(IObjectEvent):
    """An ICachableSourcePollerConfigurations is about to begin polling"""

class ICompletedCachableSourcePoll(IObjectEvent):
    """An ICachableSource has been polled"""

class ICachableSourcePollerConfigurations(Interface):
    """A sequence based data structure for ICachableSource poller configurations
    
    [{'cachablesource': cachablesource_element, 'cachearea': cachearea_element}]
    """