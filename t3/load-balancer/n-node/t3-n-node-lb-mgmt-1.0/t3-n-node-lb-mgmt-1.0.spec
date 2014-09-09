Summary: CloudTop T3 N-Node Load Balancer package for Management VM
Name: t3-n-node-lb-mgmt
Version: 1.0
Release: 1
License: GPLv2
URL: http://www.cloudtop.ph
Vendor: CloudTop
Packager: Ken Salanio
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
Group: System Tools
Source0: t3-n-node-lb-mgmt-1.0.tgz

%description
N-Node Load Balancer for CloudTop T3 RDP system, to be installed in the Management VM.
This package includes the Thin Client load balancer, which is installed directly to the
tftpboot file system used by the Thin Clients.

%prep
%setup

%build

%install
rm -rf %{buildroot}

%{__install} -d -m0755 %{buildroot}/opt/lb_mgmt
%{__install} -m0644 src/lb_mgmt/lb_mgmt.py %{buildroot}/opt/lb_mgmt/lb_mgmt.py
%{__install} -m0644 src/lb_mgmt/config.ini %{buildroot}/opt/lb_mgmt/config.ini

%{__install} -d -m0755 %{buildroot}/opt/lb_mgmt/logs
%{__install} -m0644 src/lb_mgmt/logs/lb_mgmt.log %{buildroot}/opt/lb_mgmt/logs/lb_mgmt.log

%{__install} -d -m0755 %{buildroot}/etc/init
%{__install} -m0644 upstart/lb_mgmt.conf %{buildroot}/etc/init/lb_mgmt.conf

%{__install} -d -m0755 %{buildroot}/etc/logrotate.d
%{__install} -m0644 logrotate.d/lb_mgmt %{buildroot}/etc/logrotate.d/lb_mgmt

%{__install} -d -m0755 %{buildroot}/tftpboot/node_fs/opt/lb_tc
%{__install} -m0644 src/lb_tc/lb_tc.py %{buildroot}/tftpboot/node_fs/opt/lb_tc/lb_tc.py
%{__install} -m0644 src/lb_tc/config.ini %{buildroot}/tftpboot/node_fs/opt/lb_tc/config.ini

%{__install} -d -m0755 %{buildroot}/tftpboot/node_fs/root/
%{__install} -m0644 src/lb_tc/.xinitrc %{buildroot}/tftpboot/node_fs/root/.xinitrc

%files
%defattr(-,root,root,-)
/opt/lb_mgmt/lb_mgmt.py
/opt/lb_mgmt/config.ini
/opt/lb_mgmt/logs/lb_mgmt.log
/etc/init/lb_mgmt.conf
/etc/logrotate.d/lb_mgmt
/tftpboot/node_fs/opt/lb_tc/lb_tc.py
/tftpboot/node_fs/opt/lb_tc/config.ini
/tftpboot/node_fs/root/.xinitrc

%changelog
* Wed Jul 15 2014 Ken Salanio - 1.0
- Built Package t3-n-node-lb-mgmt
