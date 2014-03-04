node 'sa.104871.cloudtop.ph'
{
#    include 'mcollective-node'
#    include 'ct-mcollective-agents'
#     include 't3-base-initialize_disk'
     include 't3-base-install-prelim'
#     class {'t3-base-update-network':
#        gateway => '10.225.3.1'
#     }
     class {'t3-base-configureT3':
        localIP => '10.225.3.81',
        peerIP => '10.225.3.82',
        localIPMI => '10.225.3.83',
        peerIPMI => '10.225.3.84',
        virtualIP => '10.225.3.85',
        hostname => 'sa.104871.cloudtop.ph'
     }
     class {'t3-base-drbd':}
     class {'t3-base-lvm':}
     class {'t3-base-2node-gfs':}

#Class['t3-base-initialize_disk']->
Class['t3-base-install-prelim']->Class['t3-base-configureT3']->Class['t3-base-drbd']->Class['t3-base-lvm']->Class['t3-base-2node-gfs']
}
