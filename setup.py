from setuptools import setup,find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='bbcmd',
    version='1.2',
    author='Lucian Cooper',
    url='https://github.com/luciancooper/bbcmd',
    description='Baseball Statistics Simulator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='baseball statistics sabermetrics',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    packages=find_packages(),
    install_requires=['cmdprogress','numpy','pandas','beautifulsoup4'],
    entry_points={
        'console_scripts': [
            'bbsim = bbsim.__main__:main',
            'bbscrape = bbscrape.__main__:main',
        ]
    },
)
