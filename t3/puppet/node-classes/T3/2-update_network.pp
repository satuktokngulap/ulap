# 2-update_network.pp
# Author: Marc Angco
# Last Edited: January 20, 2014
# Description:
# Puppet manifest to configure and update network interfaces


class t3-base-update-network ($gateway){

    file {"/etc/sysconfig/network-scripts/ifcfg-eth0_bak":
        ensure => file,
        source => "/etc/sysconfig/network-scripts/ifcfg-eth0"
    }
    file {"/etc/sysconfig/network-scripts/ifcfg-eth1_bak":
        ensure => file,
        source => "/etc/sysconfig/network-scripts/ifcfg-eth1"
    }
    file {"/etc/sysconfig/network-scripts/ifcfg-eth0":
        ensure => file,
        content => template("/etc/puppet/manifests/templates/networking/ifcfg-eth0.erb")
    }
    file {"/etc/sysconfig/network-scripts/ifcfg-eth2":
        ensure => file,
        content => template("/etc/puppet/manifests/templates/networking/ifcfg-eth1.erb")
    }
    file {"/etc/sysconfig/network-scripts/ifcfg-br0":
        ensure => file,
        content => template("/etc/puppet/manifests/templates/networking/ifcfg-br0.erb")
    }
    file {"/etc/sysconfig/network-scripts/ifcfg-br1":
        ensure => file,
        content => template("/etc/puppet/manifests/templates/networking/ifcfg-br1.erb")
    }
}
