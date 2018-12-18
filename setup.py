from setuptools import setup, find_packages

setup(name='thundra',
      version='2.1.0',
      description='Thundra Python agent',
      url='https://github.com/thundra-io/thundra-lambda-agent-python',
      author='Thundra',
      author_email='python@thundra.io',
      python_requires='>=3',
      packages=find_packages(exclude=('tests', 'tests.*',)),
      install_requires=['requests>=2.16.0', 'opentracing>=2.0', 'wrapt>=1.10.11'],
      zip_safe=True,
      )