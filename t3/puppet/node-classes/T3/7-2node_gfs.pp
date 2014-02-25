# 7-2node_gfs.pp
# Author: Marc Angco
# Last Edited: January 20, 2014
# Description:
# Puppet manifest to set up GFS on T3
# Based on 7_2node_gfs.sh (Jan 10, 2014)

class t3-base-2node-gfs {

    notify{ 'Configuring GFS':
        message => 'Configuring GFS'
    }
    #file {"/root/scripts":
    #    ensure => directory,
    #}

    file {"/root/scripts/2node-gfs.sh":
        ensure => file,
        owner => root,
        group => root,
        mode => 0740,
        source => "puppet:///modules/ct-files/t3-scripts/2node-gfs.sh"
    }
    exec {"2node-gfs.sh":

        command => "/root/scripts/2node-gfs.sh",
        require => File['/root/scripts/2node-gfs.sh'],
        logoutput => true,
    }
    File['/root/scripts'] -> File['/root/scripts/2node-gfs.sh'] -> Exec['2node-gfs.sh']

#    service { "cman":
#        enable => true,
#        ensure => running,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
#    }
    service { "rgmanager":
        enable => true,
        ensure => running,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
    }
}
