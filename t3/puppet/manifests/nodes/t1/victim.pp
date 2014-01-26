node 'victim' inherits 'cloudtop-base' {
    include 'mcollective-node'
    include 'ct-mcollective-agents'
    service { 'puppet':
        ensure => running,
    }
    sudo::conf { 'mac':
        priority => 10,
        content => 'mac ALL=(ALL) NOPASSWD: ALL',
    }
}
