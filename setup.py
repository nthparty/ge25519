from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The lines below are parsed by `docs/conf.py`.
name = "ge25519"
version = "1.2.0"

setup(
    name=name,
    version=version,
    packages=[name,],
    install_requires=[
        "parts~=1.3",
        "bitlist~=0.7",
        "fe25519~=1.2",
        "fountains~=1.3",
    ],
    license="MIT",
    url="https://github.com/nthparty/ge25519",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Pure Python data structure for working with Ed25519 "+\
                "(and Ristretto) group elements and operations.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
