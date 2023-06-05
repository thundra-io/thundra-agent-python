import codecs
import os.path

from setuptools import setup, find_packages


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(name='thundra',
      version=get_version('thundra/_version.py'),
      description='Thundra Python agent',
      long_description='Thundra Python agent',
      url='https://github.com/thundra-agent-python',
      author='Thundra',
      author_email='python@thundra.io',
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
      packages=find_packages(exclude=('tests', 'tests.*',)),
      install_requires=['requests>=2.16.0', 'opentracing>=2.0', 'wrapt>=1.10.11', 'simplejson', 'enum-compat',
                        'jsonpickle==1.3', 'websocket-client', 'python-dateutil', 'GitPython>=3.1.18', 'fastcounter>=1.1.0', 'pympler'],
      zip_safe=True,
      entry_points={"pytest11": ["thundra-foresight = foresight.pytest_integration.plugin"]},
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
      ],
      )
