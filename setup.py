import setuptools

from pipenv.project import Project
from pipenv.utils.dependencies import convert_deps_to_pip

project = Project(chdir=False).parsed_pipfile

requirements = convert_deps_to_pip(project['packages'])
test_requirements = convert_deps_to_pip(project['dev-packages'])

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='warhammer_stats',
    version="0.1.1",
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
    install_requires=requirements,
    test_requirements=test_requirements,
    python_requires='>=3.6',
)
