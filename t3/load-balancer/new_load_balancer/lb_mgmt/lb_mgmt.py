import socket, random, time, logging
from time import gmtime, strftime
from socket import error as SocketError
from utils import LoadException
HOST = ''
SERVICE_PORT    = 54545
RDP_A           = "rdpa.tc.net"
RDP_B           = "rdpb.tc.net"
#MAX_RETRIES     = 90
MAX_RETRIES     = 6
MAX_FIN_RETRIES = 12
RETRY_INTERVAL  = 5
SERVER_TIMEOUT  = 9
LAST_SERVER     = ""
SLEEP_TIME      = 1
FIN_SLEEP_TIME  = 5
LOGGING         = True
logging.basicConfig(filename='/opt/lb_mgmt/logs/lb_mgmt.log',level=logging.DEBUG)

def log(msg):
    if LOGGING:
        print "[LB MGMT]: "+str(msg)
        logging.info("["+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"]: "+str(msg))

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

def get_lb_server_data(lb_server_hostname, client_ip):
    SERVICE_PORT = 54546
    for i in range(int(MAX_RETRIES)):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SERVER_TIMEOUT)
            sock.connect((lb_server_hostname,SERVICE_PORT))
            
            command = "INQ %s" % client_ip
            sock.send(command)
            reply_data = sock.recv(1024)
            sock.close()
            data_list = []
            for data in reply_data.split("/"):
                data_list.append(int(data))
            return data_list
            
        except socket.timeout:
            time.sleep(RETRY_INTERVAL)
            
        except socket.error:
            time.sleep(RETRY_INTERVAL)
    
    return None

def load_balance(client_ip):
    """
        Returns the preferred RDP VM to connect to
    """
    log("Handling connection from [%s]" % client_ip)
    
    #Get load
    data_rdpa = get_lb_server_data(RDP_A, client_ip)
    data_rdpb = get_lb_server_data(RDP_B, client_ip)
    
    if (data_rdpa is None) and (data_rdpb is None):
        raise LoadException("Can't retrieve load info from RDP VMs!")
    elif (data_rdpa is None) and (data_rdpb is not None):
        log("Cannot contact RDP_A, sending RDP_B[%s] to [%s]" % (RDP_B, client_ip))
        return "1OFF-"+RDP_B
    elif (data_rdpa is not None) and (data_rdpb is None):
        log("Cannot contact RDP_B, sending RDP_A[%s] to [%s]" % (RDP_A, client_ip))
        return "1OFF-"+RDP_A
    else:
        log("RDP_A load: "+str(data_rdpa))
        log("RDP_B load: "+str(data_rdpb))
        
        #Handle duplicate tcps
        dups_result = cmp_dups(data_rdpa[2], data_rdpb[2])
        if dups_result is not None:
            log("Duplicate TCP detected for [%s]" % client_ip)
            return "2ON-"+dups_result
        
        else:
            #Handle normal state (compare loads)
            load_rdpa = data_rdpa[0:2]
            load_rdpb = data_rdpb[0:2]
            return "2ON-"+cmp_load(load_rdpa, load_rdpb)

def cmp_dups(dups_rdpa, dups_rdpb):
    if (dups_rdpa is 0) and (dups_rdpb is 0):
        return None
    elif dups_rdpa > dups_rdpb:
        return RDP_A
    elif dups_rdpa < dups_rdpb:
        return RDP_B
    else:
        RDP_VMS = [RDP_A, RDP_B]
        return random.choice(RDP_VMS)
        
def cmp_load(load_rdpa, load_rdpb):
    cur_load_rdpa = int(load_rdpa[0])
    cur_load_rdpb = int(load_rdpb[0])
    if False:
        pass
    elif cur_load_rdpa < cur_load_rdpb:
        return RDP_A
    elif cur_load_rdpa > cur_load_rdpb:
        return RDP_B
    else:
        RDP_VMS = [RDP_A, RDP_B]
        #return RDP_A
        return random.choice(RDP_VMS)

def main():
    log("LB-MGMT Started!")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, SERVICE_PORT))
    sock.listen(1)
    
    connecting_tc_ip='NONE'
    fin_retries = 0

    # Accept the connection once (for starter)
    while True:
        conn, addr = sock.accept()
        client_ip, client_port = addr
        current_sleep_time=SLEEP_TIME

        # RECEIVE CLIENT DATA
        command = conn.recv(1024).rstrip()
        log("command received: %s from: %s" % (command, client_ip))

        # PROCESS DATA
        reply = 'EMP No command/data sent from'
        
        if command=='INQ':                    # The client requests the data
            
            if connecting_tc_ip == 'NONE':
                try:
                    reply = load_balance(client_ip)     # Return the stored data
                    log("Sending preferred server [%s] to client [%s]" % (reply, client_ip))
                    connecting_tc_ip = client_ip

                except LoadException as e:
                    reply = "ERROR"     # Return the stored data
                    log("Cannot contact RDP load balancers. Sending [%s] to client [%s]" % (reply, client_ip))
            else:
                reply = 'WAIT'
                log("TC [%s] is still trying to connect. Sending [%s] to client [%s]" % (connecting_tc_ip, reply, client_ip))
                time.sleep(FIN_SLEEP_TIME)

                fin_retries +=1
                if fin_retries >= MAX_FIN_RETRIES:
                    log("FIN from TC [%s] expired. Resetting lock..." % (connecting_tc_ip))
                    connecting_tc_ip = 'NONE'
                    fin_retries = 0
        elif command=='FIN':
            if client_ip == connecting_tc_ip:
                reply = 'ACK Same IP [%s]' % client_ip
            else:
                reply = 'ACK Different IP [%s / %s]' % (client_ip, connecting_tc_ip)
            connecting_tc_ip = 'NONE' 
            #time.sleep(FIN_SLEEP_TIME)
            current_sleep_time = FIN_SLEEP_TIME
        elif command=='CUR':
            reply = 'CUR %s' % connecting_tc_ip
        else:
            reply = 'UNK Unknown command sent [%s]' % command

        # SEND REPLY
        conn.send(reply)
        conn.close()
        time.sleep(current_sleep_time)
    
main()
