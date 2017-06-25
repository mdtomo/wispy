from setuptools import setup, find_packages 

setup(
    name='wispy',
    version='0.1',
    license='MIT',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=['pcapy'],
)
