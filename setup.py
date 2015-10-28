from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='sparc.apps.cache',
      version=version,
      description="A generic CSV to SQL DB caching utility.",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
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
          'argparse',
          'pyinstaller',
          'SQLAlchemy',
          'sparc.common',
          'sparc.db',
          'sparc.cache'
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts':['cache=sparc.apps.cache.cache:main'],
          },
      )
