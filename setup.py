import os
from setuptools import (
    setup,
    find_packages,
)


version = '1.3'
shortdesc ="Mac Finder like view for Plone."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()


setup(name='bda.plone.finder',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Environment :: Web Environment',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='',
      author='Robert Niederreiter',
      author_email='dev@bluedynamics.com',
      url=u'https://github.com/collective/bda.plone.finder',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['bda', 'bda.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'Plone',
          'plone.app.jquerytools',
          # -*- Extra requirements: -*
      ],
      extras_require = dict(
      ),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
