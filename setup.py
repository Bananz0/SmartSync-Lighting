from setuptools import setup, find_packages

setup(
    name="smartsync-lighting",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "spotipy",
        "requests",
        "numpy",
        "pyyaml",
        "python-dotenv",
        "Pillow",
        "opencv-python"
    ],
    entry_points={
        'console_scripts': [
            'smartsync-lighting=src.main:main',
        ],
    },
)