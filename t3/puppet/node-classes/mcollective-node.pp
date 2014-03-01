class  mcollective-node {
    file {'/usr/libexec/mcollective':
        ensure  => directory,
        owner   => root,
        group   => root,
        mode    => '0644',
    }

    file {'/usr/libexec/mcollective/mcollective':
        ensure  => directory,
        owner   => root,
        group   => root,
        mode    => '0644',
    }

    file {'/usr/libexec/mcollective/mcollective/registration':
        ensure  => directory,
        owner   => root,
        group   => root,
        mode    => '0644',
    }

    file {'/usr/libexec/mcollective/mcollective/registration/meta.rb':
        ensure  => present,
        owner   => root,
        group   => root,
        mode    => '0644',
        source  => 'puppet:///modules/ct-files/mcollective/meta.rb',
    }

    class { 'mcollective':
        template                => '/etc/puppet/manifests/templates/mcollective/ct-mconode-server.cfg.erb',
        stomp_host              => '10.225.1.216',
        stomp_user              => 'mcollective',
        stomp_password          => 'marionette',
        stomp_admin             => 'admin',
        stomp_admin_password    => 'activeMQadmin@cloudtop',
        psk                     => 'm@ri0n3tt3PSK',
        port                    => '61613',
        install_client          => true,
        #install_stomp_server => true,
        #install_server => true,
        install_plugins         => true,
        monitor                 => false,
        monitor_tool            => [],
        firewall                => false,
        #firewall_tool => 'iptables',
        #firewall_src => '10.225.0.0/16',
        #firewall_dst => $ipaddress_eth0,
    }
}
