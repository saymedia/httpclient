from setuptools import setup

setup(
    name='httpclient',
    version='0.01',
    description='HTTP Client library for Python',
    long_description=open('README.rst').read(),
    author='Franck Cuny',
    author_email='franck.cuny@gmail.com',
    url='https://github.com/franckcuny/httpclient',
    packages=['httpclient'],
    license='MIT',
    tests_require=['coverage', 'nose', 'unittest2', 'pep8'],
    install_requires=['http', 'urllib3'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ]
)
