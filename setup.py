from setuptools import setup, find_packages

setup(
    name='tree-viewer',
    version='0.0.1',
    packages=find_packages(exclude=['tests*']),
    description='The service for testing of the test function',
    long_description=open('README.md').read(),
    install_requires=[
        'aiohttp',
        'environs',
    ],
    url='',
    author='Aleksei Burov',
    author_email='burov_alexey@mail.ru',
    zip_safe=False
)
