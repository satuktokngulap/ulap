import socket, time, shlex, sys, fcntl, struct, re, pprint
from subprocess import CalledProcessError, Popen, PIPE

class CommandCallException(Exception):
    pass

HOST = ''
SERVICE_PORT = 54545
SLEEP_TIME = 0.5
INTERFACE = "eth1"

def command_line_call_and_return(command_string, exit_on_error=True, suppress_warnings=True):
    command_list = shlex.split(command_string)

    try:
        if suppress_warnings:
            return Popen(command_list, stdout=PIPE, stderr=PIPE).communicate()
        else:
            return Popen(command_list, stdout=PIPE).communicate()[0]
    except CalledProcessError, details:

        err_msg = """\nERROR: Bash call from script failed!\n
        Bash command(s): %s\n
        DETAILS: 
        %s""" % (command_string, details)
        
        
        if(exit_on_error):
            logging.error(err_msg)
            sys.exit("Exited due to error")
        else:
            raise CommandCallException(err_msg)

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError as e:
        return None

def count_xrdp_connections(data_string):
    
    subnet=get_ip_address(INTERFACE).rpartition(".")[0]+"."
    xrdp_port=command_line_call_and_return("grep -m 1 '^port' /etc/xrdp/xrdp.ini")[0].partition("=")[2].rstrip()
    pattern_string = 'tcp[ 0-9]+%s[0-9]+:%s[ 0-9]+%s[0-9]+:[ 0-9]+ESTABLISHED[ 0-9/]+xrdp' % (subnet,xrdp_port,subnet)
    
    p = re.compile(pattern_string)
    matches = p.findall(data_string)
    #pprint.pprint(matches)
    return len(matches)

def parse_load():
    cli_cmd = "netstat -antlp"
    stdout, stderr = command_line_call_and_return(cli_cmd)
    
    cur_ses = count_xrdp_connections(stdout)
    max_ses = command_line_call_and_return("grep -m 1 '^MaxSessions=' /etc/xrdp/sesman.ini")[0].partition("=")[2].rstrip()
    return str(cur_ses)+"/"+max_ses

def start_listening():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, SERVICE_PORT))
    sock.listen(1)

    while True:
        conn, addr = sock.accept()
        #print 'Request from', addr
        conn.send(parse_load())
        conn.close()
        time.sleep(SLEEP_TIME)

start_listening()
