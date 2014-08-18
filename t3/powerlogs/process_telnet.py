import getpass, sys, telnetlib, time, shlex, io
from subprocess import CalledProcessError, Popen, PIPE
from time import gmtime, strftime

HOST = "switch.local"
PORT = 120
TELNET_TIMEOUT=60
LOG_FILE = "/var/log/power.log"
#LOG_FILE = "/home/ken/power_scripts/power.log"
RETRY_INTERVAL = 600 # upon error, retry after N seconds (600 secs = 5 mins)
#RETRY_INTERVAL = 5 # upon error, retry after N seconds
TRIM_TIME="00:00:00"

class RestartTelnetException(Exception): pass

def cli_call(command_string, exit_on_error=True, suppress_warnings=True):
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

def log_error(logfile, log_msg):
    print log_msg
    log_msg += "[%s]: %s" %(strftime("%Y-%m-%d %H:%M:%S", gmtime()) , log_msg)
    logfile.write(u'%s' % log_msg)
    time.sleep(RETRY_INTERVAL)

def log_telnet(logfile, log_msg):
    print log_msg
    logfile.write(u'%s' % log_msg)

with io.open(LOG_FILE, 'a') as logfile:
    while True:
        try:
            tn = telnetlib.Telnet(HOST, PORT, TELNET_TIMEOUT)
            while True:

                try:
                   log_line = tn.read_until("\n")
                   #print log_line.rstrip()
                   #logfile.write(str(log_line.replace('\r\n', '\n')))
                   log_telnet(logfile, str(log_line.replace('\r\n', '\n')))

                #Log if error occurs
                except Exception as e:
                    log_error(logfile, "ERROR: %s\n\n" % str(e))
                    try:
                        tn.close()
                    except:
                        pass
                    finally:
                        raise RestartTelnetException("Restarting telnet connection...")

        except RestartTelnetException as e:
            pass

        except Exception as e:
            log_line = "ERROR: %s\n\n" % str(e)
            log_error(logfile, log_line)
        
        time.sleep(1)

