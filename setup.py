import distutils.cmd
import os
import re
import sys

from setuptools import find_packages, setup


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


here = os.path.abspath(os.path.dirname(__file__))
long_description = read_file(os.path.join(here, 'README.md'))
long_description_content_type = 'text/markdown'

version_content = read_file(os.path.join(here, 'parser_2gis', 'version.py'))
match = re.search(r"^version\s*=\s*'(?P<version>.+?)'", version_content, re.M)
assert match
version = match.group('version')


class BuildStandaloneCommand(distutils.cmd.Command):
    """A custom command to build standalone app."""
    description = 'Build standalone app with PyInstaller'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import shutil

        try:
            # Target filename
            dist_filename = 'Parser2GIS'

            # Dist
            build_cmd = [
                'pyinstaller',
                '--clean',
                '--onefile',
                '--windowed',
                '-n', dist_filename,
            ]

            # Icon
            if sys.platform.startswith('win'):
                build_cmd += [
                    '--icon', 'parser_2gis/data/images/icon.ico',
                ]
            elif sys.platform.startswith('darwin'):
                build_cmd += [
                    '--icon', 'parser_2gis/data/images/icon.icns',
                ]

            # Add data
            build_cmd += [
                '--add-data', f'parser_2gis/data{os.pathsep}parser_2gis/data',
                'parser-2gis.py',
            ]

            print('Running command: %s' % ' '.join(build_cmd), file=sys.stderr)
            subprocess.check_call(build_cmd)
        finally:
            # Cleanup
            shutil.rmtree(os.path.join(here, 'build'), ignore_errors=True)
            try:
                os.remove(os.path.join(here, f'{dist_filename}.spec'))
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    setup(
        name='parser-2gis',
        version=version,
        description='Парсер сайта 2GIS',
        long_description=long_description,
        long_description_content_type=long_description_content_type,
        author='Andy Trofimov',
        author_email='interlark@gmail.com',
        packages=find_packages(),
        include_package_data=True,
        python_requires='>=3.7',
        keywords='parser scraper 2gis',
        url='https://github.com/interlark/parser_2gis',
        install_requires=[
            'pychrome==0.2.3',
            'pydantic>=1.9.0',
            'psutil>=5.4.8',
        ],
        extras_require={
            'gui': [
                'PySimpleGUI==4.59.0',
            ],
            'dev': [
                'pyinstaller>=5.0',
                'pytest>=6.2,<8',
                'tox>=3.5,<4',
                'pre-commit>=2.6',
                'wheel>=0.36.2,<0.38',
            ],
        },
        classifiers=[
            "Topic :: Internet",
            "Topic :: Utilities",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Natural Language :: Russian",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        ],
        license='LGPLv3+',
        entry_points={'console_scripts': ['parser-2gis = parser_2gis:main']},
        cmdclass={'build_standalone': BuildStandaloneCommand}
    )
