from setuptools import setup,find_packages

setup(
    name='bbcmd',
    version='1.0',
    author='Lucian Cooper',
    url='https://github.com/luciancooper/bbcmd',
    description='Baseball Statistics Simulator',
    keywords='baseball statistics sabermetrics',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['numpy','pandas'], #'array','argparse','re','xml','os','collections','datetime','math',
    entry_points={
        'console_scripts': [
            'bbsim = bbsim.__main__:main',
            'bbdata = bbdata.__main__:main',
            'bbscrape = bbscrape.__main__:main',
        ]
    },
)
