import re
import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

README = (here / 'README.md').read_text(encoding='utf-8')
VERSION = (here / 'VERSION').read_text()

parse_reqs = re.compile(r"([^# \n]*)([# \n].*)?")
reqs = (here / 'requirements.txt').read_text(encoding='utf-8')
requirements = [m.groups()[0]
                for m in map(parse_reqs.match, reqs.split('\n'))
                if m.groups()[0]]

setup(
    name='entitlements',
    version=VERSION,
    description='',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Alex Nasukovich',
    author_email='chemiron34@gmail.com',
    url="https://authmachine.com",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='~=3.5',
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
    ]
)
