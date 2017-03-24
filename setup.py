from setuptools import setup, find_packages

def readfile(name):
    with open(name) as f:
        return f.read()

readme = readfile('README.rst')
changes = readfile('CHANGES.rst')

requires = [
    'setuptools', # for pkg_resources
]

docs_require = [
    'Sphinx',
    'pylons-sphinx-themes',
]

tests_require = [
    'pytest',
    'pytest-cov',
    'mock',
]

setup(
    name='plaster',
    version='0.3.dev0',
    description='A loader interface around multiple config file formats.',
    long_description=readme + '\n\n' + changes,
    author='Michael Merickel',
    author_email='michael@merickel.org',
    url='https://github.com/mmerickel/plaster',
    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requires,
    extras_require={
        'docs': docs_require,
        'testing': tests_require,
    },
    test_suite='tests',
    zip_safe=False,
    keywords='plaster pastedeploy ini config',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
