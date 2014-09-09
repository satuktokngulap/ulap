import socket, time, shlex, sys, fcntl, struct, re, pprint
from subprocess import CalledProcessError, Popen, PIPE

###
#  EXCEPTIONS
###
class RDPException(Exception):
    """
        Parent exception class for load balancer
    """
    pass

class CommandCallException(RDPException):
    """
        Thrown when an error is encountered from calling a shell command
    """
    pass

class ConfigNotFoundException(RDPException):
    """
        Thrown when config.ini file is not found
    """
    pass

class LoadException(RDPException):
    """
        Thrown when invalid load is received from RDP VM load balancer
    """
    pass

###
#  UTILS
###

def cli_call(cmd_str):
    """
        Executes the shell command <cmd_str> and returns the output,
        otherwise raises an error, if any is encountered.
    """
    cmd_list = shlex.split(cmd_str)

    try:
        return Popen(cmd_list, stdout=PIPE).communicate()[0]
    except CalledProcessError, details:
        err_msg = """\nERROR: Shell call from script failed!\n
        Shell command(s): %s\n
        Details:
            %s""" % (cmd_str, err_msg)

###
#  MAIN
###
class RdpLoadBalancer:
    "Class for RDP VM Load Balancer"
    def __init__(self):
        """
            Initializes config variables from values inside config.ini file
        """
        self.HOST = ''
        self.SERVICE_PORT = 54546
        self.SLEEP_TIME = 1
        self.INTERFACE = "eth1"
        self.LOGGING = True

    def log(self, msg):
        """
            Logs <msg> to standard output
        """
        if self.LOGGING:
            print "[LB SERVER]: "+msg

    def get_ip_address(self, ifname):
        """
            Returns the IP Address for interface <ifname>
            (currently set to 'eth1')
        """
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

    def parse_load(self, client_ip):
        """
            Parses and returns the current number of unique
            RDP TCP connections, the maximum allowed RDP connections
            from XRDP, and the number of duplicate RDP TCP connections
            derived from the source IP address of <client_ip>.
        """
        cli_cmd = "netstat -antlp"
        stdout = cli_call(cli_cmd)

        cur_ses, has_dup = self.count_xrdp_connections(stdout, client_ip)
        max_ses = cli_call("grep -m 1 '^MaxSessions=' /etc/xrdp/sesman.ini").partition("=")[2].rstrip()
        return str(cur_ses)+"/"+str(max_ses)+"/"+str(has_dup)

    def discount_dups(self, matches, client_ip):
        """
            Returns the unique RDP TCP connections from <matches>,
            and the number of duplicate RDP TCP connections matching <client_ip>
        """
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

    def count_xrdp_connections(self, data_string, client_ip):
        """
            Counts the number of unique RDP TCP connections and
            duplicates from <data_string> returned by the 'netstat' command.
        """
        #subnet=get_ip_address(self.INTERFACE).rpartition(".")[0]+"."
        ip_regex="\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        xrdp_port=cli_call("grep -m 1 '^port' /etc/xrdp/xrdp.ini").partition("=")[2].rstrip()
        pattern_string = 'tcp[ 0-9]+%s:%s[ 0-9]+%s:[ 0-9]+ESTABLISHED[ 0-9/]+xrdp' % (ip_regex,xrdp_port,ip_regex)

        p = re.compile(pattern_string)
        matches = p.findall(data_string)

        return self.discount_dups(matches, client_ip)

    def validate_ip(self, s):
        """
            Returns true if <s> is a valid IP address, false otherwise
        """
        a = s.split('.')

        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

def main():
    rdp_lb = RdpLoadBalancer()
    rdp_lb.log("LB-RDP Started!")

    # Initialize listener socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((rdp_lb.HOST, rdp_lb.SERVICE_PORT))
    sock.listen(1)

    # Accept the connection once (for starter)
    while True:
        conn, addr = sock.accept()

        # Receive connection from Management VM Load Balancer
        data = conn.recv(1024).rstrip()

        # Process message
        tokens = data.split(' ',1)            # Split by space at most once
        if len(tokens) > 1:
            command = tokens[0]
            reply = 'ERR No command/data sent\n'

            if command=='INQ':                      # Management VM requests for load data
                client_ip = tokens[1].rstrip()
                if rdp_lb.validate_ip(client_ip):   # Validate <client_ip> if proper IP Address
                    reply = rdp_lb.parse_load(client_ip)     # Reply with load and duplicates data

                else:
                    reply = 'ERR Invalid IP address argument: [%s]\n' % client_ip   # Otherwise, reply with error

            else:
                reply = 'ERR Unknown command sent [%s]\n' % data                    # Error reply for unhandled request

        else:
            reply = "ERR 'INQ' request needs an IP address argument. Command sent [%s]\n" % tokens[0] # Error reply for insufficient arguments

        # Send reply
        conn.send(reply+"\n")
        conn.close()
        # Pause before accepting new connections
        time.sleep(rdp_lb.SLEEP_TIME)

main()

