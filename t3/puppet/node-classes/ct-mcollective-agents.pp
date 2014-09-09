class ct-mcollective-agents {
    file {'/root/mcollective/':
        ensure  => directory,
        mode    => '0750',
        owner   => root,
        group   => root,
    }

    # Remove old packages
#    exec {'remove-old-agents':
#        command => 'yum remove -y mcollective-backup-agent mcollective-backup-common mcollective-backup-app',
#        path    => ['/sbin', '/bin', '/usr/sbin', '/usr/bin'],
#        unless => 'rpm -qa | grep mcollective-backup-common-1.2-1.noarch',
#        }

    file {'/root/mcollective/mcollective-backup-agent-1.2-1.noarch.rpm':
        ensure  => file,
        mode    => '0750',
        owner   => root,
        group   => root,
        source  => 'puppet:///modules/ct-files/mcollective/mcollective-backup-agent-1.2-1.noarch.rpm',
        require => File['/root/mcollective/'],
    }

    file {'/root/mcollective/mcollective-backup-common-1.2-1.noarch.rpm':
        ensure  => file,
        mode    => '0750',
        owner   => root,
        group   => root,
        source  => 'puppet:///modules/ct-files/mcollective/mcollective-backup-common-1.2-1.noarch.rpm',
    }

    file {'/root/mcollective/mcollective-backup-app-1.2-1.noarch.rpm':
        ensure  => file,
        mode    => '0750',
        owner   => root,
        group   => root,
        source  => 'puppet:///modules/ct-files/mcollective/mcollective-backup-app-1.2-1.noarch.rpm',
    }

    file {'/root/mcollective/mcollective-backup-package-1.0-1.noarch.rpm':
        ensure  => file,
        mode    => '0750',
        owner   => root,
        group   => root,
        source  => 'puppet:///modules/ct-files/mcollective/mcollective-backup-package-1.0-1.noarch.rpm',
    }

    package {'mcollective-backup-agent':
        ensure      => absent,
        source      => '/root/mcollective/mcollective-backup-agent-1.2-1.noarch.rpm',
        provider    => rpm,
        notify      => Service['mcollective'],
        require     => File['/root/mcollective/mcollective-backup-agent-1.2-1.noarch.rpm'],
    }

    package {'mcollective-backup-common':
        ensure      => absent,
        source      => '/root/mcollective/mcollective-backup-common-1.2-1.noarch.rpm',
        provider    => rpm,
        notify      => Service['mcollective'],
        require     => File['/root/mcollective/mcollective-backup-common-1.2-1.noarch.rpm'],
    }

    package {'mcollective-backup-app':
        ensure      => absent,
        source      => '/root/mcollective/mcollective-backup-app-1.2-1.noarch.rpm',
        provider    => rpm,
        notify      => Service['mcollective'],
        require     => [File['/root/mcollective/mcollective-backup-app-1.2-1.noarch.rpm'],],
    }

    package {'mcollective-backup-package':
        ensure      => installed,
        source      => '/root/mcollective/mcollective-backup-package-1.0-1.noarch.rpm',
        provider    => rpm,
        notify      => Service['mcollective'],
        require     => File['/root/mcollective/mcollective-backup-package-1.0-1.noarch.rpm'],
    }

    Package['mcollective-backup-app'] -> Package['mcollective-backup-agent'] -> Package['mcollective-backup-common'] -> Package['mcollective-backup-package']
}