from __future__ import print_function
from setuptools import setup, find_packages

entry_points = """
StatsDataViewer=StatsDataViewer:setup
"""

with open('README.rst') as infile:
    LONG_DESCRIPTION = infile.read()

with open('version.py') as infile:
    exec(infile.read())

setup(name='myplugin',
      version=__version__,
      description='My example plugin',
      long_description=LONG_DESCRIPTION,
      url="https://github.com/jk31768/StatsDataViewer",
      author='',
      author_email='',
      packages = find_packages(),
      package_data={},
      entry_points=entry_points
    )
