from setuptools import find_packages, setup

setup(
    name='basket-price-calculator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "dataclasses==0.6"
    ]
)
