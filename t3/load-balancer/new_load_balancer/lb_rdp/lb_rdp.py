import socket, time, shlex, sys, fcntl, struct, re, pprint
from utils import command_line_call_and_return, check_file_exists, config_map, get_cwd, parse_config
from utils import RDPException, CommandCallException, ConfigNotFoundException, LoadException, ConnectException

HOST = ''
SERVICE_PORT = 54546
SLEEP_TIME = 5
INTERFACE = "eth1"
LOGGING=True

def log(msg):
    if LOGGING:
        print "[LB SERVER]: "+msg

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError as e:
        log("Error retrieving IP address for interface [%s]!" % ifname)
        return None

def parse_load(client_ip):
    cli_cmd = "netstat -antlp"
    stdout, stderr = command_line_call_and_return(cli_cmd, suppress_warnings=True)
    
    cur_ses, has_dup = count_xrdp_connections(stdout, client_ip)
    max_ses = command_line_call_and_return("grep -m 1 '^MaxSessions=' /etc/xrdp/sesman.ini").partition("=")[2].rstrip()
    return str(cur_ses)+"/"+str(max_ses)+"/"+str(has_dup)

def discount_dups(matches, client_ip):
    tc_ip_addresses = []
    has_dup=0
    for m in matches:
        #tc_ip = m.split()[4].split(':')[0]
        tc_ip = m.split()
        tc_ip = tc_ip[4].split(':')[0]
        if tc_ip not in tc_ip_addresses:
            tc_ip_addresses.append(tc_ip)
        if client_ip == tc_ip:
            has_dup += 1
    return len(tc_ip_addresses), has_dup

def count_xrdp_connections(data_string, client_ip):
    
    subnet=get_ip_address(INTERFACE).rpartition(".")[0]+"."
    #xrdp_port=command_line_call_and_return("grep -m 1 '^port' /etc/xrdp/xrdp.ini").partition("=")[2].rstrip()
    xrdp_port="3389"
    pattern_string = 'tcp[ 0-9]+%s[0-9]+:%s[ 0-9]+%s[0-9]+:[ 0-9]+ESTABLISHED[ 0-9/]+xrdp' % (subnet,xrdp_port,subnet)
    
    p = re.compile(pattern_string)
    matches = p.findall(data_string)
    
    return discount_dups(matches, client_ip)
        
def main():
    log("LB-RDP Started!")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, SERVICE_PORT))
    sock.listen(1)

    # Accept the connection once (for starter)
    while True:
        conn, addr = sock.accept()
        
        # RECEIVE CLIENT DATA
        data = conn.recv(1024)

        # PROCESS DATA
        tokens = data.split(' ',1)            # Split by space at most once
        command = tokens[0]                   # The first token is the command
        reply = 'ERR No command/data sent'
        
        if command=='INQ':                    # The client requests the data
            client_ip = tokens[1].rstrip()    # Get the data as second token
            reply = parse_load(client_ip)     # Return the stored data
        else:
            reply = 'ERR Unknown command sent [%s]' % data

        # SEND REPLY
        conn.send(reply)
        conn.close()
        time.sleep(SLEEP_TIME)
        
main()

