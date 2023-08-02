import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlh",
    version = '0.0.7',
    author="Devendra Kumar Sahu",
    author_email="devsahu99@gmail.com",
    description="This package provides helper utilities for machine learning tasks. One major utility is calculation of weight of evidence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devsahu99/mlh",
    packages=['mlh'],
    install_requires=[
        'pandas','scipy','IPython','matplotlib', 'snowflake-connector-python[pandas]', 's3fs', 'boto3', 'openpyxl', 'xlsxwriter'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
