#!/usr/bin/env python
from setuptools import setup, find_packages


dev_requires = [
    'Sphinx==1.2.2',
]

tests_require = [
    'factory_boy==2.4.1',
]

install_requires = [
    'apache-libcloud>=1.1.0',
    'nodeconductor>=0.110.0',
]


setup(
    name='nodeconductor-aws',
    version='0.1.3',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='http://nodeconductor.com',
    description='NodeConductor plugin for managing Amazon Web Services.',
    long_description=open('README.rst').read(),
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
            'nodeconductor_aws = nodeconductor_aws.extension:AWSExtension',
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
