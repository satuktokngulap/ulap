class  mcollective-node {
  class { 'mcollective':
     stomp_host           => '10.225.1.216',
     stomp_user           => 'mcollective',
     stomp_password       => 'marionette',
     stomp_admin          => 'admin',
     stomp_admin_password => 'activeMQadmin@UCC',
     psk                  => 'm@ri0n3tt3PSK',
     port                 => '61613',
     install_client       => true,
     #install_stomp_server => true,
     #install_server => true,
     install_plugins => true,
     monitor => false,
     monitor_tool => [],
     firewall => true,
     firewall_tool => 'iptables',
     firewall_src => '10.225.1.0/24',
     firewall_dst => $ipaddress_eth0,
  }
}

node 'cloudtop-base'
{
    # Add Admin Users
    add_user { cloudtopadmin:
      email => "gerryroxas@outlook.com",
      uid => 500
    }
    add_ssh_key { cloudtopadmin:
       key => "AAAAB3NzaC1yc2EAAAADAQABAAABAQDm4C93rBH3XDU/EVytthzc9RMjAFrjORF2b+nUmcND1JnV93FwGNpBCLz9g93B35KObhWbNccLrB34iqYt/Hf4hd4nM1vc/hCxKaMYON9ZHAsiSpUp/Ss0t2mvVddbJ7GdWjmUvS+ADmA2PMWpsxvlcCcRvG0RfLPHJ+BCbEwlGX4eHBzokZE8zakDuiwacnOid8rbMtrBerveOzEBwvoX9gbqO8+Pt7y8c6e/ZZcBWlIuOHPRVsw+hfdm5pgIegYQ0T4iTUwawTAsklcE72nob6PfZQSGlhcNzaLASS6Zg7n3lSF3qHkLDpCiZbEjNglcItVyqVrx2DdrObTIPDgt",
       type => "ssh-rsa" 
    }
    
    # Add to sudo
    class { 'sudo': }
    sudo::conf { 'cloudtopadmin':
        priority => 10,
        content => 'cloudtopadmin ALL=(ALL) NOPASSWD: ALL',
    }
 
    # Install upcentos repo
    package {'upcentos':
        ensure => present,
        source => "http://centosrepo.upd.edu.ph/CentOS/upcentos-0.1-1.el6.x86_64.rpm",
        provider => rpm,
    }

    # Base packages
    $basepackages = ['vim-enhanced','cronie','crontabs']

    # Install non-module packages

    package { $basepackages:
	ensure => installed,
    }

    # NTP
    class {'ntp':
        runmode => service,
        server => ["time.upd.edu.ph"],
    }

    
    # SNMP
    # Check tier
    case $ipaddress_eth0 {
        /10\.225\.1\.[0-9]{1,3}/: {
		$snmplocation = "Cloudtop T1"
		$snmpcommunity = "CLOUDTOPT1"
	}
 	 /10\.225\.2\.[0-9]{1,3}/: {
		$snmplocation = "Cloudtop T2"
		$snmpcommunity = "CLOUDTOPT2"
	}
	/10\.225\.3\.[0-9]{1,3}/: {
		$snmplocation = "Cloudtop T2"
		$snmpcommunity = "CLOUDTOPT2"
	}
    }
#    notify{'Giving snmp settings for $::ipaddress_eth0 located at $::snmplocation}':}
    
    class {'snmp':
        agentaddress => ['udp:161',],
        ro_community => $snmpcommunity,
        contact => 'Gerry Roxas <gerryroxas@outlook.com>',
        location => $snmplocation,
    }
    
    # RSYSLOG
    class {'rsyslog':
        firewall => true,
        firewall_tool => 'iptables',
        firewall_src => '10.225.1.200',
    }

    # SSH

    # IPTABLES
    iptables::rule {
	'ssh-gw':
		port => '22',
		protocol => 'tcp',
 		source => '10.225.1.202',
    }
    iptables::rule {
        'snmp':
            port => '161',
            protocol => 'udp',
            source => '10.225.1.201',
    }

    # TURN OFF UNNECESSARY SERVICES
    service { 'netfs':
        ensure => stopped,
    }
    service { 'portmap':
        ensure => stopped,
    }
    service { 'rpcbind':
        ensure => stopped,
    }
}
