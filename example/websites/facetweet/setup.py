from setuptools import setup, find_packages

setup(
    name = "facetweet",
    version = "0.01",
    author = "afroisalreadyinu",
    install_requires = ["flask"],
    packages=find_packages(),
    zip_safe=False,
    entry_points = {'console_scripts': ['runlocal=facetweet:run']}
)
