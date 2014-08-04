import socket, time, shlex, sys, fcntl, struct, re, os
from subprocess import CalledProcessError, Popen, PIPE
from ConfigParser import ConfigParser

###
#  EXCEPTIONS
###
    
class RDPException(Exception):
    """
        Parent exception class for load balancer
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

class CommandCallException(RDPException):
    """
        Thrown when an error is encountered from calling a shell command
    """
    pass

###
#   UTIL FUNCTIONS
###

def parse_config(path_to_config):
    """
        Parses the config.ini file
    """
    if check_file_exists(path_to_config):
        config = ConfigParser()
        config.read(path_to_config)
        return config
    else:
        err_msg = "Config file 'config.ini' not found in folder:\n   " + get_cwd()
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
    #"""
    #path = os.path.realpath(__file__)
    return path.rpartition("/")[0]+"/"

def check_file_exists(path_to_file):
    """
        Checks if file <path_to_file> exists
    """
    try:
        with open(path_to_file): pass
        return True
        
    except IOError:
        return False

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

        raise CommandCallException(err_msg)
        
class TcLoadBalancer:
    "Class for Thin Client Load Balancer"
    def __init__(self):
        """
            Initializes config variables from values inside config.ini file
        """
        CONFIG_PATH = get_cwd()+"config.ini"
        CONFIG      = parse_config(CONFIG_PATH)
        SETTINGS="settings"
        self.MGMT_VM_IP      = CONFIG.get(SETTINGS, "MGMT_VM_IP")
        self.MGMT_VM_PORT    = CONFIG.getint(SETTINGS, "MGMT_VM_PORT")
        self.XFREERDP_CMD    = CONFIG.get(SETTINGS, "XFREERDP_CMD")
        self.SLEEP_TIME      = CONFIG.getint(SETTINGS, "SLEEP_TIME")
        self.LOGGING         = CONFIG.getboolean(SETTINGS, "LOGGING")
        
    def log(self, msg):
        """
            Logs to standard output
        """
        if self.LOGGING:
            print "[LB TC]: "+str(msg)
            
    def get_loadbalanced_rdp_server(self):
        """
            Creates a connection to the Management Load Balancer and 
            sends an 'INQ' message inquiring for the load-balanced 
            RDP VM to connect to. Returns the IP address of the 
            load-balanced RDP VM."
        """
        command = "INQ"     #Request command to send to Management Load Balancer
        self.log("Sending inquiry to Management Load Balancer [%s]..." % self.MGMT_VM_IP)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.MGMT_VM_IP, self.MGMT_VM_PORT))
            sock.send(command+"\n")
            reply_data = sock.recv(1024).rstrip()
            sock.close()
            return reply_data

        except socket.timeout as e:
            self.log(str(e))
            raise LoadException("Cannot contact lb_mgmt")

        except socket.error as e:
            self.log(str(e))
            raise LoadException("Cannot contact lb_mgmt")
            
def main():
    tc_lb = TcLoadBalancer()
    tc_lb.log("LB-TC Started!")
    
    while True:
        try:
            # Send inquiry to Management VM and get response
            lb_mgmt_reply = tc_lb.get_loadbalanced_rdp_server()                         
            tc_lb.log(lb_mgmt_reply) 
        
            # Call command to xfreerdp client to initiate RDP connection to load-balanced RDP VM IP
            rdp_cmd = tc_lb.XFREERDP_CMD + " " + lb_mgmt_reply.split(" ")[1].rstrip()
            tc_lb.log("[DEBUG] CLI command: "+rdp_cmd)    
            cmd_result = cli_call(rdp_cmd)
            tc_lb.log(cmd_result)
            
        except LoadException as e:                                              # Output error if Management VM cannot be found
            tc_lb.log("[ERROR] "+str(e))
        
        except CommandCallException as e:                                       # Output error if call to shell command fails
            tc_lb.log("[ERROR] Error executing shell command!\n    "+str(e))

        except Exception as e:                                                  # Output other errors not expected
            tc_lb.log("[ERROR] Unexpected error!\n    "+str(e))

        tc_lb.log("[DEBUG] Sleeping for %i seconds before retrying" % tc_lb.SLEEP_TIME)    # Pause before retrying
        time.sleep(tc_lb.SLEEP_TIME)

main()

