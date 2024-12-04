from setuptools import setup, find_packages

setup(
    name="kwiz",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",  # Add any dependencies your wrapper needs
    ],
    description="A Python wrapper for WhatsApp Business API",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="youremail@example.com",
    url="https://github.com/yourusername/kwiz",  # Replace with your actual repo link
)
