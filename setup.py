#!/usr/bin/env python3
"""
Professional setup script for Text Converter macOS app
"""

from setuptools import setup, find_packages
import os

# App configuration
APP_NAME = "TextConverter Pro"
APP = ['textconverter_launcher.py']
DATA_FILES = []

# Find all source files
def find_data_files():
    data_files = []
    for root, dirs, files in os.walk('src'):
        if '__pycache__' in root:
            continue
        py_files = [os.path.join(root, f) for f in files if f.endswith('.py')]
        if py_files:
            data_files.append((root, py_files))
    return data_files

OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.textconverter.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Background app (no dock icon)
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.12.0',
        'NSAppleEventsUsageDescription': 'Text Converter needs access to control other applications for text conversion.',
        'NSSystemAdministrationUsageDescription': 'Text Converter needs accessibility permissions to monitor keyboard shortcuts.'
    },
    'packages': find_packages(),
    'includes': ['src.core', 'src.ui', 'src.utils'],
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=find_data_files(),
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    packages=find_packages(),
    install_requires=[
        'rumps>=0.4.0',
        'pyperclip>=1.8.2',
        'pynput>=1.7.6'
    ],
    python_requires='>=3.8',
    author='Simone Mattioli',
    description='Professional text conversion tool for macOS',
    long_description='A professional macOS application for instant text case conversion with global hotkeys.',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: MacOS :: MacOS X',
    ],
)