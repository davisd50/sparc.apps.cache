from importlib import import_module
import argparse, sys, os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from zope.interface import alsoProvides
from zope.component import createObject, getMultiAdapter, getFactoriesFor, subscribers

from sparc.cache.interfaces import ICachableItem, ICachedItemMapper, ICacheArea, ICachedItem
from sparc.cache.sql import ICachedItemMapperSqlCompatible
from sparc.db import ISqlAlchemySession

from sparc.apps.cache.configure import Configure
from sparc.db import Base

import log
import sparc.common.log
import logging
logger = logging.getLogger('sparc.apps.cache')

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
            description='CSV information cache update script.  This will '\
                        'import CSV data into a database.  If the database is '\
                        'already populated, then only new entries and updates '\
                        'will be imported.  Please reference Pypi package '\
                        'documentation for detailed usage information.',
            epilog="This script will exit with a non-zero status on failure, otherwise zero."+os.linesep+\
                        "Windows invocation: cache.exe C:\\my\\csv\\dir sqlite:///C:\\tmp\\cache.db"+os.linesep+\
                        "Unix invocation   : cache /path/to/my/csv sqlite:////tmp/cache.db")
    # configuration
    parser.add_argument('--package',
            action='append',
            help="Python package to configure for processing.  There should be "\
                 "a valid configure.zcml file within the package that configures "\
                 "the required caching factories and mapping subscribers.  This"\
                 "option can be issued multiple times.")
    # configuration
    parser.add_argument('--module',
            action='append',
            help="Python package.module to import Python-based configuration from. "\
                 "See deatailed package documentation (README.md) for how "\
                 "to create and registered the required components. This should "\
                 "be the full package.module name.")
    # source
    parser.add_argument('source',
            help="Valid CSV source.  This should be a path to a CSV file, or a "\
                 "directory that contains CSV files.  CSV data sources that are "\
                 "found to have a matching registered "\
                 "sparc.cache.interfaces.ICachedItemMapper interface will import "\
                 "updates to SQL cache area identified by db_url")
    # db_url
    parser.add_argument('db_url',
            help="Valid database url to use for connection  (see "\
                 "http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html) for "\
                 "detailed specifications for url.  Short-hand definition is "\
                 "dialect+driver://user:password@host/dbname[?key=value..].")

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
        self.args = args
        self._source_files = list()
        self._source_map_info = list() # list of tuples (source, factory, map)
        self.setLoggers()
        packages = args.package
        if not packages:
            packages = []
        Configure([import_module(name) for name in packages]) # <-- set up ZCA with ZCML
        if args.module:
            for package_module in args.module:
                import_module(package_module) # <-- Python-based ZCA configuration
        self.connectDb()
        self.validateSources()

    def setLoggers(self):
        self._loggers = {
                         'sparc.cache.sql': logging.getLogger('sparc.cache.sql'),
                         'sparc.cache.item': logging.getLogger('sparc.cache.item'),
                         'sparc.cache.sources.normalized_datetime': logging.getLogger('sparc.cache.sources.normalized_datetime'),
                         'sparc.common.configure': logging.getLogger('sparc.common.configure')
                         }
        for name, logger in self._loggers.items():
            if self.args.verbose:
                logger.setLevel('INFO')
            if self.args.debug:
                logger.setLevel('DEBUG')

    def connectDb(self):
        engine = create_engine(self.args.db_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        alsoProvides(self.session, ISqlAlchemySession) # this will make sure the multi-adapter lookup will function

    def _findItemFactories(self):
        _cachableItemFactories = list()
        for name, factory in getFactoriesFor(ICachableItem):
            _cachableItemFactories.append((name, factory),)
        if not _cachableItemFactories:
            logger.error("Unable to find any registered ZCA utility factories "\
                        "that generate objects that implement "\
                        "sparc.cache.interfaces.ICachableItem.  Unable to cache "\
                        "any of the sources.")
        return _cachableItemFactories

    def validateSources(self):
        """
         - loop through all potential source files
           - find CSV sources via cache.sources.CSVSourceFactory (valid sources return entries on first() calls)
             - find an appropriate mapper, loop all mappers (need to relate mapper to CSVsource)
        """
        self._source_files = list()
        self._import = list()

        if os.path.isfile(self.args.source):
            self._source_files.append(self.args.source)
        else:
            self._source_files = [os.path.join(self.args.source, f) for f in os.listdir(self.args.source) if os.path.isfile(os.path.join(self.args.source, f))]

        for source in self._source_files:
            logger.debug("found file, attempting to validate and process: %s", str(source))
            if '\0' in open(source,'rb').read(1024 * 10): # read 10MB and look for NUL byte
                logger.debug("file contains NUL byte, skip parsing: %s", str(source))
                continue
            _validated_file = False
            try:
                for fname, factory in self._findItemFactories():
                    csvsource = createObject('cache.sources.CSVSourceFactory', source, factory)
                    item = csvsource.first()
                    if not item:
                        logger.debug("Item factory test failed for %s", str(fname))
                        continue
                    logger.info("found potential CSV item source file, now will try to find a matching mapper: %s", str(source))

                    for sfacName, sFactory in getFactoriesFor(ICachedItem):
                        for mapper in subscribers((csvsource,sFactory,), ICachedItemMapper):
                            logger.debug("testing mapper/cachedItem combination: %s, %s", str(mapper), str(sfacName))
                            if not ICachedItemMapperSqlCompatible.providedBy(mapper): # filter out non-SQL-based mappers
                                logger.debug("skipping ICachedItemMapper %s because it does not also provide required interface ICachedItemMapperSqlCompatible", str(mapper))
                                continue
                            if not mapper.check(item):
                                logger.info("skipping CachedItemMapper %s because item failed mapper validation check", str(mapper))
                                continue
                            _validated_file = True
                            logger.info("found valid ICachedItemMapper %s", str(mapper))
                            self._import.append((mapper, csvsource))
                            raise StopIteration
            except StopIteration:
                pass
            if not _validated_file:
                logger.warn("unable to find valid CSV entries in source: %s", str(source))

    def go(self):
        _total = 0
        for map, csvsource in self._import:
            sqlObjectCacheArea = getMultiAdapter((self.session, map), ICacheArea)
            sqlObjectCacheArea.initialize(Base)
            c = sqlObjectCacheArea.import_source(csvsource)
            _total += c
            logger.debug("Updated %s cache entries from CSV source file: %s", str(c), str(csvsource.source))
        self.session.commit()
        logger.info("Updated %s cache entries from CSV source file(s): %s", str(_total), str(self.args.source))
        return _total

def main():
    args = getScriptArgumentParser().parse_args()
    rows = cache(args).go()
    print 'Successfully updated %s rows in the cache'%(rows)

if __name__ == '__main__':
    main()
