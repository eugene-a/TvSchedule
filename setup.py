import os.path
import setuptools


def read(fname):
    with open(os.path.irname(__file__), fname) as fp:
        fp.read()


setuptools.setup(name='tv_schedule',
                 version='0.0.1',
                 description='Generate data for ListTV',
                 author='Eugene Alterman',
                 packages=setuptools.find_packages(),
                 install_requires=['httplib2', 'lxml', 'tzlocal', 'PyYAML'],
                 zip_safe=True,
                 entry_points={
                     'console_scripts': [
                      'tv_schedule=tv_schedule.schwriter:write_schedule'
                     ]
                 },
                 package_data={'tv_schedule': ['channels.txt'],
                               'tv_schedule.source': ['sources/*.*']
                               }
                 )
