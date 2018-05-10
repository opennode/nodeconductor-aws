Name: waldur-aws
Summary: Amazon plugin for Waldur
Group: Development/Libraries
Version: 0.11.4
Release: 1.el7
License: MIT
Url: http://waldur.com
Source0: %{name}-%{version}.tar.gz

Requires: waldur-core >= 0.156.2
Requires: python-libcloud >= 1.1.0
Requires: python-libcloud < 2.2.0

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

Obsoletes: nodeconductor-aws

%description
Amazon Web Services plugin for Waldur.

%prep
%setup -q -n %{name}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{python_sitelib}/*

%changelog
* Thu May 10 2018 Jenkins <jenkins@opennodecloud.com> - 0.11.4-1.el7
- New upstream release

* Sat Mar 24 2018 Jenkins <jenkins@opennodecloud.com> - 0.11.3-1.el7
- New upstream release

* Fri Dec 1 2017 Jenkins <jenkins@opennodecloud.com> - 0.11.2-1.el7
- New upstream release

* Wed Nov 29 2017 Jenkins <jenkins@opennodecloud.com> - 0.11.1-1.el7
- New upstream release

* Sun Oct 29 2017 Jenkins <jenkins@opennodecloud.com> - 0.11.0-1.el7
- New upstream release

* Mon Sep 4 2017 Jenkins <jenkins@opennodecloud.com> - 0.10.0-1.el7
- New upstream release

* Wed Jul 12 2017 Jenkins <jenkins@opennodecloud.com> - 0.9.3-1.el7
- New upstream release

* Mon Jul 3 2017 Jenkins <jenkins@opennodecloud.com> - 0.9.2-1.el7
- New upstream release
