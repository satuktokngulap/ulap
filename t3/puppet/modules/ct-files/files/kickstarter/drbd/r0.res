# This is the resource used for the shared GFS2 partition.
resource r0 {

	# This is the block device path.
	device /dev/drbd0;

	# We'll use the normal internal metadisk (takes about 32MB/TB)
	meta-disk internal;

	# This is the `uname -n` of the first node
	on sa.SITE_ID.cloudtop.ph {
		# The 'address' has to be the IP, not a hostname.
		# This is the # node's SN (bond1) IP. The port number must be unique among # resources.
		address MY_IP:7788;

		# This is the block device backing this resource on this node.
		disk /dev/sda5;
	}

	# Now the same information again for the second node.
	on sb.SITE_ID.cloudtop.ph {
		address MY_PEER:7788;
		disk /dev/sda5;
	}
}

