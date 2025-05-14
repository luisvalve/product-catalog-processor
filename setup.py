from setuptools import setup, find_packages

setup(
    name="product-merger",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "openpyxl>=3.1.2",
        "rich>=13.6.0"
    ],
    entry_points={
        "console_scripts": [
            "product-merger=product_merger.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    description="A tool for merging and enriching automotive product data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 