from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc ="Mac Finder like view for browsing plone sites."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='bda.plone.finder',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Web Environment',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',        
      ],
      keywords='',
      author='Robert Niederreiter',
      author_email='dev@bluedynamics.com',
      url=u'https://svn.plone.org/svn/collective/bda.plone.finder',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['bda', 'bda.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'plone.app.jquerytools',
          # -*- Extra requirements: -*
      ],
      extras_require = dict(
      ),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )