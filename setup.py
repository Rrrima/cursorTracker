"""
setup.py - Creates a proper macOS app bundle with required permissions
"""
from setuptools import setup

APP = ['tracker.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'CursorMonitor',
        'CFBundleDisplayName': 'Cursor Monitor',
        'CFBundleGetInfoString': "Tracking cursor interactions",
        'CFBundleIdentifier': "com.example.cursor-monitor",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2024, Your Name, All Rights Reserved",
        # Request necessary permissions
        'NSAppleEventsUsageDescription': 'This app needs to monitor cursor events.',
        'NSAccessibilityUsageDescription': 'This app needs accessibility access to monitor cursor interactions.',
        # Required permissions
        'NSRequiredAttributes': {
            'com.apple.security.automation.apple-events': True,
            'com.apple.security.personal-information.accessibility': True
        }
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)