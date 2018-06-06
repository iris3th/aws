from Easy_Connection import AWSCommunications
import argparse
import time 
import boto3
import os
import sys
import paramiko
import re

# -------vars--------
timestr = time.strftime("%Y%m%d-%H%M%S")
SSH_PORT = '22'
SSH_KEY_FILENAME = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')


AWS = AWSCommunications()
parser = argparse.ArgumentParser(description='get inventory')
parser.add_argument('-c', '--customer', help='AWS customer name')
parser.add_argument('-u', '--username', help='Your AWS username')
args = parser.parse_args()

if args.customer is not None:
    customer = args.customer
    args.zone = "eu-west-1"
    USERNAME = args.username
    AWS.set_env_from_args(args.customer, args.zone)
else:
    parser.print_help(sys.stderr)
    sys.exit(1)
    AWS.set_env_from_db()

AWS.decrypt_customer()


# =========================================================================================== #

access_key = AWS.get_short_key()
secret_key = AWS.get_long_key()
region = AWS.get_region()


# ------------file to write the result to-----------------------------------
#orig_stdout = sys.stdout
#f = open('%s-%s.txt' % (customer,timestr), 'w') 
#sys.stdout = f


# ------------ssh----------------------

def sshConnect(address):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    try:
        client.connect(address, port=SSH_PORT, username=USERNAME,key_filename=SSH_KEY_FILENAME,timeout=10)
        stdin, stdout, stderr = client.exec_command("uptime|awk '{ print $3\" \"$4}'")
        return (re.compile(r'\x1b[^m]*m')).sub('', stdout.readline())
        client.close()
    except Exception as ex:
        print str(ex),


#--------------
client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

#---------------scanning running instances in every region-------------------
def hostsUP():
    up = 0
    for region in ec2_regions:
        conn = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                       region_name=region)
        instances = conn.instances.filter()
        for instance in instances:
         if instance.state["Name"] == "running":
              up=up+1
              instancename = ''
              for tag in instance.tags:
               if tag["Key"] == 'Name':
                instancename = tag["Value"]
                print "%s\t%s\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s" % (instance.state["Name"], 
        							  instance.private_ip_address,   
        							  instance.public_ip_address, 
        							  instance.instance_type, 
        							  region, 
        							  instancename, 
        							  instance.key_name, 
        							  instance.public_dns_name, 
        							  instance.image_id),
                print  sshConnect(instance.public_ip_address)
#---------------scanning stopped instances in every region-------------------
def hostsDown():
    down=0
    for region in ec2_regions:
        conn = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
	               region_name=region)
	instances = conn.instances.filter()
	for instance in instances:
 	 if instance.state["Name"] == "stopped":
	      down=down+1
	      instancename = ''
	      for tag in instance.tags:
	        if tag["Key"] == 'Name':
	            instancename = tag["Value"]
	      print "%s\t%s\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s" % (instance.state["Name"],
	    							  instance.private_ip_address, 
	    							  instance.public_ip_address, 
	    							  instance.instance_type, region, 
	    							  instancename,
	    							  instance.key_name, 
	    							  instance.public_dns_name, 
	    							  instance.image_id)
	     
#---------------
def ELBs():
    for region in ec2_regions:
        elbList = boto3.client('elb')
        conn = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,region_name=region)

        bals = elbList.describe_load_balancers()
        for elb in bals['LoadBalancerDescriptions']:
            print 'ELB DNS Name : ' + elb['DNSName']
	    for connId in elb['Instances']:
		running_instances = \
    			conn.instances.filter(Filters=[{'Name': 'instance-state-name'
	    	                              , 'Values': ['running']},
	    			              {'Name': 'instance-id',
	        			      'Values': [connId['InstanceId']]}])
    		for instance in running_instances:
    		    print("              Instance : " + instance.public_dns_name);
    



hostsUP()
#hostsDown()
#print "---stats--- \n---customer %s\n---hosts up %s down %s" % (customer, up, down)

#ELBs()

#sys.stdout = orig_stdout
#f.close()
