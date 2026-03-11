from setuptools import setup, find_packages

setup(
    name="red-ai",
    version="2.0.0",
    description="AI-powered RHEL configuration tool",
    author="Natesh Sharma",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "red-ai=red_ai.cli:entry_point",
        ],
    },
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
