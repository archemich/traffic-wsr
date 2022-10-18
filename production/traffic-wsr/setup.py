import pathlib

from pkg_resources import parse_requirements
from setuptools import setup

with pathlib.Path('requirements.txt').open() as reqs_file:
    install_requires = [str(reqs) for reqs in parse_requirements(reqs_file)]

setup(
    name='traffic-wsr',
    description='WorldSkills Russia task',
    author='archemich',
    author_email='archemich@gmail.com',
    setup_requires=['setuptools_scm'],
    use_scm_version={'root': '../..',
                     'relative_to': __file__},
    packages=['traffic_wsr'],
    install_requires=install_requires,
    python_requires='>3.10',
    entry_points={
        'console_scripts': [
            'traffic-wsr = traffic_wsr.main:main'
        ]
    }
)
