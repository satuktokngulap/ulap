# IPTABLES for T3 Baremetal
# Created; March 1, 2014
# Last Edited: March 3, 2014

# T3 iptables::rule using example42/iptables

class t3-iptables($localIP=undef,$peerIP=undef,$network_address=undef) {

  # Allow SSH
  iptables::rule { 'ssh':
    port        => '22',
    protocol    => 'tcp',
  }

  # Allow SNMP for Tier 1
  iptables::rule { 'snmp-t1':
    port        => '161:162',
    protocol    => 'udp',
    source      => '10.225.1.201'
  }


  # Allow SNMP for local
  iptables::rule { 'snmp-local':
    port        => '161:162',
    protocol    => 'udp',
    source      => $localIP,
  }

  # Allow SNMP for peer
  iptables::rule { 'snmp-peer':
    port        => '161:162',
    protocol    => 'udp',
    source      => $peerIP,
  }

  # Allow Puppet
  iptables::rule { 'puppet':
    port      => '8140',
    protocol  => 'tcp',
    source    => '10.225.1.215',
  }

  # Allow HTTPS
  iptables::rule { 'https':
    port     => '443',
    protocol => 'tcp',
  }

  # Allow nginx+munin
  iptables::rule { 'nginx+munin':
    port      => '8000',
    protocol  => 'tcp',
  }

  # Allow NFS - Portmap
  iptables::rule { 'NFS-Portmap-tcp':
    port      => '111',
    protocol  => 'tcp',
    source    => "${network_address}/24",
  }

  iptables::rule { 'NFS-Portmap-udp':
    port      => '111',
    protocol  => 'udp',
    source    => "${network_address}/24",
  }

  # Allow NFS - NFS
  iptables::rule { 'NFS-tcp':
    port      => '2049',
    protocol  => 'tcp',
    source    => "${network_address}/24",
  }

  iptables::rule { 'NFS-udp':
    port      => '2049',
    protocol  => 'udp',
    source    => "${network_address}/24",
  }

  # Allow NFS - MOUNTD
  iptables::rule { 'NFS-MOUNTD-tcp':
    port      => '892',
    protocol  => 'tcp',
    source    => "${network_address}/24",
  }

  iptables::rule { 'NFS-MOUNTD-udp':
    port      => '892',
    protocol  => 'udp',
    source    => "${network_address}/24",
  }

  # Allow NFS - STATUS
  iptables::rule { 'NFS-STATUS-tcp':
    port      => '662',
    protocol  => 'tcp',
    source    => "${network_address}/24",
  }

  iptables::rule { 'NFS-STATUS-udp':
    port      => '662',
    protocol  => 'udp',
    source    => "${network_address}/24",
  }

  # Allow NFS - Lock Manager
  iptables::rule { 'NFS-Lock-tcp':
    port      => '32803',
    protocol  => 'tcp',
    source    => "${network_address}/24",
  }

  iptables::rule { 'NFS-Lock-udp':
    port      => '32769',
    protocol  => 'udp',
    source    => "${network_address}/24",
  }

  # Allow NFS - RQUOTAD
  iptables::rule { 'NFS-RQUOTA-tcp':
    port      => '875',
    protocol  => 'tcp',
    source    => "${network_address}/24",
  }

  iptables::rule { 'NFS-RQUOTA-udp':
    port      => '875',
    protocol  => 'udp',
    source    => "${network_address}/24",
  }

  # Allow DRBD
  iptables::rule { 'DRBD':
    port      => '7788:7789',
    protocol  => 'tcp',
    source    => $peerIP,
  }

  # Allow CMAN
  iptables::rule { 'CMAN':
    port      => '5404:5405',
    protocol  => 'udp',
    source    => $peerIP,
  }

  # Allow RGManager
  iptables::rule { 'RGManager':
    port      => '49152:49215',
    protocol  => 'tcp',
    source    => $peerIP,
  }

  # Allow DLM
  # TODO: Check multiports if working

  iptables::rule { 'DLM':
    port      => '21064',
    protocol  => 'tcp',
    source    => $peerIP,
  }

  iptables::rule { 'modclusterd':
    port      => '16851',
    protocol  => 'tcp',
    source    => $peerIP,
  }

  iptables::rule { 'ricci':
    port      => '11111',
    protocol  => 'tcp',
    source    => $peerIP,
  }
}
