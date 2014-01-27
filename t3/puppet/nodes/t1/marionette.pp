node 'marionette' {
    service { 'puppet':
        ensure => running,
    }

    include 'mcomaster-node'
    include 'ct-mcollective-agents'
    
    # Add Admin Users
    add_user { ken:
      email => "kssalanio@gmail.com",
      uid => 502
    }
    add_ssh_key { ken:
      key => 'AAAAB3NzaC1yc2EAAAADAQABAAABAQCcgOkmmlOSXFlM83SQYwnVkR/qFV8j5Qx5winbzgQst24R7XiCMBYttnRBXJuqxLOYyOe/rSlmfL09H5LlLDk4WjRLCm+I6bvOHaopjN0zvke9TLCYvoEXbGa5MHuW6nj66m/y4bj4Z9Fh0az5agq23Ry3vOKdIk+8XyTTQzIPR3yk5BLJe9WIUEFJkKLWndTfhgIulRxW9EWMVmmZcjdm+a6SyzbuPdWNlyJwbv5j6dZ6r6n14btmQe7bg4FXYO6EAiY3Q74sIUWVmoZduM6hJ79FeVz2mLEcxnXvqqhxHU34+wznwO0vxFCIbjPRbChdg0vR+Zj6HMQhoLRu/NfV', 
      type => "ssh-rsa"
    }

    # Add to sudo
    class { 'sudo': }
    sudo::conf { 
        'ken':
        priority => 10,
        content => 'ken ALL=(ALL) NOPASSWD: ALL',
    } 
    sudo::conf { 
        'mac':
        priority => 10,
        content => 'mac ALL=(ALL) NOPASSWD: ALL',
    }
     
    
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
        'activemq-t3-sanroque':
                port => '61613',
                protocol => 'tcp',
                source => '10.18.221.0/24',
    }
    iptables::rule {
        'activemq-t3-tambubong':
                port => '61613',
                protocol => 'tcp',
                source => '10.19.28.0/25',
    }

    iptables::rule {
        'snmp':
            port => '161',
            protocol => 'udp',
            source => '10.225.1.201',
    }
    iptables::rule {
        'httpd':
            port => '80',
            protocol => 'tcp',
            source => '10.0.0.0/8',
    }
    iptables::rule {
        'redis':
            port => '6379',
            protocol => 'tcp',
            source => '10.0.0.0/8',
    }
}
