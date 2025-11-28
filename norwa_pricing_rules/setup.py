from setuptools import setup, find_packages

setup(
    name="norwa_pricing_rules",  # The name of your app
    version="0.0.1",  # The version of your app
    author="Newton Manyisa/newty",
    author_email="manyisanewton26@gmail.com",
    description="Pricing and discount approval rules for Norwa Africa",
    long_description=open("README.md").read(),  # You can add more details in a README file
    long_description_content_type="text/markdown",
    url="https://github.com/manyisanewton/norwa_pricing_rules",  # Your GitHub URL or project URL
    packages=find_packages(),  # Automatically find all packages in the directory
    include_package_data=True,  # Ensures non-Python files are included (like fixtures)
    install_requires=[  # List of dependencies that your app requires
        "frappe>=13.0.0",  # Ensure that Frappe version is compatible with your app
        "pytest",  # You mentioned using pytest for testing
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Minimum Python version
)
