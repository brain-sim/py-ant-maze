from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-ant-maze",
    version="0.1.0",
    author="Yihao Liu",
    author_email="yihao.jhu@gmail.com",
    description="A package for building and managing ant maze environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brain-sim/py-ant-maze",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
)
