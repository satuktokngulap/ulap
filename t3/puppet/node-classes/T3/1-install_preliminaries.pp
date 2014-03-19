# 1-install_preliminaries.pp
# Author: Marc Angco
# Last Edited: January 23, 2014
# Description:
# Puppet manifest to install preliminary packages for CloudTop T3
# based on 1-install-preliminaries.sh


class t3-base-install-prelim {
    notify{ 'Installing Preliminaries':}
    notify{'Setting up proxy':}
    file {'/etc/profile.d/export_proxy.sh':
        content => inline_template("export http_proxy='http://10.16.5.100:8080' \n export https_proxy='http://10.16.5.100:8080'\n")
    }
    notify{'Setting up as CloudTop Base server':}
    include cloudtop-t3-base

    # Check restrict tick.redhat

    # Installing Third-party repository

    notify{'Installing ELREPO repository packages':}
    package {'elrepo':
#        unless => 'rpm -qa | grep elrepo-release',
        ensure      => present,
        source      => 'http://elrepo.org/elrepo-release-6-5.el6.elrepo.noarch.rpm',
        provider    => 'rpm',
    }


    # Package installation

    notify{'Setting package groups (KVM,cluster,DRBD,GFS,NFS,Utilities)':}

    # KVM packages
    $kvmpackages = ['qemu-kvm-tools','qemu-kvm',
                    'python-virtinst','virt-manager','virt-viewer',
                    'bridge-utils','libvirt']
    # Cluster packages
    $clusterpackages = ['cman','corosync','rgmanager','ricci']

    # DRBD packages
    $drbdpackages = ['drbd84-utils','kmod-drbd84']

    # GFS2 packages
    $gfs2packages = ['gfs2-utils','lvm2-cluster']

    # NFS packages
    $nfspackages = ['nfs-utils','nfs-utils-lib']

    # Utility packages
    $utilpackages = ['syslinux','gpm','mlocate','rsync','wget']

    notify{'Installing KVM packages':}
    package { $kvmpackages:
        ensure => present,
        }

    notify{'Installing Cluster packages':}
    package { $clusterpackages:
        ensure => present,
        }

    notify{'Installing GFS2 packages':}
    package { $gfs2packages:
        ensure => present,
        }

    notify{'Installing NFS packages':}
    package { $nfspackages:
        ensure => present,
        }

    notify{'Installing Utility packages':}
    package { $utilpackages:
        ensure => present,
        }

    notify{'Installing DRBD packages':}
    package { $drbdpackages:
        ensure      => present,
        require     => Package['elrepo'],
        }

    notify{'Installing obliterate-peer.sh':}

    file {'/sbin/obliterate-peer.sh':
        ensure  => present,
        source  => 'puppet:///modules/ct-files/t3-scripts/obliterate-peer.sh',
        mode    => '0755',

    }
    #
    # exec {'/sbin/obliterate-peer.sh':
    #    command => '/sbin/obliterate-peer.sh',
    # }

    # Generate ssh key
    notify{'Creating ssh-key':}
    file {'/root/.ssh':
        ensure => directory,
    }
    exec {'ssh-keygen':
        command => 'ssh-keygen -t rsa -N "" -b 2048 -f ~/.ssh/id_rsa',
        cwd     => '/root',
        path    => ['/usr/bin', '/usr/sbin'],
        creates => '/root/.ssh/id_rsa',

    }



}
