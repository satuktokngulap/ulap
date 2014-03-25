import socket, time, shlex, sys, fcntl, struct, re
from subprocess import CalledProcessError, Popen, PIPE

SERVICE_PORT    = 54545
MGMT_VM         = "mgmt.tc.net"
MAX_RETRIES     = 90
RETRY_INTERVAL  = 1
SERVER_TIMEOUT  = 1000
LAST_SERVER     = ""
ERROR_PATTERN   = "Error"
#XFREERDP_CMD    = "xfreerdp --sec rdp -a 24 -z -f --plugin xrdpvr --plugin rdpsnd --plugin rdpdr --data disk:media:/media --"
XFREERDP_CMD    = "xfreerdp --sec rdp -a 24 -f --plugin xrdpvr --plugin rdpsnd --bcv3 jpeg --skip-bs "
INTERFACE       = "eth0"
LOGGING         = True
SLEEP_TIME      = 10

def log(msg):
    if LOGGING:
        print "[LB TC]: "+str(msg)

def command_line_call_and_return(command_string, exit_on_error=True, suppress_warnings=False):
    """
        Splices the command string and feeds it to subprocess.check_call(),
          which accepts a list
        It basically feeds the command line commands and execute them as they
          would on a terminal
        Use three doublequotes (\"\"") to feed commands as strings to avoid
          the need to escape single quotes or double quotes
        Returns the output of the command as a string
          instead of putting it in terminal
        If suppress_warnings is set to true, returns a tuple
          (stdout_output,stderr_output)
    """

    command_list = shlex.split(command_string)

    try:
        #return Popen(["pip","freeze","-E","env/"], stdout=PIPE).communicate()[0]
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
        log("Error retrieving IP address for interface [%s]!" % ifname)
        return None

def get_loadbalanced_rdp_server(lb_mgmt_hostname):
    return send_lb_cmd("INQ", lb_mgmt_hostname)

def send_fin_cmd(lb_mgmt_hostname):
    return send_lb_cmd("FIN", lb_mgmt_hostname)

def send_lb_cmd(command, lb_mgmt_hostname):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SERVER_TIMEOUT) 
            sock.connect((lb_mgmt_hostname,SERVICE_PORT))
            #command = "FIN"
            sock.send(command)
            reply_data = sock.recv(1024)
            sock.close()
            return reply_data

        except socket.timeout:
            log("Timeout from lb_mgmt. Retrying...")
            time.sleep(SLEEP_TIME)

        except socket.error:
            log("Error from lb_mgmt. Retrying...")
            time.sleep(SLEEP_TIME)


def main():
    log("LB-TC Started!")
    while True:
        lb_mgmt_reply = get_loadbalanced_rdp_server(MGMT_VM)
        log(lb_mgmt_reply) 
        if lb_mgmt_reply == "WAIT":
            log("Waiting...")
            time.sleep(SLEEP_TIME)

        elif lb_mgmt_reply == "ERROR":
            log("Error encountered by LB-MGMT! Retrying...")
            time.sleep(SLEEP_TIME)
        
        elif "2ON-" in lb_mgmt_reply:
            rdp_cmd = XFREERDP_CMD + lb_mgmt_reply.split("-")[1].rstrip()
            log(send_fin_cmd(MGMT_VM))    
            cmd_result = command_line_call_and_return(rdp_cmd)
            log(cmd_result)
            
        elif "1OFF-" in lb_mgmt_reply:
            rdp_cmd = XFREERDP_CMD + lb_mgmt_reply.split("-")[1].rstrip()
            log(send_fin_cmd(MGMT_VM))    
            cmd_result = command_line_call_and_return(rdp_cmd)
            log(cmd_result)
            
        else:
            #~ rdp_cmd = XFREERDP_CMD + lb_mgmt_reply
            #~ log(send_fin_cmd(MGMT_VM))    
            #~ cmd_result = command_line_call_and_return(rdp_cmd)
            #~ log(cmd_result)
            
            log("Unknown reply! Retrying...")
            time.sleep(SLEEP_TIME)
        

main()
