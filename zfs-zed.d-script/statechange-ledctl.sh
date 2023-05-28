#!/bin/sh
#
# Turn off/on vdevs' enclosure fault LEDs when their pool's state changes.
# based on statechange-led.sh
#
# Exit codes:
#   0: enclosure led successfully set
#   1: enclosure leds not available
#   2: enclosure leds administratively disabled
#   3: The led sysfs path passed from ZFS does not exist
#   4: $ZPOOL not set
#   5: ledctl is not installed

[ -f "${ZED_ZEDLET_DIR}/zed.rc" ] && . "${ZED_ZEDLET_DIR}/zed.rc"
. "${ZED_ZEDLET_DIR}/zed-functions.sh"

if [ "${ZED_USE_ENCLOSURE_LEDS}" != "1" ] ; then
	exit 2
fi

zed_check_cmd "$ZPOOL" || exit 4
zed_check_cmd ledctl || exit 5

# Global used in set_led debug print
vdev=""

# set_led (dev, val)
#
# Set enclosure led on device
#
# Arguments
#   dev: blockdevice to set
#   val: value to set it to
#
# Return
#  0 on success, 3 on missing blockdevice path
#
set_led()
{
	dev="$1"
	val="$2"

	if [ -z "$val" ]; then
		return 0
	fi

	if [ ! -e "$dev" ] ; then
		return 3
	fi

	ledctl $val=$dev
}

# path_to_dev()
# 
# This function returns the full path to the parent device for a given
# blockdevice
#
path_to_dev()
{
	path=$1
	echo -n /dev/
	lsblk -no pkname $path
}

state_to_val()
{
	state="$1"
	case "$state" in
		FAULTED|DEGRADED|UNAVAIL)
			echo failure
			;;
		ONLINE)
			echo off
			;;
	esac
}

# process_pool (pool)
#
# Iterate through a pool and set the vdevs' enclosure slot LEDs to
# those vdevs' state.
#
# Arguments
#   pool:	Pool name.
#
# Return
#  0 on success, 3 on missing sysfs path
#
process_pool()
{
	pool="$1"

	# The output will be the vdevs only (from "grep '/dev/'"):
	#
	#    U45     ONLINE       0     0     0   /dev/sdk          0
	#    U46     ONLINE       0     0     0   /dev/sdm          0
	#    U47     ONLINE       0     0     0   /dev/sdn          0
	#    U50     ONLINE       0     0     0  /dev/sdbn          0
	#
	ZPOOL_SCRIPTS_AS_ROOT=1 $ZPOOL status -c upath,fault_led "$pool" | grep '/dev/' | (
	rc=0
	while read -r vdev state _ _ _ therest; do
		# Read out current LED value and path
		# Get dev name (like 'sda')
		dev=$(basename "$(echo "$therest" | awk '{print $(NF-1)}')")
#		vdev_enc_sysfs_path=$(realpath "/sys/class/block/$dev/device/enclosure_device"*)
#		if [ ! -d "$vdev_enc_sysfs_path" ] ; then
#			# This is not a JBOD disk, but it could be a PCI NVMe drive
#			vdev_enc_sysfs_path=$(nvme_dev_to_slot "$dev")
#		fi

#		current_val=$(echo "$therest" | awk '{print $NF}')

#		if [ "$current_val" != "0" ] ; then
#			current_val=1
#		fi

#		if [ -z "$vdev_enc_sysfs_path" ] ; then
#			# Skip anything with no sysfs LED entries
#			continue
#		fi

#		led_path=$(path_to_led "$vdev_enc_sysfs_path")
#		if [ ! -e "$led_path" ] ; then
#			rc=3
#			zed_log_msg "vdev $vdev '$led_path' doesn't exist"
#			continue
#		fi

		val=$(state_to_val "$state")

#		if [ "$current_val" = "$val" ] ; then
#			# LED is already set correctly
#			continue
#		fi

		if ! set_led "$dev" "$val"; then
			rc=3
		fi
	done
	exit "$rc"; )
}

if [ -n "$ZEVENT_VDEV_PATH" ] && [ -n "$ZEVENT_VDEV_STATE_STR" ] ; then
	# Got a statechange for an individual vdev
	val=$(state_to_val "$ZEVENT_VDEV_STATE_STR")
	vdev=$(path_to_dev "$ZEVENT_VDEV_PATH")
	set_led "$vdev" "$val"
else
	# Process the entire pool
	poolname=$(zed_guid_to_pool "$ZEVENT_POOL_GUID")
	process_pool "$poolname"
fi
