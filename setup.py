"""Setup configuration for development."""
from setuptools import setup, find_packages

setup(
    name="oplaadpalen-homeassistant-dev",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "geopy>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
