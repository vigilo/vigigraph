# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = [
    'WebTest',
    'BeautifulSoup',
    'coverage',
]

setup(
    name='vigigraph',
    version='0.1',
    description='',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    #url='',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    install_requires=[
        "tg.devtools",
        "TurboGears2 >= 2.0b7",
        "Catwalk >= 2.0.2",
        "Babel >=0.9.4",
        #can be removed iif use_toscawidgets = False
        "ToscaWidgets >= 0.9.7.1",
        "vigilo-models",
        "vigilo-themes-default",
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
#            'public/*/*',
        ],
    },
    message_extractors={
        'vigigraph': [
            ('**.py', 'python', None),
#            ('public/**', 'ignore', None),
        ],
    },

    entry_points="""
    [paste.app_factory]
    main = vigigraph.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [console_scripts]
    vigigraph-init-db = vigigraph.websetup:init_db
    """,
)
