from setuptools import setup

setup(
    name='megans_law',
    packages=['megans_law'],
    version='1.0',
    description="An automated method to query state Megan's Law databases"
                "(CA Only)",
    author='Shyam Saladi',
    author_email='saladi@caltech.edu',
    url='https://github.com/LASciFair/megans-law',
    download_url='https://github.com/LASciFair/megans-law/tarball/0.1',
    keywords=['automation'],
    license='GNU General Public License v3 (GPLv3)',
    entry_points={'console_scripts': [
        'ca_megans_law.py=megans_law.ca_megans_law:main']},
    install_requires=['pandas', 'selenium'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pandas']
)
