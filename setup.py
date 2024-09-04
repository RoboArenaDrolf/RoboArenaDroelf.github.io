from setuptools import setup, find_packages

setup(
    name="CyberClash",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.0",
    install_requires=["pygame", "screeninfo", "pkg_resources"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "start-game=CyberClash.__main__:main",
        ]
    },
)
