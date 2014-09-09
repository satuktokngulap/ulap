import re, pprint, sys, os, mmap, pprint, shlex
from subprocess import CalledProcessError, Popen, PIPE

class PowerParseException(Exception):
    pass

def cli_call(cmd_string, exit_on_error=True, suppress_warnings=False):
    cmd_list = shlex.split(cmd_string)

    try:
        #return Popen(["pip","freeze","-E","env/"], stdout=PIPE).communicate()[0]
        if suppress_warnings:
            return Popen(cmd_list, stdout=PIPE, stderr=PIPE).communicate()
        else:
            return Popen(cmd_list, stdout=PIPE).communicate()[0]
    except CalledProcessError, details:

        err_msg = """\nERROR: Bash call from script failed!\n
        Bash command(s): %s\n
        DETAILS: 
        %s""" % (cmd_string, details)
        
        
        if(exit_on_error):
            logging.error(err_msg)
            sys.exit("Exited due to error")
        else:
            raise CommandCallException(err_msg)


def parse_last_log(filepath="/var/log/power.log", cc=1, col_val=8):
    #print "KEYWORDS: [%i - %i]" %(cc, col_val)
    if cc<0 or cc>3:
        raise PowerParseException("Invalid Charge Controller ID: %s" % str(cc))
    
    pattern=u'^CC[ .\-0-9ABCDEF]+$\n^CC[ .\-0-9ABCDEF]+$\n^CC[ .\-0-9ABCDEF]+$\n^[ 0-9ABCDEF]+PDU[ 0-9ABCDEF]+$\n\n'
    #pattern="^CC[ .\-0-9ABCDEF]+$"
    
    #get last 10 lines of power.log
    tail_cmd = "tail -n 15 %s" % filepath
    
    data = cli_call(tail_cmd)

    if "ERROR" in data:
        raise PowerParseException("Error encountered while logging from switch!")
	
    #pprint.pprint(data)
    
    matches = re.findall(pattern, data, flags=re.MULTILINE)
    #pprint.pprint(matches)
    
    if len(matches) <=0:
        raise PowerParseException("Error reading log file [%s]" % filepath)
        
    last_log = matches[-1].split('\n')
    
    #~ #Print results
    #~ print "Number of complete logs: %i" % len(matches)
    #~ print "Last complete log:"
    #~ pprint.pprint(last_log)
    
    #Parse charge percentages
    if cc==0:
        cc1_charge = re.findall('[.a-zA-Z0-9]+',last_log[0])[col_val]
        cc2_charge = re.findall('[.a-zA-Z0-9]+',last_log[1])[col_val]
        cc3_charge = re.findall('[.a-zA-Z0-9]+',last_log[2])[col_val]
        return "%s %s %s" % (cc1_charge, cc2_charge, cc3_charge)
    elif cc==1:
        return re.findall('[.a-zA-Z0-9]+',last_log[0])[col_val]
    elif cc==2:
        return re.findall('[.a-zA-Z0-9]+',last_log[1])[col_val]
    elif cc==3:
        return re.findall('[.a-zA-Z0-9]+',last_log[2])[col_val]
    else:
        raise PowerParseException("Invalid Charge Controller ID: %s" % str(cc))

#filepath="/home/ken/Public/power.log"
#filepath="/home/ken/power_scripts/power.log"
#filepath="/var/log/power.log"

print parse_last_log(filepath=str(sys.argv[1]),cc=int(sys.argv[2]), col_val=int(sys.argv[3]))
#pprint.pprint(result)
#print "%s %s %s" %(result[0],result[1],result[2])
