# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

cmdclass = {}
try:
    from babeljs import compile_catalog_plusjs
except ImportError:
    pass
else:
    cmdclass['compile_catalog'] = compile_catalog_plusjs

sysconfdir = os.getenv("SYSCONFDIR", "/etc")

tests_require = [
    'WebTest',
    'BeautifulSoup',
    'coverage',
]

setup(
    name='vigilo-vigigraph',
    version='2.0.8',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    url='http://www.projet-vigilo.org',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    description="Vigilo metrology interface",
    long_description="Vigilo metrology interface",
    install_requires=[
        "vigilo-turbogears",
        ],
    zip_safe=False, # pour pouvoir déplacer app_cfg.py
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
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
        'paste.app_install': [
            'main = pylons.util:PylonsInstaller',
        ],
        'vigilo.models': [
            'populate_db = vigigraph.websetup:populate_db',
        ],
    },

    cmdclass=cmdclass,
    data_files=[
        (os.path.join(sysconfdir, 'vigilo/vigigraph/'), [
            'deployment/vigigraph.conf',
            'deployment/vigigraph.wsgi',
            'deployment/settings.ini',
            'deployment/who.ini',
        ]),
    ],
)
