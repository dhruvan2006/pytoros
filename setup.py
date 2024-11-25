from setuptools import setup, find_packages

setup(
    name="pytoros",
    version="0.1.0",
    description="An unoffical pythonic wrapper for Toros Finance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dhruvan Gnanadhandayuthapani",
    author_email="dhruvan2006@gmail.com",
    url="https://github.com/dhruvan2006/pytoros",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas"
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
