node 'sa.104871.cloudtop.ph'
{
#    include 'mcollective-node'
#    include 'ct-mcollective-agents'
     include 't3-base-install-prelim'
     class {'t3-base-update-network':
        gateway => '10.225.3.1'
     }
#     include 't3-base-initialize_disk'
     class {'t3-base-configureT3':
        localIP => '10.225.3.131',
        peerIP => '10.225.3.132',
        localIPMI => '10.225.3.133',
        peerIPMI => '10.225.3.134',
        virtualIP => '10.225.3.138',
        hostname => 'sa.104871.cloudtop.ph'
     }
     #class {'t3-base-drbd':}
     class {'t3-base-lvm':}

}
