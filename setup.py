from setuptools import setup, find_packages

setup(name='thundra',
      version='1.3.0',
      description='Thundra Python agent',
      url='https://github.com/thundra-io/thundra-lambda-agent-python',
      author='Thundra',
      author_email='support@thundra.io',
      python_requires='>=3',
      packages=find_packages(exclude=('tests', 'tests.*',)),
      install_requires=['opentracing>=2.0'],
      zip_safe=True,
      )