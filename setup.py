import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='warhammer_stats-akabbeke',
    version="0.0.2",
    author="Adam Kabbeke",
    author_email='akabbeke@gmail.com',
    description="Warhammer 40k stats tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akabbeke/warhammer_stats",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.6',
)