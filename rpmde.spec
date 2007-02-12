%include	/usr/lib/rpm/macros.perl
Summary:	RPM Development Environment
Summary(pl.UTF-8):   Środowisko do tworzenia RPM-ów
Name:		rpmde
Version:	1.0.1
Release:	0.12
License:	GPL v2
Group:		Applications
Source0:	http://kaizen.macroelite.ca/pub/rpmde/%{name}-release-%{version}.tar.gz
# Source0-md5:	736f9e0dd3489a17c719625e5ff33d64
Source1:	%{name}.conf
Patch0:		%{name}-mod_perl.patch
Patch1:		%{name}-config.patch
Patch2:		%{name}-corrupt.patch
URL:		http://kaizen.macroelite.ca/index.pl/rpmde2
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.194
Requires:	apache >= 2.0
# not automatically detected
Requires:	perl-Class-DBI-mysql
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}

%description
The RPM Development Environment (RPMDE) is used to help RPM-based
Linux distribution managers, package managers and testers do their job
more quickly and efficiently.

The RPMDE consists of two parts;
- a front-end interface to manage the distribution
- a back-end build daemon that handles the process of building the
  RPMs.

%description -l pl.UTF-8
RPM Development Environment (RPMDE) służy pomocą zarządzającym
dystrybucjami Linuksa opartymi na pakietach RPM, zarządzającym
pakietami i testerom przy wykonywaniu pracy szybciej i wydajniej.

RPMDE składa się z dwóch części:
- interfejsu frontendowego do zarządzania dystrybucją
- backendowygo demona budującego obsługującego proces budowania
  pakietów RPM.
  
%package daemon
Summary:	RPMDE daemon
Summary(pl.UTF-8):   Demon RPMDE
Group:		Daemons

%description daemon
rpmde back-end build daemon that handles the process of building the
RPMs.

%description daemon -l pl.UTF-8
Backendowy demon budujący rpmde obsługujący proces budowania pakietów
RPM.

%package common
Summary:	RPMDE Common Modules
Summary(pl.UTF-8):   Wspólne moduły RPMDE
Group:		Libraries

%description common
RPMDE Common Modules.

%description common -l pl.UTF-8
Wspólne moduły RPMDE.

%prep
%setup -q -n %{name}-release-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%install
rm -rf $RPM_BUILD_ROOT

# common modules
install -d $RPM_BUILD_ROOT%{perl_vendorlib}/Kaizen/RPMDE
cp -a common-modules-1.0/Kaizen/RPMDE/* $RPM_BUILD_ROOT%{perl_vendorlib}/Kaizen/RPMDE

# frontend
install -d $RPM_BUILD_ROOT/var/lib/rpmde/rpm/{build_logs,SOURCES,SPECS,TMPSRC}
install -d $RPM_BUILD_ROOT/var/lib/rpmde/{rpm/{base,updates}/distrodir,SRPMS/distrodir/{base,updates}}
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_datadir}/%{name}}
install -d $RPM_BUILD_ROOT/var/log/rpmde
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf

cp -a rpmde-1.0/etc/* $RPM_BUILD_ROOT%{_sysconfdir}
cp -a rpmde-1.0/modules/Kaizen/RPMDE.pm $RPM_BUILD_ROOT%{perl_vendorlib}/Kaizen
cp -a rpmde-1.0/www/* $RPM_BUILD_ROOT%{_datadir}/%{name}

# daemon
install -d $RPM_BUILD_ROOT%{_sbindir}
install rpmde_daemon-1.0/rpmde_daemon.pl $RPM_BUILD_ROOT%{_sbindir}/%{name}-daemon

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = 1 ]; then
%banner %{name} -e <<EOF
If this is your first install of RPMDE then you need to setup MySQL database:

mysqladmin create rpmde
mysql -e "GRANT select,insert,update,delete ON rpmde.* TO rpmde@localhost IDENTIFIED BY 'PASSWORD'"
mysql -e "GRANT select,insert,update,delete ON rpmde.* TO rpmde@BUILD_SERVER_HOST  IDENTIFIED BY 'PASSWORD'"
zcat %{_docdir}/%{name}-%{version}/database/rpmde.sql | mysql rpmde

EOF
fi

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%files
%defattr(644,root,root,755)
%doc rpmde-1.0/database
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/rpmde.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/database.pm
%{perl_vendorlib}/Kaizen/RPMDE.pm
/var/lib/rpmde
%{_datadir}/%{name}
%dir %attr(770,root,http) /var/log/rpmde

%files common
%defattr(644,root,root,755)
%dir %{perl_vendorlib}/Kaizen
%{perl_vendorlib}/Kaizen/RPMDE

%files daemon
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/%{name}-daemon
