#!/usr/bin/env python
from setuptools import setup, find_packages


dev_requires = [
    'Sphinx==1.2.2',
]

tests_require = [
    'factory_boy==2.4.1',
]

install_requires = [
    'apache-libcloud>=1.1.0,<2.2.0',
    'nodeconductor>0.148.3',
]


setup(
    name='waldur-aws',
    version='0.11.1',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='http://waldur.com',
    description='Waldur plugin for managing Amazon Web Services.',
    long_description=open('README.rst').read(),
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'dev': dev_requires,
        'test': tests_require,
    },
    entry_points={
        'nodeconductor_extensions': (
            'waldur_aws = waldur_aws.extension:AWSExtension',
        ),
    },
    tests_require=tests_require,
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
