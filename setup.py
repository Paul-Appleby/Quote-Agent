from setuptools import setup, find_packages

setup(
    name="sales-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.5",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
    },
    python_requires=">=3.8",
)