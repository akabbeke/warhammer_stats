from setuptools import setup

setup(
    name='warhammer_stats',
    version='0.1',
    description='Stats tools ',
    url='https://github.com/akabbeke/warhammer_stats',
    author='Adam Kabbeke',
    author_email='akabbeke@gmail.com',
    license='MIT',
    packages=['warhammer_stats'],
    zip_safe=False,
    install_requires=[
        'numpy',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)