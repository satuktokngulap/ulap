node 'sb.104871.cloudtop.ph'
{
     #include 't3-base-initialize_disk'
     include 't3-base-install-prelim'
     #class {'t3-base-update-network':
     #   gateway => '10.225.3.1'
     #}
     class {'t3-base-configureT3':
        localIP => '10.225.3.132',
        peerIP => '10.225.3.131',
        localIPMI => '10.225.3.134',
        peerIPMI => '10.225.3.133',
        virtualIP => '10.225.3.135',
        hostname => 'sb.104871.cloudtop.ph'
     }
     class {'t3-base-drbd':}
     class {'t3-base-lvm':}
     class {'t3-base-2node-gfs':}

#Class['t3-base-initialize_disk']->
Class['t3-base-install-prelim']->Class['t3-base-configureT3']->Class['t3-base-drbd']->Class['t3-base-lvm']->Class['t3-base-2node-gfs']
}
