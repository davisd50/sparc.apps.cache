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
from sparc.configuration.zcml.configure import configure_vocabulary_registry
from sparc.configuration.xml import IAppElementTreeConfig
import sparc.configuration
import sparc.cache

import sparc.apps.cache
from events import CachableSourcePollersAboutToStartEvent
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

    @classmethod
    def configure_zca(cls, cache_config):
        """Configure runtime Zope Component Architecture registry
        
        We need a 3 step process to make sure dependencies are met
        1. load static package-based ZCML files....standard stuff here.
        2. Register the config into the registry (i.e. make it available for
           lookup)
        3. Manually register zcml entries in the config (these entries 
           may be dependent on having the config available for lookup)
           
        Args:
            cache_config: application configuration file name or file object
        """
        # step 1
        packages = [sparc.apps.cache]
        Configure(packages)
        configure_vocabulary_registry()
        #step 2
        config = ElementTree.parse(cache_config).getroot()
        for zcml in config.findall('zcml'):
            zcml_file, package = 'configure.zcml' \
                        if 'file' not in zcml.attrib else zcml.attrib['file'],\
                            import_module(zcml.attrib['package'])
            zope.configuration.xmlconfig.XMLConfig(zcml_file, package)()
        #step3
        alsoProvides(config, IAppElementTreeConfig)
        sm = getSiteManager()
        sm.registerUtility(config, IAppElementTreeConfig)
        return config

    def __init__(self, args):
        self.setLoggers(args)
        self.config = self.configure_zca(args.config_file)
        logger.debug("Component registry initialized, application configuration registered")

    def setLoggers(self, args):
        logger = logging.getLogger() # root logger
        if args.verbose:
            logger.setLevel('INFO')
        if args.debug:
            logger.setLevel('DEBUG')
    
    def poller_configurations(self):
        """Returns sequence of poller configurations
        
        sequence entry data structure:
            {
             'cacheablesource': cacheablesource_element, 
             'cachearea': cachearea_element
             }
        
        Returns: sequence of data structure for all poller configurations
        """
        configs = []
        for cacheablesource in self.config.findall('cacheablesource'):
            for cachearea in self.config.findall('cachearea'):
                if 'sources' not in cachearea.attrib:
                    configs.append({'cacheablesource': cacheablesource, 
                           'cachearea': cachearea})
                elif cacheablesource.attrib['id'] in \
                                        cachearea.attrib['sources'].split():
                    configs.append({'cacheablesource': cacheablesource, 
                           'cachearea': cachearea})
        return configs

    
    def create_poller(self, **kwargs):
        """Returns poller data structure
        
        Kwargs:
            cacheablesource: Elemtree.element object of cacheablesource
            cachearea: Elemtree.element object of cachearea
        
        Returns: (ICachableSource, ICacheArea, poll)
        """
        cacheablesource = \
            createObject(kwargs['cacheablesource'].attrib['factory'], 
                         kwargs['cacheablesource'])
        cachearea = \
            createObject(kwargs['cachearea'].attrib['factory'], 
                         kwargs['cachearea'])
        poll = abs(int(kwargs['cacheablesource'].attrib['poll']))
        logger.info("Poller create for cacheablesource id %s and cachearea id %s" \
                        % (kwargs['cacheablesource'].attrib['id'], \
                          kwargs['cachearea'].attrib['id'])
                        )
        return (cacheablesource, cachearea, poll)

    def poll(self, **kwargs):
        """Continously poll a cachablesource/cachearea combination
        
        Kwargs:
            cacheablesource: Elemtree.element object of cacheablesource
            cachearea: Elemtree.element object of cachearea
            exit_: threading.Event listener for app exit call message
        """
        source, area, delta = self.create_poller(**kwargs)
        area.initialize()
        while True:
            try:
                new = area.import_source(source)
                if ITransactionalCacheArea.providedBy(area):
                    area.commit()
                logger.info("Found %d new items in cachablesource %s" % \
                                (new, kwargs['cacheablesource'].attrib['id']))
                notify(CompletedCachableSourcePoll(source))
            except Exception:
                if ITransactionalCacheArea.providedBy(area):
                    area.rollback()
                logger.exception("Error importing cachable items into cache area")
            if not delta:
                return
            for i in xrange(delta):
                if kwargs['exit_'].is_set():
                    return
                time.sleep(1)

    def go(self, poller_configurations):
        """Create threaded pollers and start configured polling cycles
        """
        try:
            notify(
                CachableSourcePollersAboutToStartEvent(poller_configurations))
            logger.info("Starting pollers")
            exit_ = threading.Event()
            for config in poller_configurations: # config is a dict
                kwargs = {'exit_': exit_}
                kwargs.update(config)
                threading.Thread(target=self.poll, 
                                        kwargs=(kwargs), 
                                    ).start()
            while threading.active_count() > 1:
                time.sleep(.001)
        except KeyboardInterrupt:
            logger.info("Exiting application.")
            exit_.set()
    

def main():
    args = getScriptArgumentParser().parse_args()
    r = cache(args)
    r.go(r.poller_configurations())

if __name__ == '__main__':
    main()