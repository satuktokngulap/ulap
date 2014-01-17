IPADDR="addr:10.0.0.0"
HNAME=HELLO

HOSTENT=$(cat test | grep "${IPADDR#"addr:"} $HNAME")
echo $HOSTENT
