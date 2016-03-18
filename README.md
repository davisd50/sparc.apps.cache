#Introduction

A generic information to SQL DB caching utility.

##Usage

cache [-h] [--package PACKAGE] [--verbose] [--debug] source db_url

This application requires you to create one or more custom Python packages
that define and register the CSV <-> SQL mapping mechanisms.  See the
*Requirements* section below for an example.

CSV information cache update script. This will import CSV data into a
database. If the database is already populated, then only new entries and
updates will be imported. Please reference Pypi package documentation for
detailed usage information.

**positional arguments:**

<table>
 <tr>
  <td><strong>source</strong></td>
  <td>&nbsp;</td>
  <td>
    Valid CSV source. This should be a path to a CSV file, or a directory 
    that contains CSV files. CSV data sourcesthat are found to have a 
    matching registered sparc.cache.interfaces.ICachedItemMapper interface 
    will import updates to SQL cache area identified by db_url
  </td>
 </tr>
 <tr>
  <td><strong>db_url</strong></td>
  <td>&nbsp;</td>
  <td>
  Valid database url to use for connection (see 
  http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html) for detailed 
  specifications for url. Short-hand definition is
  dialect+driver://user:password@host/dbname[?key=value..].
  <td>
 </tr>
</table>

**optional arguments:**

<table>
 <tr>
  <td><strong>--module MODULE</strong></td>
  <td>&nbsp;</td>
  <td>
    Python package.module to import Python-based configuration from. See 
    deatailed package documentation (README.md) for how to create and 
    registered the required components. This should be the full 
    package.module name.
  </td>
 </tr>
 <tr>
  <td><strong>--package PACKAGE</strong></td>
  <td>&nbsp;</td>
  <td>
    Python package to configure for processing. There should be a valid 
    configure.zcml file within the package that configures the required 
    caching factories and mapping subscribers. Thisoption can be issued 
    multiple times.
  </td>
 </tr>
</table>

**sample invocations**

The samples assume you've create the *mypackage* Python package containing the
*mymodule* Python module referenced below.

    Cache mycsvfile.csv information into a SQLite DB based on 
    mypackage.mymodule schema.

    $ ~# cache --module mypackage.mymodule mycsvfile.csv sqlite:////tmp/cache.db

##Capabilities

This utility allows the caching of CSV file information into a SQL database
with appropriate data type assignment (i.e. text vs. date vs integer vs ...).

##Features

 - Can import a named CSV file, or a directory of CSV files into a SQL DB
 - Utilizes SQLAlchemy, allowing command line identified DB type selection
 - Cached data can be imported with appropriate named SQL data types

##Requirements

This application can be used either as an installed Python package (i.e.
pip install ...), or as a platform-specific standalone binary called
*cache*.  But on it's own, the application will not do anything useful.  
*You* must create some implementation specific python code to augment this
application to perform the appropriate data caching.

One key note before we discuss the Python requirement, is the CSV source data
*must* contain a primary key field (i.e. a field guranteed to be unique among
all rows).

###Python Requirement: Cachable Item factory
You'll need to provide this for the sole purpose of identifying which CSV field
is considered the primary key.  In the following example, the 'id' field is
the primary key.

    mypackage.mymodule
    >>> from zope.component.factory import Factory
    >>> from sparc.cache.item import cachableItemMixin
    >>> class myItem(cachableItemMixin):
    >>>     def __init__(self, attributes=None):
    >>>         super(myItem, self).__init__('id', attributes)
    >>> myCachableItemFactory = Factory(myItem, 'myCachableItemFactory')

The above code should work for most use-cases, where you would simply change
the *id* entries to what-ever CSV field contains the primary key.

For advanced usage, please reference the sparc.cache.interfaces.ICachableItem
interface definition and the sparc.cache documentation on how to create a 
factory for ICachableItem items.

###Python Requirement: Cached Item factory
This component will provide the SQL schema information that will be used to 
create and store the equivilant CSV entries in the SQL DB.  Most use-cases 
can leverage the pre-baked mixin class cachedItemMixin to minimize code to lines
that are specific to the implementation at hand.

    mypackage.mymodule
    >>> from sparc.cache.item import cachedItemMixin
    >>> from zope.component import getUtility
    >>> from sparc.db.sql.sa import ISqlAlchemyDeclarativeBase
    >>> from sparc.db.sql.sa import sparcBaseMixin
    >>> Base = getUtility(ISqlAlchemyDeclarativeBase)
    >>> class myCachedItem(cachedItemMixin, sparcBaseMixin, Base):
    >>>     _key = 'id'
    >>>     id = sqlalchemy.Column(sqlalchemy.VARCHAR(), primary_key=True)
    >>>     time = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    >>>     user_ip = sqlalchemy.Column(sqlalchemy.VARCHAR(), nullable=True)
    >>>     username = sqlalchemy.Column(sqlalchemy.VARCHAR(), nullable=True)
    >>> myCachedItemFactory = Factory(myCachedItem, 'myCachedItemFactory')

The above code should work for most use cases where the *_key* identifies which
attribute should be considered the primary key in the DB table and the other
attributes indicate the DB table column schemas.

For advacned usage, please reference sparc.cache.interfaces.ICachedItem
interface, sparc.cache documentation, and sparc.cache.sql.

###Python Requirement: Mapper for CSV fields to SQL columns
This component maps CSV field names to SQL column names.  Once again, we'll use
a mixin class to insure our custom code requirements are minimal.  For the most
part, we'll provide a Python dictionary whose keys reference the CSV field
names and values reference the associated SQL column names.

One note, notice the *normalizedDateTime()* reference below.  This is a class
that implements IManagedCachedItemMapperAttributeKeyWrapper (see 
sparc.cache.interfaces) allowing Python based data magling before SQL
storage.  Allow this is an advanced topic, it can be usefull in many
circumstances where CSV data is not well-strucutred (for example: dates where
a date string can take many different formats). 

    mypackage.mymodule
    >>> from sparc.cache.sql import SqlObjectMapperMixin
    >>> from sparc.cache.sources.normalized_datetime import normalizedDateTime
    >>> class myItemCacheMapper(SqlObjectMapperMixin):
    >>>     mapper = {
    >>>               'id'       :'id', 
    >>>               'time'     : normalizedDateTime('time'),
    >>>               'user_ip'  : 'user_ip',
    >>>               'username' : 'username'
    >>>               }
    
###Python Requirement: Component registration
Registration is what allows the caching application to lookup and
leverage the custom components created above.  We'll need to register our 
2 factories for ICachableItem and ICachedItem, and also a subscriber for the
ICachedItemMapper implementation.

    mypackage.mymodule
    >>> from zope.component import getSiteManager
    >>> from zope.component.interfaces import IFactory
    >>> from sparc.cache import ICachedItemMapper, ICachableSource
    >>> sm = getSiteManager()
    >>> sm.registerUtility(mypackage.mymodule.myCachableItemFactory, IFactory, u'mypackage.mymodule.myCachableItemFactory')
    >>> sm.registerUtility(mypackage.mymodule.myCachedItemFactory, IFactory, u'mypackage.mymodule.myCachedItemFactory')
    >>> sm.registerSubscriptionAdapter(myItemCacheMapper, (ICachableSource, IFactory,), ICachedItemMapper)

Components may also be registered via ZCML in combination with the --package
launch parameter.  In this case, you would need to have a properly formated
configure.zcml file which defines the above components.