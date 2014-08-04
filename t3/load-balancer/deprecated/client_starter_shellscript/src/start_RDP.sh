#!/bin/bash
#  Shortcut to starting client-side load-balancing script
#
#  Optional args:
#  $1: username
#  $2: username

PREFIX_DIR='/opt/rdpstarter'
[ "$#" -eq 2 ] && $PREFIX_DIR/client_starter.sh $1 $2
[ "$#" -eq 1 ] && $PREFIX_DIR/client_starter.sh $1
[ "$#" -eq 0 ] && $PREFIX_DIR/client_starter.sh
