import distutils.cmd
import pathlib
import re

from setuptools import setup


PACKAGE_NAME = 'parser_2gis'
ROOT_DIR = pathlib.Path(__file__).parent
VERSION_PATH = ROOT_DIR / PACKAGE_NAME / 'version.py'
README_PATH = ROOT_DIR / 'README.md'

long_description = README_PATH.read_text(encoding='utf-8')
long_description_content_type = 'text/markdown'

match = re.search(r'^version\s*=\s*[\'"](?P<version>.+?)[\'"]',
                  VERSION_PATH.read_text(encoding='utf-8'), re.M)
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
        import os
        import shutil
        import subprocess
        import sys

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
            shutil.rmtree(ROOT_DIR / 'build', ignore_errors=True)
            try:
                os.remove(ROOT_DIR / f'{dist_filename}.spec')
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
        packages=[PACKAGE_NAME],
        include_package_data=True,
        python_requires='>=3.7',
        keywords='parser scraper 2gis',
        url='https://github.com/interlark/parser-2gis',
        install_requires=[
            'pychrome==0.2.3',
            'pydantic>=1.9.0',
            'psutil>=5.4.8',
            'requests>=2.13.0',
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
