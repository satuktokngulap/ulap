node 'puppet.t1.cloudtop.ph' {
    include 'mcollective-node'
    iptables::rule {
        'ssh':
            port => '22',
            protocol => 'tcp',
    }
    iptables::rule {
        'snmp':
            port => '161',
            protocol => 'udp',
            source => '10.225.1.201',
    }
    iptables::rule {
        'puppetmaster':
            port => '8140',
            protocol => 'tcp',
            source => '10.225.0.0/16',
    }
    iptables::rule {
        'dashboard':
            port => '80',
            protocol => 'tcp',
            source => '10.225.0.0/16',
    }
    iptables::rule {
        'puppetdb':
            port => '8081',
            protocol => 'tcp',
            source => '10.225.0.0/16',
    }
    iptables::rule {
        'rsyslog':
            port => '514',
            protocol => 'tcp',
            source => '10.225.1.200',
    }



}

node 'marionette' {
    service { 'puppet':
        ensure => running,
    }

    include 'mcollective-node'
    iptables::rule {
        'ssh-gw':
                port => '22',
                protocol => 'tcp',
                source => '10.225.1.202',
    }
    iptables::rule {
        'activemq':
                port => '61613',
                protocol => 'tcp',
                source => '10.225.1.0/24',
    }
    iptables::rule {
        'snmp':
            port => '161',
            protocol => 'udp',
            source => '10.225.1.201',
    }
}


node 'victim' inherits 'cloudtop-base' {
    include 'mcollective-node'
    service { 'puppet':
        ensure => running,
    }
    sudo::conf { 'mac':
        priority => 10,
        content => 'mac ALL=(ALL) NOPASSWD: ALL',
    }
}
