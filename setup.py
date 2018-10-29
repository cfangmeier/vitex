from setuptools import setup

import sys

if sys.version_info < (3, 6):
    print('vitex requires python>=3.6.')
    exit(1)

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('README.md') as f:
    desc = f.read()

setup(
    name='vitex',
    version='0.1.0',
    description='An unholy conglomeration of vim, evince, and friends for writing LaTeX',
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/cfangmeier/vitex',
    author='Caleb Fangmeier',
    author_email='caleb@fangmeier.tech',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='vim LaTeX Gtk',
    install_requires=requirements,
    scripts=[
        'vitex',
    ],
    package_data={
        # If any package contains *.txt files, include them:
        '': ['requirements.txt'],
        # And include any *.dat files found in the 'data' subdirectory
        # of the 'mypkg' package, also:
        # 'mypkg': ['data/*.dat'],
    }
)
