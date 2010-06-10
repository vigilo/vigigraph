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
%config(noreplace) %{_sysconfdir}/logrotate.d/%{module}
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%{python_sitelib}/*

