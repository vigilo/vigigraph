# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

sysconfdir = os.getenv("SYSCONFDIR", "/etc")

tests_require = [
    'WebTest',
    'BeautifulSoup',
    'coverage',
]

setup(
    name='vigigraph',
    version='2.0.0',
    description='',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    #url='',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    install_requires=[
        "vigilo-turbogears",
        ],
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
            'templates/*/*',
            'public/js/*.js',
#            'public/*/*',
        ],
    },
    message_extractors={
        'vigigraph': [
            ('**.py', 'python', None),
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

    data_files=[
        (os.path.join(sysconfdir, 'vigilo/vigigraph/'), [
            'deployment/vigigraph.conf',
            'deployment/vigigraph.wsgi',
            'deployment/settings.ini',
        ]),
    ],
)
