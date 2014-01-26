class mcomaster-node {
    class { 'mcollective':
        #template         => 'puppet:///modules/mcollective/ucc-server.cfg.erb',
        template          => '/etc/puppet/manifests/templates/mcollective/ct-mcomaster-server.cfg.erb',
        template_client   => '/etc/puppet/manifests/templates/mcollective/ct-mcomaster-client.cfg.erb',
        stomp_host           => '10.225.1.216',
        stomp_user           => 'mcollective',
        stomp_password       => 'marionette',
        stomp_admin          => 'admin',
        stomp_admin_password => 'activeMQadmin@cloudtop',
        psk                  => 'm@ri0n3tt3PSK',
        port          => '61613',
        install_client       => true,
        #install_stomp_server => true,
        #install_server => true,
        install_plugins => true,
        monitor => false,
        monitor_tool => [],
        firewall => true,
        firewall_tool => 'iptables',
        firewall_src => '10.225.0.0/16',
        firewall_dst => $ipaddress_eth0,
    }

    file {"/usr/libexec/mcollective/mcollective/registration/meta.rb":
        ensure => present,
        owner => root,
        group => root,
        mode => 644,
        source => "puppet:///modules/ct-files/mcollective/meta.rb",
    }

    file {"/usr/libexec/mcollective/mcollective/agent/registration.rb":
        ensure => present,
        owner => root,
        group => root,
        mode => 644,
        source => "puppet:///modules/ct-files/mcollective/registration.rb"
    }

    file {"/usr/libexec/mcollective/mcollective/discovery/redisdiscovery.ddl":
        ensure => present,
        owner => root,
        group  => root,
        mode => 644,
        source => "puppet:///modules/ct-files/mcollective/redisdiscovery.ddl"
    }
    file {"/usr/libexec/mcollective/mcollective/discovery/redisdiscovery.rb":
        ensure => present,
        owner => root,
        group  => root,
        mode => 644,
        source => "puppet:///modules/ct-files/mcollective/redisdiscovery.rb"
    }

    package { "redis":
        ensure => installed,
    }
    service { "redis":
        ensure => running,
    }
}
