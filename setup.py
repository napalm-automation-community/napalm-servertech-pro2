"""setup.py file."""

from setuptools import setup, find_packages

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

with open("README.md", "r") as fs:
    long_description = fs.read()


__author__ = "Antoine Meillet <antoine.meillet@gmail.com>"

setup(
    name="napalm-servertech-pro2",
    version="0.1.0",
    packages=find_packages(),
    author="Antoine Meillet",
    author_email="antoine.meillet@gmail.com",
    description="NAPALM driver for ServerTech PRO2 PDUs",
    license="Apache 2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    url="https://github.com/napalm-automation-community/napalm-servertech-pro2",
    include_package_data=True,
    install_requires=reqs,
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
