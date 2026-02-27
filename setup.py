from setuptools import setup, find_packages

setup(
    name="pulsar-mouse-tool",
    version="1.0.0",
    description="Pulsar X2V2 Mini mouse tool with KDE Plasma integration",
    author="Pulsar Mouse Tool",
    packages=find_packages(),
    install_requires=[
        "pyusb>=1.0.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pulsard=pulsard.service:main",
        ],
    },
)
