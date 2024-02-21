Name:      rockit-domealert
Version:   %{_version}
Release:   1
Summary:   Internal conditions monitoring
Url:       https://github.com/rockit-astro/domealertd
License:   GPL-3.0
BuildArch: noarch

%description


%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/domealertd/
mkdir -p %{buildroot}%{_udevrulesdir}

%{__install} %{_sourcedir}/domealertd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/domealertd@.service %{buildroot}%{_unitdir}

%{__install} %{_sourcedir}/config/clasp.json %{buildroot}%{_sysconfdir}/domealertd/
%{__install} %{_sourcedir}/config/onemetre.json %{buildroot}%{_sysconfdir}/domealertd/
%{__install} %{_sourcedir}/config/goto1.json %{buildroot}%{_sysconfdir}/domealertd/
%{__install} %{_sourcedir}/config/goto2.json %{buildroot}%{_sysconfdir}/domealertd/
%{__install} %{_sourcedir}/config/goto3.json %{buildroot}%{_sysconfdir}/domealertd/
%{__install} %{_sourcedir}/config/goto4.json %{buildroot}%{_sysconfdir}/domealertd/
%{__install} %{_sourcedir}/config/halfmetre.json %{buildroot}%{_sysconfdir}/domealertd/

%package server
Summary:  Conditions monitoring server
Group:    Unspecified
Requires: python3-Pyro4 python3-rockit-domealert
%description server

%files server
%defattr(0755,root,root,-)
%{_bindir}/domealertd
%defattr(0644,root,root,-)
%{_unitdir}/domealertd@.service

%package data-lapalma
Summary: Conditions monitoring data for La Palma telescopes
Group:   Unspecified
%description data-lapalma

%files data-lapalma
%defattr(0644,root,root,-)
%{_sysconfdir}/domealertd/onemetre.json
%{_sysconfdir}/domealertd/clasp.json
%{_sysconfdir}/domealertd/halfmetre.json
%{_sysconfdir}/domealertd/goto1.json
%{_sysconfdir}/domealertd/goto2.json

%package data-sso
Summary: Conditions monitoring data for GOTO South
Group:   Unspecified
%description data-sso

%files data-sso
%defattr(0644,root,root,-)
%{_sysconfdir}/domealertd/goto3.json
%{_sysconfdir}/domealertd/goto4.json

%changelog
