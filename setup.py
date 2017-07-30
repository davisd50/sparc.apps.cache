from setuptools import setup, find_packages
import os

version = '0.5.0'

setup(name='sparc.apps.cache',
      version=version,
      description="Configurable information collector and processor",
      long_description=open("README.md").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
      ],
      keywords=['zca'],
      author='David Davis',
      author_email='davisd50@gmail.com',
      url='https://github.com/davisd50/sparc.apps.cache',
      download_url = '',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sparc', 'sparc.apps'],
      include_package_data=True,
      package_data = {
          '': ['*.zcml']
        },
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.component',
          'zope.interface',
          'zope.event',
          'sparc.asset',
          'sparc.aws',
          'sparc.box',
          'sparc.cache',
          'sparc.common',
          'sparc.configuration',
          'sparc.db',
          'sparc.entity',
          'sparc.event',
          'sparc.i18n',
          'sparc.logging',
          'sparc.login',
          'sparc.publish',
          'sparc.testing',
          'sparc.utils'
          # -*- Extra requirements: -*-
      ],
      tests_require=[
          'sparc.testing'
      ],
      entry_points={
          'console_scripts':['cacher=sparc.apps.cache.cache:main',
                             'cacher_test=sparc.apps.cache.testing.cache_test:main'],
          },
      )
