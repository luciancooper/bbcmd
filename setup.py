from setuptools import setup

setup(
    name='bbcmd',
    version='1.0',
    author='Lucian Cooper',
    url='https://github.com/luciancooper/bbcmd',
    description='Baseball command line tools',
    packages=['bbsim','bbdata','cmdtools'],
    install_requires=[
        'numpy',
        'pandas',
        'array',
        'argparse',
        're',
        'xml',
        'os',
        'collections',
        'datetime',
        'math',
        'time',
    ],
    entry_points={
        'console_scripts': [
            'bbsim = bbsim.__main__:main',
            'bbdata = bbdata.__main__:main',
            #'bbscrape = bbdata.scrape.__main__:main',
        ]
    },
)
