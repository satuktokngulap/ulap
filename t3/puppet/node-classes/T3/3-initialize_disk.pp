# 3-initialize_disk.pp
# Author: Marc Angco
# Last Edited: January 20, 2014
# Description:
# Puppet manifest to initialize disk for File system
# Based on 3-initialize_disk.sh (Jan 10, 2014)

class t3-base-initialize_disk {

    notify{ 'Configuring T3':
        message => 'Configuring T3'
    }

    notify{'Creating scripts directory':}
    file {"/root/scripts":
        ensure => directory,
        owner => root,
        group => root,
        chmod => 0740,
    }
    notify{'Copying initialize disk script':}
    file {"/root/scripts/initialize_disk.sh":
        ensure => file,
        owner => root,
        group => root,
        chmod => 0740,
        source => "puppet:///modules/ct-files/t3-scripts/initialize_disk.sh"
    }
    exec {"initialize_disk.sh":

        command => "/root/scripts/initialize_disk.sh",
        require => File['/root/scripts/initialize_disk.sh']
    }
    File['/root/scripts'] -> File['/root/scripts/initialize_disk.sh'] -> Exec['initialize_disk.sh']
}
