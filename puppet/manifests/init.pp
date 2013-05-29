class vdsmcodecoverage {
    package {"vdsmcodecoverage":
        ensure => present,
    }

    service {"vdsmcodecoveraged":
        require => Package["vdsmcodecoverage"],
        enable  => false,
    }

    file {"/etc/vdsmcodecoverage.conf":
        ensure => file,
        source => "puppet:///modules/vdsmcodecoverage/vdsmcodecoverage.conf",
    }

    file {"/var/lib/vdsmcodecoverage/coveragerc":
        ensure => file,
        source => "puppet:///modules/vdsmcodecoverage/coveragerc",
    }
}
