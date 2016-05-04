import argparse
import re
import sys

from zope.component import createObject
from zope.component import getMultiAdapter
from sparc.apps.cache.cache import cache
from sparc.cache import ICachableSource
from sparc.db.splunk import ISplunkSavedSearches
from sparc.db.splunk import ISplunkSavedSearchQueryFilter

from sparc.logging import logging
logger = logging.getLogger(__name__)

DESCRIPTION="""\
Cache application configuration tester.  This will enumerate and verify all
cachearea and cachablesource configuration elements.  This will initialize
each cache source and issue info level messages to STDOUT.  Debug messages
can be enable via a command line toggle.
"""

def getScriptArgumentParser(args=sys.argv):
    """Return ArgumentParser object
    
    Kwargs:
        args (list):        list of arguments that will be parsed.  The default
                            is the sys.argv list, and should be correct for most
                            use cases.
        components (list)   
    
    Returns:
        ArgumentParser object that can be used to validate and execute the
        current script invocation.
    """
    # Description
    parser = argparse.ArgumentParser(
            description=DESCRIPTION)
    # source
    parser.add_argument('config_file',
            help="Valid script configration file.  This should be the path to "\
                 "the script XML configuration file.  See config_sample.xml"\
                 "for detailed config specifications.")
    
    # --enumerate
    parser.add_argument('--enumerate',
            action='store_true',
            help="Enumerate and print discovered cachable items to stdout.")
    
    # --debug
    parser.add_argument('--debug',
            action='store_true',
            help="Echo debug messages to stdout.")
    
    return parser

class cache_test(object):

    def __init__(self, args):
        self.args = args
        self.args.verbose = True
        self.cache = cache(args) # inits the env, includes zca, loggers, etc...
    
    def cachesources(self):
        """Return iterable of Elemtree objects for each unique cachesource element in config"""
        _cs = []
        for pc in self.cache.poller_configurations():
            if pc['cacheablesource'] not in _cs:
                _cs.append(pc['cacheablesource'])
        return _cs
        
    def go(self):
        """Test the Cache configuration"""
        for cs in self.cachesources():
            logger.info(
                "Found config cacheablesource entry with id: %s and filter: %s" 
                                        % (cs.attrib['id'], 
                                           cs.attrib['filter']))
            cacheablesource = createObject(cs.attrib['factory'],  cs)
            if self.args.enumerate:
                for i in cacheablesource.items():
                    logger.info(
                        "Found cacheable item with id %s and attributes %s" %
                            (i.getId(), str(i.attributes)))

            

def main():
    args = getScriptArgumentParser().parse_args()
    rpr_test = cache_test(args)
    rpr_test.go()
    

if __name__ == '__main__':
    main()