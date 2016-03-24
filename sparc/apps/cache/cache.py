import argparse
from importlib import import_module
import sys
import time
import threading
from xml.etree import ElementTree
from zope.component import createObject
from zope.component import getSiteManager
from zope.component import getUtility
import zope.component.event #needed in order to initialize the event notification environment
import zope.configuration.xmlconfig
from zope.event import notify
from zope.interface import alsoProvides

from sparc.cache import ITransactionalCacheArea
from sparc.configuration.zcml import Configure
from sparc.configuration.xml import IAppElementTreeConfig
import sparc.configuration
import sparc.cache

import sparc.apps.cache
from events import CacheAreaPollersAboutToStartEvent
from events import CompletedCachableSourcePoll

from sparc.logging import logging
logger = logging.getLogger(__name__)

DESCRIPTION="""\
Configurable information collector and processor.  Hookable system that allows
runtime configuration of data pollers and cache areas.  In the most simple
sense, this will collect cachable information from the configured sources
and store that informaton into the configured cache areas.  Please see
README for detailed information on how to configure and run this system. 
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
    
    # --verbose
    parser.add_argument('--verbose',
            action='store_true',
            help="Echo verbose messages to stdout.")
    
    # --verbose
    parser.add_argument('--debug',
            action='store_true',
            help="Echo debug messages to stdout.")
    
    return parser

class cache(object):

    def __init__(self, args):
        self.setLoggers(args)
        self._configure_zca(args.config_file)
        logger.debug("Component registry initialized")

    def config_get_all_sources_with_polls(self):
        """Return all source configs as [(factory_name, poll, element)].
        """
        config = getUtility(IAppElementTreeConfig)
        sources = []
        for cs_element in config.findall('cacheablesource'):
            _factory_name = cs_element.attrib['factory']
            _poll = abs(int(cs_element.attrib['poll'] if \
                                        'poll' in cs_element.attrib else 0))
            sources.append((_factory_name, _poll, cs_element,))
        return sources

    def create_polled_sources_for_cache(self, factory_name):
        """Return dictionary {ICacheableSource:poll} of sources and polls for
        cachearea with factory_name
        """
        config = getUtility(IAppElementTreeConfig)
        cachearea_xml = config.find(
                    ".//cachearea[@factory='{}']".format(factory_name) )
        
        polled_sources = {}
        for sf_name, poll, cs_element in \
                        self.config_get_all_sources_with_polls():
            if 'sources' not in cachearea_xml.attrib or \
                                not cachearea_xml.attrib['sources'].split():
                polled_sources[createObject(sf_name, cs_element)] = poll
            elif sf_name in cachearea_xml.attrib['sources'].split():
                polled_sources[createObject(sf_name, cs_element)] = poll
            
            logger.info('Configured polling source factory %s with poll ' +\
                                        'time %d and for cachearea factory %s',
                                            sf_name,
                                            poll,
                                            factory_name)
        return polled_sources        
    
    def create_pollers(self):
        """Return configured pollers as a Python dictionary
        
        pollers: {ICacheArea:{ICacheableSource:poll}} <-- unique thread created based on Area + Source
        """
        pollers = createObject(u'sparc.apps.cache.pollers')
        config = getUtility(IAppElementTreeConfig)
        for cachearea_xml in config.findall('cachearea'):
            pollers[createObject(cachearea_xml.attrib['factory'],
                                 element=cachearea_xml
                                 )] = \
                self.create_polled_sources_for_cache(
                                            cachearea_xml.attrib['factory'])
        
        return pollers

    def setLoggers(self, args):
        logger = logging.getLogger() # root logger
        if args.verbose:
            logger.setLevel('INFO')
        if args.debug:
            logger.setLevel('DEBUG')
        
    
    def _configure_zca(self, cache_config):
        """We need a 3 step process to make sure dependencies are met
        1. load static package-based ZCML files....standard stuff here.
        2. Register the config into the registry (i.e. make it available for
           lookup)
        3. Manually register zcml entries in the config (these entries 
           may be dependent on having the config available for lookup)
        """
        # step 1
        packages = [sparc.apps.cache]
        Configure(packages)
        #step 2
        config = ElementTree.parse(cache_config).getroot()
        alsoProvides(config, IAppElementTreeConfig)
        sm = getSiteManager()
        sm.registerUtility(config, IAppElementTreeConfig)
        #step3
        for zcml in config.findall('zcml'):
            zcml_file, package = 'configure.zcml' \
                        if 'file' not in zcml.attrib else zcml.attrib['file'],\
                            import_module(zcml.attrib['package'])
            zope.configuration.xmlconfig.XMLConfig(zcml_file, package)()

    def poll(self, area, source, delta, exit_ = None):
        while True:
            try:
                new = area.import_source(source)
                if ITransactionalCacheArea.providedBy(area):
                    area.commit()
                logger.info("Found %d new items in cachable source", new)
                notify(CompletedCachableSourcePoll(source))
            except Exception as e:
                if ITransactionalCacheArea.providedBy(area):
                    area.rollback()
                logger.exception("Error importing cachable items into cache area")
            if not delta:
                return
            for i in xrange(delta):
                if exit_.is_set():
                    return
                time.sleep(1)
    
    def go(self, pollers):
        """Create threaded pollers and start configured polling cycles
        """
        try:
            notify(CacheAreaPollersAboutToStartEvent(pollers))
            logger.info("Starting pollers")
            exit_ = threading.Event()
            for area, poller in pollers.iteritems(): # {ICacheArea:{ICacheableSource:poll}}
                area.initialize()
                for source, poll in poller.iteritems():
                    threading.Thread(target=self.poll, 
                                        args=(area, source, poll,exit_), 
                                    ).start()
            while threading.active_count() > 1:
                time.sleep(.001)
        except KeyboardInterrupt:
            logger.info("Exiting application.")
            exit_.set()
    

def main():
    args = getScriptArgumentParser().parse_args()
    r = cache(args)
    r.go(r.create_pollers())

if __name__ == '__main__':
    main()