# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = "1.0.0"

setup(
    name="hl7db2s",
    version=version,
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="",
    author="Aurthur Musendame",
    author_email="aurthurmusendame@gmail.com",
    url="",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pymysql",
        "pandas",
        "requests",
        "sqlalchemy",
        "schedule"
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        "dev": [
            "pytest",
            "coverage",
        ]
    },
    entry_points={
        "console_scripts": ["results2s=cli:main"]
    }
)
