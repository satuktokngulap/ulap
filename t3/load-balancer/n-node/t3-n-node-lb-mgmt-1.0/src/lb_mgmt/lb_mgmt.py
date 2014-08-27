import socket, random, time, logging, os, operator, copy, math
from pprint import pprint
from time import gmtime, strftime
from socket import error as SocketError
from ConfigParser import ConfigParser

###
#  EXCEPTIONS
###
class RDPException(Exception):
    """Parent exception class for load balancer"""
    pass

class ConfigNotFoundException(RDPException):
    """Thrown when config.ini file is not found"""
    pass

class LoadException(RDPException):
    """Thrown when invalid load is received from RDP VM load balancer"""
    pass

###
#  Utility Functions
###
def check_file_exists(path_to_file):
    """
        Checks if file <path_to_file> exists
    """
    try:
        with open(path_to_file): pass
        return True
    except IOError:
        return False

def parse_config(path_to_config):
    """
        Parses the config.ini file
    """
    if check_file_exists(path_to_config):
        config = ConfigParser()
        config.read(path_to_config)
        return config
    else:
        err_msg = "Config file 'config.ini' not found in folder:\n[" + get_cwd() + "]"
        raise ConfigNotFoundException(err_msg)

def get_cwd():
    """
        Returns the current working directory of the python script
    """
    path = os.path.realpath(__file__)
    if "?" in path:
        return path.rpartition("?")[0].rpartition("/")[0]+"/"
    else:
        return path.rpartition("/")[0]+"/"

###
#  Load Balancer Class
###

class MgmtLoadBalancer:
    """Class for Management VM Load Balancer"""

    def __init__(self):
        """
            Initializes config variables from values inside config.ini file
        """
        # Initialize logging
        logging.basicConfig(filename=get_cwd()+'logs/lb_mgmt.log',level=logging.DEBUG)
        self.LOGGING = True

        # Parse config.ini
        self.CONFIG      = parse_config(get_cwd()+"config.ini")
        # Parse settings
        self.SETTINGS           = "settings"
        self.HOST               = self.CONFIG.get(self.SETTINGS, "HOST")
        self.MAX_CONNECTIONS    = self.CONFIG.getint(self.SETTINGS, "MAX_CONNECTIONS")
        self.MGMT_PORT          = self.CONFIG.getint(self.SETTINGS, "MGMT_PORT")
        self.RDP_PORT           = self.CONFIG.getint(self.SETTINGS, "RDP_PORT")
        self.SLEEP_TIME         = self.CONFIG.getint(self.SETTINGS, "SLEEP_TIME")
        self.RDP_TIMEOUT        = self.CONFIG.getint(self.SETTINGS, "RDP_TIMEOUT")
        self.RDP_MAX_RETRIES    = self.CONFIG.getint(self.SETTINGS, "RDP_MAX_RETRIES")
        self.RDP_RETRY_INTERVAL = self.CONFIG.getint(self.SETTINGS, "RDP_RETRY_INTERVAL")

    def log(self, msg):
        """
            Logs <msg> to lb_mgmt/logs/lb_mgmt.log
        """
        if self.LOGGING:
            print "[LB MGMT]: "+str(msg)
            logging.info("["+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"]: "+str(msg))

    def get_lb_rdp_data(self, client_ip, lb_rdp_host):
        """
            Retrieves the load and duplicate TCP data of <lb_rdp_host>
            with reference to the sending Thin Client IP address <client_ip>
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.RDP_TIMEOUT)
            sock.connect((lb_rdp_host, self.RDP_PORT))

            command = "INQ %s" % client_ip
            sock.send(command)
            reply_data = sock.recv(1024).rstrip()
            sock.close()
            data_list = []
            for data in reply_data.rstrip().split("/"):
                data_list.append(int(data))
            return data_list

        except ValueError:
            return None

        except socket.timeout:
            return None

        except socket.error:
            return None

    def valid_load(self, rdp_load):
        """
            Validates <rdp_load>
        """
        if rdp_load is not None:
            return True
        else:
            return False

    def get_rdp_loads(self, client_ip, rdp_vms=None):
        """
            "Retrieves the load and duplicate TCP data of RDP VMs listed
            in <rdp_vms> with reference to the sending Thin Client IP
            address <client_ip>. If <rdp_vms> is none, it retrieves
            the list of RDP VMs from the config file instead."
        """
        rdp_loads = []

        if rdp_vms is None:
            rdp_vms = self.get_rdp_vms()

        for rdp_name, rdp_ip in rdp_vms.items():
            #Filter empty loads
            load = self.get_lb_rdp_data(client_ip, rdp_ip)
            if self.valid_load(load):
                rdp_load_tuple = ( rdp_ip, load[0], load[1], load[2] )
                rdp_loads.append(rdp_load_tuple)
            else:
                self.log("WARNING: Invalid load from [%s]" % rdp_ip)

        return rdp_loads

    def find_most_dups(self, rdp_loads):
        """
            Finds the RDP VM IP address with the most number of
            duplicate TCP connections from <rdp_loads>
        """
        rdp_load =  max(rdp_loads, key=operator.itemgetter(3))
        if rdp_load[3] > 0:             #Evaluate if there are duplicates
            return rdp_load[0]
        else:
            return None

    def find_least_load(self, rdp_loads):
        """
            Finds the RDP VM IP address with the least number of
            RDP sessions from <rdp_loads>
        """
        rdp_load = min(rdp_loads, key=operator.itemgetter(1))
        if rdp_load[1] < rdp_load[2]:   #Evaluate if RDP load is less than its limit
            return rdp_load[0]
        else:
            return None

    def get_rdp_vms(self):
        """
            Returns the list of RDP VM IP adresses from the
            config.ini file
        """
        return dict(self.CONFIG.items('rdp_vms'))

    def log_load_data(self, client_ip, rdp_loads=None):
        """
            Logs the load data of the RDP VMs, and notes if the VM is
            offline. If <rdp_loads> is None, it retrieves the loads
            from the RDP VMs first.
        """
        rdp_vms = self.get_rdp_vms()

        if rdp_loads is None:
            rdp_load_values = self.get_rdp_loads(client_ip)
        else:
            rdp_load_values = copy.deepcopy(rdp_loads)

        rdp_on_list = [ data[0] for data in rdp_load_values ]

        for rdp_name, rdp_ip in rdp_vms.items():
            if rdp_ip not in rdp_on_list:
                rdp_load_values.append((rdp_ip,"OFFLINE"))

        self.log("[RDP VMS LOAD VALUES]")
        for rdp in rdp_load_values:
            self.log("    "+str(rdp))

        return rdp_load_values

    def load_balance(self, client_ip):
        """
            The main function of the MgmtLoadBalancer class. Returns
            the RDP VM chosen from load balancing using the load data
            retrieved from the RDP VMs.
        """
        #Retrieve load data from RDP VMs
        rdp_vms     = self.get_rdp_vms()
        rdp_loads   = self.get_rdp_loads(client_ip, rdp_vms)

        self.log_load_data(client_ip, rdp_loads)

        #No RDP load response
        if len(rdp_loads) is 0:
            raise LoadException("No RDP VMs online!")

        #Find duplicate TCP, find max
        chosen_rdp = self.find_most_dups(rdp_loads)
        if chosen_rdp is not None:
            self.log("[DUP_TCP]: duplicate TCP found at ["+str(chosen_rdp)+"]")
            return chosen_rdp

        #Find load < RDP limit, find min, retry until RDP_MAX_RETRIES
        i=0
        num_offline_vms = len(rdp_vms) - len(rdp_loads)
        self.log("[DEBUG]: Number of VMs offline: [%i] " % num_offline_vms )
        retry_count = self.RDP_MAX_RETRIES

        #Scale down retries to # of offline VMs
        if num_offline_vms != 0:
            retry_count = int(math.ceil(self.RDP_MAX_RETRIES/ num_offline_vms ))

        for i in range(retry_count):
            chosen_rdp  = self.find_least_load(rdp_loads)
            rdp_loads   = self.get_rdp_loads(client_ip, rdp_vms)
            if chosen_rdp is not None:
                return chosen_rdp
            time.sleep(self.RDP_RETRY_INTERVAL)

        self.log("[ERROR]: Finding minimum load failed. All available RDP VMs are full. Retries: ["+str(i)+"]")
        raise LoadException("All online RDP VMs are full!")

def main():
    mgmt_lb = MgmtLoadBalancer()
    mgmt_lb.log("LB-MGMT Started!")

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((mgmt_lb.HOST, mgmt_lb.MGMT_PORT))
    sock.listen(mgmt_lb.MAX_CONNECTIONS)

    # Start accepting connections
    while True:
        mgmt_lb.log("...Ready to accept a new connection...")
        conn, addr = sock.accept()
        client_ip, client_port = addr

        # Receive Thin Client Load Balancer connection
        command = conn.recv(1024).rstrip()
        mgmt_lb.log("Command [%s] received from: [%s]" % (command, client_ip))

        # Process connection data
        reply = 'EMP No command/data sent from'                 # Default response

        if command=='INQ':                                      # Thin client request command for load-balanced RDP VM IP
            try:
                reply = "REP %s" % str(mgmt_lb.load_balance(client_ip))     # Reply with load-balanced RDP VM IP to connect to
                mgmt_lb.log("Sending preferred server [%s] to client [%s]" % (reply, client_ip))

            except LoadException as e:                          # On error
                reply = "ERR " + str(e)                         # Send error message to client
                mgmt_lb.log("ERROR:" + str(e) + " Sending error reply to client [%s]" % client_ip)

        elif command=='LOD':                                    # Debug request command for load information
            try:
                rdp_load_values = mgmt_lb.log_load_data(client_ip)

                reply = "REP %s" % str(rdp_load_values)         # Reply with RDP VMs load data
                mgmt_lb.log("Sending preferred server [%s] to client [%s]" % (reply, client_ip))

            except LoadException as e:                          # On error
                reply = "ERR " + str(e)                         # Send error message to client
                mgmt_lb.log("ERROR:" + str(e) + " Sending error reply to client [%s]" % client_ip)

        else:
            reply = 'UNK Unknown command sent [%s]' % command   # Reply to unknown command
            mgmt_lb.log("Unknown command [%s] received from client [%s]" % (command, client_ip))

        # Send Reply
        conn.send(reply+"\n")                                   # Append newline before sending
        conn.close()

        # Sleep before accepting new connections
        mgmt_lb.log("[DEBUG]: Sleeping for " + str(mgmt_lb.SLEEP_TIME) + " seconds before processing others...")
        time.sleep(mgmt_lb.SLEEP_TIME)

main()

