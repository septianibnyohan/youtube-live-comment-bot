from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Read README for long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Additional data files to include
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

# Include additional resource files
extra_files = package_files('resources')

setup(
    name="youtube-live-bot",
    version="1.0.0",
    author="Septian",
    author_email="septianibnyohan@gmail.com",
    description="A YouTube Live Comment Bot with advanced automation features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-live-bot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=required,
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-qt>=4.2.0',
            'pytest-asyncio>=0.23.2',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.12.0',
            'black>=23.12.1',
            'isort>=5.13.2',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
            'pylint>=3.0.3',
        ],
        'docs': [
            'Sphinx>=7.1.2',
            'sphinx-rtd-theme>=1.3.0',
            'autodoc>=0.5.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'youtube-bot=youtube_bot.main:main',
        ],
    },
    package_data={
        'youtube_bot': extra_files + [
            'resources/config/*.json',
            'resources/data/*.txt',
            'resources/ui/styles/*.qss',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/youtube-live-bot/issues',
        'Source': 'https://github.com/yourusername/youtube-live-bot',
        'Documentation': 'https://youtube-live-bot.readthedocs.io/',
    },
    keywords=[
        'youtube',
        'automation',
        'bot',
        'live-chat',
        'comments',
        'pyqt6',
        'selenium',
    ],
    # Custom settings for additional metadata
    options={
        'bdist_wheel': {
            'universal': False,  # Not compatible with Python 2
        }
    },
    platforms=['any'],
    license='MIT',
    # Test suite
    test_suite='tests',
    tests_require=[
        'pytest>=7.4.3',
        'pytest-qt>=4.2.0',
        'pytest-asyncio>=0.23.2',
        'pytest-cov>=4.1.0',
        'pytest-mock>=3.12.0',
    ],
)