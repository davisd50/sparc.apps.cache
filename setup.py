from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='sparc.apps.cache',
      version=version,
      description="",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://github.com/davisd50/sparc.apps.cache',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sparc', 'sparc.apps'],
      include_package_data=True,
      package_data = {
          '': ['*.zcml']
        },
      zip_safe=False,
      install_requires=[
          'setuptools',
          'argparse',
          'pyinstaller',
          'sparc.common',
          'sparc.db'
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts':['cache=sparc.apps.cache.cache:main'],
          },
      )
