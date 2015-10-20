"""Package logging facility

This module sets up a package-level logging object that should be referenced
by all children.  Children modules should create their own logging objects
based on natural Python namespacing (i.e. pwsecurity should be the
top-level logger for all sub-packages and modules).  This will allow for dynamic
logging and debugging capabilities.
    
Typical Usage:
    >>> import pwsecurity.log
    >>> import logging
    >>>
    >>> logger = logging.getLogger('pwsecurity.myModule')
    >>> logger.info("this will log a info-level module message")
    >>>
    >>> def myFunc():
    >>>     logger = logging.getLogger('pwsecurity.myModule.myFunc')
    >>>     logger.info("this will log a info-level function message")
    >>>
    >>> class myClass(object):
    ...     def __init__(self):
    ...         self.logger = logging.getLogger('pwsecurity.myModule.myClass') # can be replaced with __name__ inside your module/class
    ...
    ...     def myMethod(self):
    ...         self.logger.warning("this will log a warning-level class message")
    ...         self.logger.info("this will log a info-level class message")
    ...
    >>> myObject = myClass()
    >>> myObject.myMethod()
    XXX-XX-XX XX:XX:XX,XXX WARNING pwsecurity.myClass this will log a warning-level message
    >>> rootlogger.setLevel(logging.INFO)
    >>> myObject.myMethod()
    XXX-XX-XX XX:XX:XX,XXX WARNING pwsecurity.myClass this will log a warning-level message
    XXX-XX-XX XX:XX:XX,XXX INFO pwsecurity.myClass this will log a info-level message
    >>> rootlogger.setLevel(logging.WARNING)
    >>> myObject.myMethod()
    XXX-XX-XX XX:XX:XX,XXX WARNING pwsecurity.myClass this will log a warning-level message
    >>> myClassLogger = logging.getLogger('pwsecurity.myClass')
    >>> myClassLogger.setLevel(logging.INFO)
    >>> rootlogger.info("this will not show")
    >>> myObject.myMethod()
    XXX-XX-XX XX:XX:XX,XXX WARNING pwsecurity.myClass this will log a warning-level message
    XXX-XX-XX XX:XX:XX,XXX INFO pwsecurity.myClass this will log a info-level message
"""
import logging
import sys

rootlogger = logging.getLogger('gesecurity')
if rootlogger.level == logging.NOTSET:
    rootlogger.setLevel(logging.WARN)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'))
rootlogger.addHandler(handler)
