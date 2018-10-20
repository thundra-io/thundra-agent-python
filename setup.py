from setuptools import setup, find_packages

setup(name='thundra',
      version='2.0.1',
      description='Thundra Python agent',
      url='https://github.com/thundra-io/thundra-lambda-agent-python',
      author='Thundra',
      author_email='python@thundra.io',
      python_requires='>=3',
      packages=find_packages(exclude=('tests', 'tests.*',)),
      install_requires=['opentracing>=2.0'],
      zip_safe=True,
      )