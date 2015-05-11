from setuptools import setup, find_packages

setup(
    name = "hackerit",
    version = "0.01",
    author = "afroisalreadyinu",
    install_requires = ["flask",'Flask-SQLAlchemy', 'passlib'],
    packages=find_packages(),
    zip_safe=False,
    entry_points = {'console_scripts':
                    ['runlocal=hackerit:run',
                     'createdb=hackerit:create_db',
                     'shell=hackerit:shell']}
)
