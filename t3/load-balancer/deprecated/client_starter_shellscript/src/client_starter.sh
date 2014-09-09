#!/bin/bash
#$1 is username
#$2 is password

SERVICE_PORT=54545
RDP_A="rdpa.tc.net"
RDP_B="rdpb.tc.net"
MAX_RETRIES=90
RETRY_INTERVAL=1
#SERVER_TIMEOUT=1
SERVER_TIMEOUT=9
LAST_TRIED_SERVER=""
ERROR_PATTERN="Error"
XFREERDP_CMD="xfreerdp --sec rdp -a 24 -z -f --plugin xrdpvr --plugin rdpsnd --plugin rdpdr --data disk:media:/media --"
#XFREERDP_CMD="echo [DEBUG] xfreerdp --sec rdp -a 24 -z -f --plugin xrdpvr --plugin rdpsnd --plugin rdpdr --data disk:media:/media --"

function print_global_vars()
{
    echo "---===GLOBALS===---"
    echo $SERVICE_PORT
    echo $RDP_A
    echo $RDP_B
    echo $MAX_RETRIES
    echo $RETRY_INTERVAL
    echo $SERVER_TIMEOUT
    echo $LAST_TRIED_SERVER
}

function die() {
    #echo >&2 "$@"
    echo "$@"
    #read -p "Press [Enter] key to exit..."
    #exit 1
    return 1
}

function restart() {
    #echo >&2 "$@"
    echo "$@"
    #read -p "Press [Enter] key to restart"
}

function cmp_load()
{   #ARGS: server_a, load_a, server_b, load_b
    local server_a=$1
    local load_a=$2
    local server_b=$3
    local load_b=$4
    
    #echo "ARGS: $1, $2, $3, $4"
    
    local cur_ses_a=$(echo $load_a | cut -d'/' -f1)
    local max_ses_a=$(echo $load_a | cut -d'/' -f2)
    local cur_ses_b=$(echo $load_b | cut -d'/' -f1)
    local max_ses_b=$(echo $load_b | cut -d'/' -f2)
    
    #echo "ARGS: $cur_ses_a, $max_ses_a, $cur_ses_b, $max_ses_b"
    
    if [ ! -z $(echo $load_a | grep "none") ] || [ $cur_ses_a -ge $max_ses_a ]     #if full load or 'none' on a, refer to b
    then
        if [ ! -z $(echo $load_b | grep "none") ] || [ $cur_ses_b -ge $max_ses_b ]
        then
            echo ""
            LAST_TRIED_SERVER=""
            return
        else
            echo $server_b
        fi
    elif [ ! -z $(echo $load_b | grep "none") ] || [ $cur_ses_b -ge $max_ses_b ]   #if full load or 'none' on b, refer to a
    then
        if [ ! -z $(echo $load_a | grep "none") ] || [ $cur_ses_a -ge $max_ses_a ]
        then
            echo ""
            LAST_TRIED_SERVER=""
            return
        else
            echo $server_a
        fi
    else
        if [ $cur_ses_a -lt $cur_ses_b ]     #if a<b, refer to a
        then
            echo "$server_a $server_b"
        elif [ $cur_ses_b -lt $cur_ses_a ]     #if b<a, refer to b
        then
            echo "$server_b $server_a"
        else
            local rnum=$((RANDOM%2))            #if a=b, randomize
            if [ $rnum -eq 0 ]; then
                echo "$server_a $server_b"
            else
                echo "$server_b $server_a"
            fi            
        fi
    fi
}

function try_last_server()
{   #ARGS: server_a, load_a, server_b, load_b
    local server_a=$1
    local load_a=$2
    local server_b=$3
    local load_b=$4
    
    local cur_ses_a=$(echo $load_a | cut -d'/' -f1)
    local max_ses_a=$(echo $load_a | cut -d'/' -f2)
    local cur_ses_b=$(echo $load_b | cut -d'/' -f1)
    local max_ses_b=$(echo $load_b | cut -d'/' -f2)
    
    if [ ! -z $(echo $load_a | grep "none") ] || [ $cur_ses_a -ge $max_ses_a ]     #if full load or 'none' on a, refer to b
    then
        if [ ! -z $(echo $load_b | grep "none") ] || [ $cur_ses_b -ge $max_ses_b ]
        then
            echo ""
            LAST_TRIED_SERVER=""
            return
        else
            echo $server_b
        fi
    elif [ ! -z $(echo $load_b | grep "none") ] || [ $cur_ses_b -ge $max_ses_b ]   #if full load or 'none' on b, refer to a
    then
        if [ ! -z $(echo $load_a | grep "none") ] || [ $cur_ses_a -ge $max_ses_a ]
        then
            echo ""
            LAST_TRIED_SERVER=""
            return
        else
            echo $server_a
        fi
    else
        if [ ! -z $(echo $LAST_TRIED_SERVER | grep $server_a) ]     #if last tried is a, refer to a
        then
            echo "$server_a $server_b"
        elif [ ! -z $(echo $LAST_TRIED_SERVER | grep $server_b) ]     #if last tried is b, refer to b
        then
            echo "$server_b $server_a"
        else
            local rnum=$((RANDOM%2))            #otherwise, randomize
            if [ $rnum -eq 0 ]; then
                echo "$server_a $server_b"
            else
                echo "$server_b $server_a"
            fi            
        fi
    fi
}

function connect_to_rdp_server()
{   #rdp_server, username=None, password=None
    #echo "NUM ARGS: $#"
    case $# in
        1) # 1=server
            #xfreerdp -f $1
            #echo "$XFREERDP_CMD $1"
            echo $($XFREERDP_CMD $1)
            ;;
        2) # 1=server, username 
            #xfreerdp -f $1 -u $2
            #echo "$XFREERDP_CMD -u $2 $1"
            echo $($XFREERDP_CMD -u $2 $1)
            ;;
        3) # 2=server, username, password
            #xfreerdp -f $1 -u $2 -p $3
            #echo "$XFREERDP_CMD -u $2 -p $3 $1"
            echo $($XFREERDP_CMD -u $2 -p $3 $1)
            ;;
        *)
            die "  [ERROR] No server specified as first argument"
            ;;
    esac
}

function get_rdp_server_load()
{
    local rdp_server=$1
    local load
    
    for (( i=1; i<=$MAX_RETRIES; i++ )) #Try for max retries
    do
        load=$(nc -w $SERVER_TIMEOUT $rdp_server $SERVICE_PORT)
        [ ! -z $(echo $load | grep '[0-9]\/[0-9]') ] && break
        sleep $RETRY_INTERVAL
    done
    
    echo $load
}

function try_2_servers()
{
    local server_1=$1
    local server_2=$2
    local user=$3
    local pass=$4
    
    echo "  Trying server $server_1..."
    result=$(connect_to_rdp_server $server_1 $user $pass)
    echo "  [OUTPUT] $result"
    local errors=$(echo $result | grep $ERROR_PATTERN)
    
    if [ -z $errors ]; then
        echo "  [/] Finished with no connection errors..."
        LAST_TRIED_SERVER=$server_1
    else
        echo "  [ERROR] Some error from $server_1"
        echo "  Trying server $server_2..."
        result=$(connect_to_rdp_server $server_2 $user $pass)
        #LAST_TRIED_SERVER=$server_2
        [ -z $(echo $result | grep $ERROR_PATTERN) ] && LAST_TRIED_SERVER=$server_2
        echo "  [OUTPUT] $result"
    fi
}

function try_connecting_to_servers()
{
    local load_a
    local load_b
    
    echo "[!] Checking load of RDP VMs, please wait..."
    load_a=$(get_rdp_server_load $RDP_A)
    
    if [ ! -z $(echo $load_a | grep '[0-9]\/[0-9]') ] 
    then
        echo "  $RDP_A load: [$load_a]"
    else
        echo "  LOAD CHECK ERROR: got [$load_a] from $RDP_A!"
        load_a="none"
    fi
    
    load_b=$(get_rdp_server_load $RDP_B)
    
    if [ ! -z $(echo $load_b | grep '[0-9]\/[0-9]') ]
    then
        echo "  $RDP_B load: [$load_b]"
    else
        echo "  LOAD CHECK ERROR: got [$load_b] from $RDP_B!"
        load_b="none"
    fi
    
    if [ -z $(echo $load_a | grep '[0-9]\/[0-9]') ] && [ -z $(echo $load_b | grep '[0-9]\/[0-9]') ]
    then 
        die "  [ERROR] Failed to check load for both RDP servers: $RDP_A $RDP_B"
        return 1
    fi
    
    local server_1
    local server_2
    local server_sequence
    
    if [ -z $LAST_TRIED_SERVER ] #RDP isn't trying to reconnect to a server
    then
        #Compare loads
        echo "[!] Comparing server load values..."
        echo "  ARGS: [$RDP_A, $load_a, $RDP_B, $load_b]"
        server_sequence=$(cmp_load $RDP_A $load_a $RDP_B $load_b)
        
    else
        #Check last connected server
        echo "[!] Checking Last tried server: [$LAST_TRIED_SERVER]"
        echo "  ARGS: [$RDP_A, $load_a, $RDP_B, $load_b]"
        server_sequence=$(try_last_server $RDP_A $load_a $RDP_B $load_b)
        
    fi
    
    echo "  Server connection sequence: [$server_sequence]"
    server_1=$(echo $server_sequence | cut -d' ' -f1)
    server_2=$(echo $server_sequence | cut -d' ' -f2)
    
    echo "[!] Initiating RDP connection..."
    if [ -z $server_1 ] && [ -z $server_2 ] #No servers to try
    then
        die "  [ERROR] Connection Error: Servers are either full or unavailable! [$RDP_A:$load_a]  [$RDP_B:$load_b]"
        return 1
    elif [ ! -z $(echo $server_1 | grep $server_2) ] #Only one server to try
    then
        echo "  Trying server $server_1..."
        result=$(connect_to_rdp_server $server_1 $1 $2)
        #LAST_TRIED_SERVER=$server_1
        [ -z $(echo $result | grep $ERROR_PATTERN) ] && LAST_TRIED_SERVER=$server_1
        die "  [OUTPUT] $result"
        return 1
    fi
    
    try_2_servers $server_1 $server_2 $1 $2
}

#print_global_vars

while [ 0 ]
do 
    try_connecting_to_servers $1 $2
    echo ""
    restart "[~] Restarting script..."
done
