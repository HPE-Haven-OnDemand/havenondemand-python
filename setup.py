from setuptools import setup, find_packages
import sys, os

version = '2.0.1'

setup(name='havenondemand',
      version=version,
      description="Haven OnDemand Python client library",
      long_description="""\
	  This Python client library helps you easily access over 70 APIs from HPE Haven OnDemand platform.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Haven OnDemand havenondemand hod',
      author='Phong Vu, Tyler Nappy',
      author_email='van-phong.vu@hpe.com, tyler.nappy@hpe.com',
      url='http://havenondemand.com',
      license='',
      packages=find_packages(exclude=[]),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
            'requests'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
