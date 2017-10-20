from setuptools import setup, find_packages

setup(
    name='pyshowoff',
    version='0.1.0a1',
    author='Aiden Nibali',
    description='Python client for the Showoff web display',
    license='Apache Software License 2.0',
    packages=find_packages(),
    test_suite='tests',
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
