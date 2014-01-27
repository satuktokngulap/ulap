# 4-configure_t3.pp
# Author: Marc Angco
# Last Edited: January 26, 2014
# Description:
# Puppet manifest to set up configuration files on T3
# Based on 4-configure_t3v0.03.sh (Jan 20, 2014)


# Parameters to put on manifest
# $peerIP = IP of peer
# $peerIPMI = IP of IPMI of peer
# $virtualIP = virtual IP to be used by the cluster

class t3-base-configureT3($localIP,$peerIP,$localIPMI,$peerIPMI,$virtualIP,$hostname) {

    notify{ 'Configuring T3':
        message => 'Configuring T3'
    }
    file {"/root/scripts":
        ensure => directory,
        owner => root,
        group => root,
        mode => 740,
        source => "puppet:///modules/ct-files/kickstarter",
        recurse => true,
    }
    file {"/root/scripts/puppet":
        ensure => directory,
        owner => root,
        group => root,
        mode => 740,
    }


    file {"/root/scripts/puppet/configure_t3.sh":
        ensure => file,
        owner => root,
        group => root,
        mode => 0740,
        source => "puppet:///modules/ct-files/t3-scripts/configure_t3.sh"
    }
    
    exec {"configure_t3.sh":

        command => "/root/scripts/4-configure_t3v0.03.sh $localIP $peerIP $localIPMI $peerIPMI $virtualIP $hostname",
        require => [File['/root/scripts/puppet/configure_t3.sh'],File['/root/scripts']],
        cwd => "/root/scripts",
        logoutput => true,
    }
    File['/root/scripts'] -> File['/root/scripts/puppet'] ->  File['/root/scripts/puppet/configure_t3.sh'] -> Exec['configure_t3.sh']
}
