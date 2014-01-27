# 1-install_preliminaries.pp
# Author: Marc Angco
# Last Edited: January 20, 2014
# Description:
# Puppet manifest to install preliminary packages for CloudTop T3
# based on 1-install-preliminaries.sh


class t3-base-install-prelim {
    notify{ 'Installing Preliminaries':}
    notify{"Setting up proxy":}
    file {"/etc/profile.d/export_proxy.sh":
        content => "export http_proxy='http://10.225.1.245:8080 
                     export https_proxy='http://10.225.1.245:8080'"
    }
    notify{"Setting up as CloudTop Base server":}
    include cloudtop-t3-base

    # Check restrict tick.redhat
    
    # Installing Third-party repository

    notify{"Installing EPEL repository packages":
    package {'elrepo':
        ensure => present,
        source => "http://elrepo.org/elrepo-release-6.5.el6.elrepo.noarch.rpm",
        provider => rpm,
    }
    

    # Package installation

    notify{"Setting package groups (KVM,cluster,DRBD,GFS,NFS,Utilities)":}
    
    # KVM packages
    $kvmpackages = ['kvm','qemu-kvm-tools','qemu-kvm',
                    'python-virtinst','virt-manager','virt-viewer',
                    'bridge-utils','libvirt','virt-install']
    # Cluster packages
    $clusterpackages = ['cman','corosync','rgmanager','ricci']

    # DRBD packages
    $drbdpackages = ['drbd-utils','kmod-drbd83']

    # GFS2 packages
    $gfs2packages = ['gfs2-utils','lvm2-cluster']

    # NFS packages
    $nfspackages = ['nfs-utils','nfs-utils-lib']

    # Utility packages
    $utilpackages = ['syslinux','gpm','mlocate','rsync','wget','twisted']

    notify{"Installing KVM packages":}
    package { $kvmpackages:
        ensure => present,
        }

    notify{"Installing Cluster packages":}
    package { $clusterpackages:
        ensure => present,
        }

    notify{"Installing GFS2 packages":}
    package { $gfs2packages:
        ensure => present,
        }
    
    notify{"Installing NFS packages":}
    package { $nfspackages:
        ensure => present,
        }

    notify{"Installing Utility packages":}
    package { $utilpackages:
        ensure => present,
        }

    notify{"Installing DRBD packages":}
    package { $drbdpackages:
        ensure => present,
        }

    notify{"Installing obliterate-peer.sh":}

    file {'/sbin/obliterate-peer.sh':
        ensure => present,
        source => "http://alteeve.com/files/an-cluster/sbin/obliterate-peer.sh",
        mode => 755,
    }
    #
    # exec {'/sbin/obliterate-peer.sh':
    #    command => '/sbin/obliterate-peer.sh',
    # }

    # Generate ssh key
    notify{'Creating ssh-key':}
    exec {'ssh-keygen':
        command => 'ssh-keygen -t rsa -N "" -b 2048 -f ~/.ssh/id_rsa'
    }

}
