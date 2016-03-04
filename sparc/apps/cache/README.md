# CACHER
---

Configurable information collector and processor.  Hookable system that allows
runtime configuration of data pollers and cache areas.  In the most simple
sense, this will collect cachable information from the configured sources
and store that informaton into the configured cache areas.  Please see
README for detailed information on how to create and configure this 
system.

*Cacher* is capable of collecting a runtime-configurable set of information
into one or more runtime-configurable data storage areas (such as a 
SQL database) on a runtime-configurable polling schedule.

Some example use-cases:

 - Monitor a log file for changes and update new log entries into a backend SQL 
   database.
 - Periodically query a 3rd party API for a set of data and update a backend
   no-SQL database with new and changed datasets.  Also perform some set
   of operations when new/updated data is found.

##Installation
*Cacher* can be installed via *pip* or *easy_install*

`pip install reaper`

###Configuration
*Cacher* must be configured in order to do anything usefull.  A configuration
file must be supplier to the *Cacher* at lunch time.  Among other things,
the configuration file must specifiy at least one cache area and at least
one cache source.  If your confused about what a cache area/source is, see
the *Cache* section below.  You can take a look at the 
[sample configuration file](https://stash.cs.sys/projects/PSO/repos/penny.reaper/browse/penny/reaper/config_sample.xml?at=refs%2Fheads%2Fdevelop)
to understand the required format.

>You may add your own custom entries into the *Cacher* configuration file.
>These can be additional attributes in the standard tags, or new tags that
>you create.  The configuration will be exposed to the application vi a
>registered utility that provides
>[sparc.configuration.xml.IAppElementTreeConfig](https://github.com/davisd50/sparc.configuration/blob/develop/sparc/configuration/xml/interfaces.py).
>This allows your cachesource and cachearea factories to derive run-time
>configurations such as url, username, password, etc durring their object
>generation calls.

###Daemon
It is typical for *Cacher* to run as a system daemon.  It is recomended to 
leverage a tool such as *supervisord* (example below) to manage the daemon
process.  Our example assumes the use of the system-wide python environment
and that a valid *Cacher* configuration file is located at */etc/reaper.conf*

##Cache
The heart of *Cacher* is the information caching system.  The caching system
is directly based on the APIs from 
[sparc.cache](https://github.com/davisd50/sparc.cache), which in turn is part
of [sparc](https://github.com/davisd50/sparc).  Sparc uses the 
[Zope Toolkit](http://docs.zope.org/zopetoolkit/) and a component registry
as the mechanism to allow a highly configurable and hookable system to 
cache and process information.

###Cachable Source
*Cacher* requires one or more sources whose data can be cached.  These are 
specified in the *Cacher* configuration file via a ZCA factory name.  A 
cachable source provides 
[sparc.cache.ICachableSource](https://github.com/davisd50/sparc.cache/blob/master/sparc/cache/interfaces.py).
It can be a complex process to create a cachable source, but 
[this](https://github.com/davisd50/sparc.cache/) shows a SQL-based example
on how to do it.

Once a cachable source implementation has been created, it will be exposed to
*Cacher* via a named factory in the *Cacher* configuration file.  Often, the
cachable source will have a required set of parameters needed to access the
source information (i.e. link, username, password, etc.).  It is recommended
to add these parameters as attributes into the given *cachablesource* node
that names the factory.  Each factory will be called exactly one time.

Cachable sources will be polled based on the polling period specified in the
*Cacher* configuration file.

###Cache Area
*Cacher* requires one or more areas where data is cached.  These are 
specified in the *Cacher* configuration file via a ZCA factory name. A cache 
area is a  storage facility (such as a database) that can be used to cache 
information  elements into.  In terms of ZCA, a cache area is a component 
that provides
[sparc.cache.ICacheArea](https://github.com/davisd50/sparc.cache/blob/master/sparc/cache/interfaces.py).
Creation of cache areas can be complex, but 
[this](https://github.com/davisd50/sparc.cache/) shows a SQL-based example
on how to do it.  Each factory will be called exactly one time.