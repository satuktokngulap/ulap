# 5-2node_lvm.pp
# Author: Marc Angco
# Last Edited: January 26, 2014
# Description:
# Puppet manifest to set up LVM on T3
# Based on 6-2node_lvm.sh (Jan 10, 2014)

class t3-base-lvm {
    service { "cman":
        enable => true,
        ensure => running,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
    }
    service { "clvmd":
        enable => true,
        # ensure => stopped,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
    }
    service { "drbd":
        enable => true,
        ensure => running,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
    }
    service { "modclusterd":
        enable => true,
        ensure => running,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
    }
    service { "ricci":
        enable => true,
        ensure => running,
        #hasrestart => true,
        #hasstatus => true,
        #require => Class["config"],
    }
    exec { "clvmd":
        command => "clvmd -R",
        path => "/usr/bin:/usr/sbin:/bin:/usr/local/bin",
        #refreshonly => true,
    
    }

    file {"/root/scripts/2node-lvm.sh":
        ensure => file,
        owner => root,
        group => root,
        mode => 0740,
        source => "puppet:///modules/ct-files/t3-scripts/2node-lvm.sh"
    }
    exec {"2node-lvm.sh":

        command => "/root/scripts/2node-lvm.sh",
        require => File['/root/scripts/2node-lvm.sh']
    }
    File['/root/scripts/2node-lvm.sh'] -> Exec['2node-lvm.sh']

}
