# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os
from setuptools import setup, find_packages

setup_requires = ['vigilo-common'] if not os.environ.get('CI') else []

cmdclass = {}
try:
    from vigilo.common.commands import compile_catalog_plusjs
    cmdclass['compile_catalog'] = compile_catalog_plusjs
except ImportError:
    pass

tests_require = [
    'WebTest',
    'coverage',
    'gearbox',
]

setup(
    name='vigilo-vigigraph',
    version='5.2.0',
    author='Vigilo Team',
    author_email='contact.vigilo@csgroup.eu',
    url='https://www.vigilo-nms.com',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    description="Vigilo metrology interface",
    long_description="Vigilo metrology interface",
    setup_requires=setup_requires,
    install_requires=[
        "vigilo-turbogears",
        ],
    zip_safe=False, # pour pouvoir déplacer app_cfg.py
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
    },
    package_data={
        'vigigraph': [
            'i18n/*/LC_MESSAGES/*.mo',
            'i18n/*/LC_MESSAGES/*.js',
            'templates/*/*',
            'public/js/*.js',
        ],
    },
    message_extractors={
        'vigigraph': [
            ('**.py', 'python', None),
            ('**/public/js/*.js', 'javascript', None),
        ],
    },
    entry_points={
        'paste.app_factory': [
            'main = vigigraph.config.middleware:make_app',
        ],
        'vigilo.models': [
            'populate_db = vigigraph.websetup:populate_db',
        ],
        'vigilo.turbogears.i18n': [
            'vigigraph = vigigraph.i18n:100',
        ],
    },
    cmdclass=cmdclass,
    vigilo_build_vars={
        'nagios': {
            'default': '/nagios/',
            'description': "URL to Nagios' UI relative to the webserver's root",
        },
        'sysconfdir': {
            'default': '/etc',
            'description': "installation directory for configuration files",
        },
        'localstatedir': {
            'default': '/var',
            'description': "local state directory",
        },
    },
    data_files=[
        ('@sysconfdir@/logrotate.d', ['deployment/vigilo-vigigraph.in']),
        (os.path.join('@sysconfdir@', 'vigilo', 'vigigraph'), [
            'deployment/vigigraph.wsgi.in',
            'deployment/vigigraph.conf.in',
            'deployment/settings.ini.in',
            'deployment/who.ini',
            'app_cfg.py',
        ]),
        (os.path.join("@localstatedir@", "log", "vigilo", "vigigraph"), []),
        (os.path.join("@localstatedir@", "cache", "vigilo", "sessions"), []),
    ],
)
