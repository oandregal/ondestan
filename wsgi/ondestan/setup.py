import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.4.5',
    'pyramid_debugtoolbar',
    'waitress==0.8.7',
    'geoalchemy2==0.2.3',
    'sqlalchemy==0.9.3',
    'psycopg2==2.5.2',
    'Babel==1.3',
    'lingua==1.6',
    'pyproj==1.9.3',
    'zope.sqlalchemy==0.7.4',
    'pyramid_tm==0.7',
    'twilio==3.6.6'
    ]
test_requires = [
    'requests==2.2.1'
    ]

setup(name='Ondestan',
      version='0.1',
      description='Ondestan',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      message_extractors={'.': [
            ('**.py', 'lingua_python', None),
            ('**.pt', 'lingua_xml', None)
            ]},
      author='',
      author_email='',
      url='',
      keywords='web python pyramid pylons cows gps monitoring sqlalchemy geoalchemy2',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires + test_requires,
      test_suite="ondestan",
      entry_points="""\
      [paste.app_factory]
      main = ondestan:main
      """,
      )
