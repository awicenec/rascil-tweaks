"""Python setup.py for rascil_tweaks package"""
import io
import os
from setuptools import find_packages, setup
from glob import glob
from sysconfig import get_path

def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("rascil_tweaks", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8")
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "git+"))
    ]


setup(
    name="rascil_tweaks",
    version=read("rascil_tweaks", "VERSION"),
    description="Awesome rascil_tweaks created by awicenec",
    url="https://github.com/awicenec/rascil-tweaks/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="awicenec",
    packages=find_packages(exclude=["tests", ".github"]),
    data_files=[
        ("data/models", ["data/models/GLEAM_EGC.fits"]),
        ("data/configurations",glob("data/configurations/*"))
        ],
    install_requires=read_requirements("requirements.txt"),
    extras_require={"test": read_requirements("requirements-test.txt")},
)
