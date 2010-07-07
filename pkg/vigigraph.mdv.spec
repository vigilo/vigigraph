%define module  vigigraph
%define name    vigilo-%{module}
%define version 2.0.0
%define release 1%{?svn}

Name:       %{name}
Summary:    Vigilo graphs interface
Version:    %{version}
Release:    %{release}
Source0:    %{module}.tar.bz2
URL:        http://www.projet-vigilo.org
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2

BuildRequires:   python-setuptools
BuildRequires:   python-babel

Requires:   python >= 2.5
Requires:   python-setuptools
Requires:   vigilo-turbogears
Requires:   apache-mod_wsgi
######### Dependance from python dependance tree #########
Requires:   vigilo-turbogears
Requires:   vigilo-models
Requires:   vigilo-themes-default
Requires:   python-TgRum
Requires:   python-rum
Requires:   python-decorator
Requires:   python-paste
Requires:   python-setuptools
Requires:   python-setuptools
Requires:   python-pastedeploy
Requires:   python-tw.forms
Requires:   python-toscawidgets
Requires:   python-turbogears2
Requires:   python-tg.devtools
Requires:   python-repoze.what-quickstart
Requires:   python-repoze.tm2
Requires:   python-tw.rum
Requires:   python-RumAlchemy
Requires:   python-EggTranslations
Requires:   python-babel
Requires:   python-babel
Requires:   python-routes
Requires:   python-webob
Requires:   python-pastescript
Requires:   python-configobj
Requires:   python-configobj
Requires:   python-simplejson
Requires:   python-turbojson
Requires:   python-genshi
Requires:   python-prioritized_methods
Requires:   python-formencode
Requires:   python-webflash
Requires:   python-peak-rules
Requires:   vigilo-common
Requires:   python-transaction
Requires:   python-zope.sqlalchemy
Requires:   python-sqlalchemy
Requires:   python-psycopg2
Requires:   python-repoze.what-pylons
Requires:   python-weberror
Requires:   python-pylons
Requires:   python-repoze.who
Requires:   python-sqlalchemy-migrate
Requires:   python-repoze.who-friendlyform
Requires:   python-repoze.what.plugins.sql
Requires:   python-repoze.who.plugins.sa
Requires:   python-repoze.what
Requires:   python-dateutil
Requires:   python-tw.dojo
Requires:   python-extremes
Requires:   python-addons
Requires:   python-decoratortools
Requires:   python-bytecodeassembler
Requires:   python-zope-interface
Requires:   python-pygments
Requires:   python-tempita
Requires:   python-webtest
Requires:   python-mako
Requires:   python-nose
Requires:   python-beaker
Requires:   python-webhelpers
Requires:   python-repoze.who-testutil
Requires:   python-symboltype

Buildarch:  noarch


%description
Vigilo graphs interface.
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q -n %{module}
cd javascript
#wget http://downloads.sourceforge.net/project/qooxdoo/qooxdoo-legacy/0.7.3/qooxdoo-0.7.3-sdk.tar.gz
wget http://vigilo-dev.si.c-s.fr/cache/qooxdoo-0.7.3-sdk.tar.gz
tar -xzf qooxdoo-0.7.3-sdk.tar.gz
cd ..
patch -p0 < patches/001_qooxdoo_getBoxObjectFor.diff

%build
make PYTHON=%{_bindir}/python SYSCONFDIR=%{_sysconfdir}

%install
rm -rf $RPM_BUILD_ROOT
make install \
	DESTDIR=$RPM_BUILD_ROOT \
	SYSCONFDIR=%{_sysconfdir} \
	PYTHON=%{_bindir}/python

%find_lang %{name}


%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING
%dir %{_sysconfdir}/vigilo
%config(noreplace) %{_sysconfdir}/vigilo/%{module}
%{_sysconfdir}/httpd/conf/webapps.d/%{module}.conf
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%{python_sitelib}/*

