"""
setup.py for using pip
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="aoc",
    version="1.0.1",
    author="Aviel Yosef",
    author_email="Avielyo10@gmail.com",
    description="Multi-cluster management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Avielyo10/aoc.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'Click>=7.1.2',
        'PyYAML>=5.4.1',
        'tabulate>=0.8.9'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    entry_points='''
        [console_scripts]
        aoc=aoc.cli:main
    ''',
)