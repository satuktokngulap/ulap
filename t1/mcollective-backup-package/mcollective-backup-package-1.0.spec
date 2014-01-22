Summary: Backup service for CloudTop MCollective
Name: mcollective-backup-package
Version: 1.0
Release: 1
License: GPLv2
URL: http://www.cloudtop.ph
Vendor: CloudTop
Packager: Ken Salanio
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
Group: System Tools
Source0: mcollective-backup-package-1.0.tgz

%description
Backup service for CloudTop MCollective

%prep
%setup

%build

%install
rm -rf %{buildroot}
%{__install} -d -m0755 %{buildroot}/usr/libexec/mcollective/mcollective/agent

%{__install} -m0644 src/agent/backup.rb %{buildroot}/usr/libexec/mcollective/mcollective/agent/backup.rb

%{__install} -m0644 src/agent/backup.ddl %{buildroot}/usr/libexec/mcollective/mcollective/agent/backup.ddl

%{__install} -d -m0755 %{buildroot}/usr/libexec/mcollective/mcollective/application

%{__install} -m0644 src/application/backup.rb %{buildroot}/usr/libexec/mcollective/mcollective/application/backup.rb

%{__install} -d -m0755 %{buildroot}/var/archive

%{__install} -m0644 src/utils/README %{buildroot}/var/archive/README

%{__install} -m0644 src/utils/failed.log %{buildroot}/var/archive/failed.log

%{__install} -d -m0755 %{buildroot}/shared/scripts/backup

%{__install} -m0755 src/shellscripts/backup_cron.sh %{buildroot}/shared/scripts/backup/backup_cron.sh

%{__install} -m0755 src/shellscripts/backup_manual.sh %{buildroot}/shared/scripts/backup/backup_manual.sh

%{__install} -m0755 src/shellscripts/backup_status.sh %{buildroot}/shared/scripts/backup/backup_status.sh

%{__install} -m0755 src/shellscripts/backup_restore.sh %{buildroot}/shared/scripts/backup/backup_restore.sh


%files
%defattr(-,root,root,-)
/usr/libexec/mcollective/mcollective/agent/backup.rb
/usr/libexec/mcollective/mcollective/agent/backup.ddl
/usr/libexec/mcollective/mcollective/application/backup.rb
/var/archive/README
/var/archive/failed.log
/shared/scripts/backup/backup_cron.sh
/shared/scripts/backup/backup_manual.sh
/shared/scripts/backup/backup_restore.sh
/shared/scripts/backup/backup_status.sh

%changelog
* Wed Jan 21 2014 Ken Salanio - 1.0
- Built Package mcollective-backup-package
