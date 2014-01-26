node 'puppet.t1.cloudtop.ph' {
    include 'mcollective-node'
    iptables::rule {
        'ssh-cloudtop-t1':
            port => '22',
            protocol => 'tcp',
            source => '10.225.1.0/24',
    }
    iptables::rule {
        'ssh-cloudtop-t3':
            port => '22',
            protocol => 'tcp',
            source => '10.225.3.0/24'
    }
    iptables::rule {
        'ssh-ucc-tech':
            port => '22',
            protocol => 'tcp',
            source => '10.40.2.0/24',
    }
    iptables::rule {
        'ssh-ucc-gw':
            port => '22',
            protocol => 'tcp',
            source => '10.16.3.130',
    }
    iptables::rule {
        'ssh-ucc-noc':
            port => '22',
            protocol => 'tcp',
            source => '10.16.3.150',
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
        'puppetmaster-t3-tambubong':
            port => '8140',
            protocol => 'tcp',
            source => '10.19.28.0/25',
    }
    iptables::rule {
        'puppetmaster-t3-sanroque':
            port => '8140',
            protocol => 'tcp',
            source => '10.18.221.0/24',
    }
    iptables::rule {
        'dashboard':
            port => '80',
            protocol => 'tcp',
            source => '10.225.0.0/16',
    }
    iptables::rule {
        'dashboard-tech':
            port => '80',
            protocol => 'tcp',
            source => '10.40.2.0/24',
    }
    iptables::rule {
        'dashboard-t3-tambubong':
            port => '80',
            protocol => 'tcp',
            source => '10.19.28.0/25',
    }
    iptables::rule {
        'puppetdb':
            port => '8081',
            protocol => 'tcp',
            source => '10.225.0.0/16',
    }
    iptables::rule {
        'puppetdb-t3-tambubong':
            port => '8081',
            protocol => 'tcp',
            source => '10.19.28.0/25',
    }
 iptables::rule {
        'rsyslog':
            port => '514',
            protocol => 'tcp',
            source => '10.225.1.200',
    }



}
