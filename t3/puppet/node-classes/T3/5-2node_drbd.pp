# 5-2node_drbd.pp
# Author: Marc Angco
# Last Edited: January 26, 2014
# Description:
# Puppet manifest to set up DRBD on T3
# Based on 5-2node_drbd.sh (Jan 10, 2014)


class t3-base-drbd {

    notify{ 'Configuring DRBD':
        message => 'Configuring DRBD'
    }

    notify {'Ensure scripts folder is created':}
    #file {"/root/scripts":
    #    ensure => directory,
    #    owner => root,
    #    group => root,
    #    chmod => 0740,
    #}
    notify {'Copying 2node-drbd.sh script':}
    file {"/root/scripts/2node-drbd.sh":
        ensure => file,
        owner => root,
        group => root,
        mode => 0740,
        source => "puppet:///modules/ct-files/t3-scripts/2node-drbd.sh"
    }
    notify {'Running drbd script':}
    exec {"2node-drbd.sh":

        command => "/root/scripts/2node-drbd.sh",
        require => File['/root/scripts/2node-drbd.sh'],
        logoutput => true,
        timeout => 3000,

    }
    File['/root/scripts'] -> File['/root/scripts/2node-drbd.sh'] -> Exec['2node-drbd.sh']
}
