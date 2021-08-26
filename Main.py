import json
from datetime import datetime
import pyeapi
import csv
from pandas import *


########## Overide the default behavior of pyeapi configuration file to check within the local folder #########

pyeapi.load_config('./.eapi.conf')

########## Defining header lists for information to be stored within the csv files under each category ########

device_names = ['Switch', 'Serial Number', 'Software', 'Free Mem', 'Total Mem', 'System Mac']
interface_names = ['Switch', 'Description', 'Bandwidth', 'VLANID', 'DUPLEX', 'INTF_TYPE','LINK STATUS']
arp_names = ['Switch', 'MAC', 'IP', 'Age']
lldp_names = ['Switch', 'Local Port', 'Remote Device', 'Remote Port']
mac_names = ["Switch","MAC ADDRESS", "INTERFACE", "TYPE", "VLAN"]

########## Defining output csv file names for each output category
csv_file = "Device.csv"
csv_file = "Interface.csv"
csv_file = "Arp.csv"
csv_file = "Lldp.csv"
csv_file = "mac.csv"

########## Create a dictionary that collects output from each category commands

Device_Audit = {}
Intf_Audit = {}
Arp_Audit = {}
Lldp_Audit = {}
mac_Audit = {}

########## Create a list to store each of the dictionary outputs from each of the category commands #########

Device_Store = []
Intf_Store = []
Arp_Store = []
Lldp_Store = []
mac_Store = []

########## Generating the nodes from a pre-defined csv file and storing them in a list - This is applicable for lots of devices #########

file = read_csv("devlist.csv")
Node_list = file['devices'].tolist()

########## For each of the nodes identified within the node list, pyeapi will connect and attempt the commands within the section #########
for node in Node_list:
    conn = pyeapi.connect_to(node)
    
    try:
        run = conn.running_config
        ver = conn.enable('show version')
        ver_txt = conn.enable('show version',encoding='text')
        intf_status = conn.enable('show interfaces status')
        intf_status_txt = conn.enable('show interfaces status',encoding='text')
        arp = conn.enable('show ip arp')
        arp_txt = conn.enable('show ip arp',encoding='text')
        lldp = conn.enable('show lldp neighbors')
        lldp_txt = conn.enable('show lldp neighbors',encoding='text')
        mac = conn.enable('show mac address-table')
        mac_txt = conn.enable('show mac address-table',encoding='text')
        port_channel = conn.enable('show port-channel summary')
        port_channel_txt = conn.enable('show port-channel summary',encoding='text')
                
    except:
        print("One of the commands on Device" + "  " + str(node) + " " + "has failed")
 
########## Store the outputs for the raw commands in objects that can be pulled out later ################# 
    ver_raw = ver_txt[0]['result']['output']
    intf_status_raw = intf_status_txt[0]['result']['output']
    arp_raw = arp_txt[0]['result']['output']
    lldp_raw = lldp_txt[0]['result']['output']
    mac_raw = mac_txt[0]['result']['output']
    port_channel_raw = port_channel_txt[0]['result']['output']
  
########## Write each of the section outputs into the text file ############################
    with open(node+'Output.txt', 'a') as f:
        f.write('\n ########## RUNNING CONFIGURATION OUTPUT ########################## \n ')
        f.write(str(run))
        f.write('\n ###########SHOW VERSION OUTPUT ###################### \n ')
        f.write(str(ver_raw))
        f.write('\n ##############SHOW INTERFACE STATUS OUTPUT ##########################\n')
        f.write(str(intf_status_raw))
        f.write('\n ##############SHOW IP ARP TABLE OUTPUT ############################# \n')
        f.write(str(arp_raw))
        f.write('\n ##############SHOW LLDP NEIGHBOR OUTPUT ############################# \n')
        f.write(str(lldp_raw))
        f.write('\n ##############SHOW MAC ADDRESS TABLE OUTPUT #############################\n ')
        f.write(str(mac_raw))
        f.write('\n ##############SHOW PORT CHANNEL SUMMARY OUTPUT #############################\n ')
        f.write(str(port_channel_raw))

##########  Extracting audit parameters from the Show version code run  ################# 

    serial_num = ver[0]['result']['serialNumber']
    software_image = ver[0]['result']['version']
    Free_Mem = ver[0]['result']['memFree']
    total_mem = ver[0]['result']['memTotal']
    system_mac = ver[0]['result']['systemMacAddress']
             
    Device_Audit = {"Switch": node,"Serial Number": serial_num, "Software": software_image, "Free Mem": Free_Mem,"Total Mem": total_mem, "System Mac": system_mac}
    Device_Store.append(Device_Audit) 

##########  Extracting audit parameters from the Show lldp Neighbor Code run  ################# 

    j = 0
    while j < len(lldp[0]['result']['lldpNeighbors']):
        j_port = lldp[0]['result']['lldpNeighbors'][j]['port']
        j_nei = lldp[0]['result']['lldpNeighbors'][j]['neighborDevice']
        j_neiport = lldp[0]['result']['lldpNeighbors'][j]['neighborPort']   
    
     
        Lldp_Audit = {"Switch": node,"Local Port": j_port, "Remote Device": j_nei, "Remote Port": j_neiport}
        Lldp_Store.append(Lldp_Audit)         
                
        j +=1
 
##########  Extracting audit parameters from the Show IP ARP Code run  ################# 
    
    n = 0
    while n < len(arp[0]['result']['ipV4Neighbors']):
        q_mac = arp[0]['result']['ipV4Neighbors'][n]['hwAddress']
        q_ip = arp[0]['result']['ipV4Neighbors'][n]['address']
        q_age = arp[0]['result']['ipV4Neighbors'][n]['age']

        Arp_Audit = {"Switch": node,"MAC": q_mac, "IP": q_ip, "Age": q_age}
        Arp_Store.append(Arp_Audit)
        n += 1

##########  Extracting audit parameters from the Show interfaces status Code run  ################# 
    
    for intf in intf_status[0]['result']['interfaceStatuses'].keys():
        if 'vlanId' in intf_status[0]['result']['interfaceStatuses'][intf]['vlanInformation']:
   
            desc = intf_status[0]['result']['interfaceStatuses'][intf]['description']
            bandwidth = intf_status[0]['result']['interfaceStatuses'][intf]['bandwidth']
            vlanid = intf_status[0]['result']['interfaceStatuses'][intf]['vlanInformation']['vlanId']
            duplex = intf_status[0]['result']['interfaceStatuses'][intf]['duplex']
            intf_type = intf_status[0]['result']['interfaceStatuses'][intf]['interfaceType']
            link_stats = intf_status[0]['result']['interfaceStatuses'][intf]['linkStatus']            
        elif 'interfaceMode' in intf_status[0]['result']['interfaceStatuses'][intf]['vlanInformation']:

            desc = intf_status[0]['result']['interfaceStatuses'][intf]['description']
            bandwidth = intf_status[0]['result']['interfaceStatuses'][intf]['bandwidth']
            vlanid = intf_status[0]['result']['interfaceStatuses'][intf]['vlanInformation']['interfaceMode']
            duplex = intf_status[0]['result']['interfaceStatuses'][intf]['duplex']
            intf_type = intf_status[0]['result']['interfaceStatuses'][intf]['interfaceType']
            link_stats = intf_status[0]['result']['interfaceStatuses'][intf]['linkStatus']            
        elif 'vlanExplanation' in intf_status[0]['result']['interfaceStatuses'][intf]['vlanInformation']:

            desc = intf_status[0]['result']['interfaceStatuses'][intf]['description']
            bandwidth = intf_status[0]['result']['interfaceStatuses'][intf]['bandwidth']
            vlanid = intf_status[0]['result']['interfaceStatuses'][intf]['vlanInformation']['vlanExplanation']
            duplex = intf_status[0]['result']['interfaceStatuses'][intf]['duplex']
            intf_type = intf_status[0]['result']['interfaceStatuses'][intf]['interfaceType']
            link_stats = intf_status[0]['result']['interfaceStatuses'][intf]['linkStatus']            

        Intf_Audit = {"Switch": node,"Description": desc, "Bandwidth": bandwidth, "VLANID": vlanid, "DUPLEX": duplex,"INTF_TYPE": intf_type,"LINK STATUS": link_stats}
        Intf_Store.append(Intf_Audit)

##########  Extracting audit parameters from the Show mac address Code run  #################     
    k = 0
    while k < len(mac[0]['result']['unicastTable']['tableEntries']):
        mac_add = mac[0]['result']['unicastTable']['tableEntries'][k]['macAddress']
        int_add = mac[0]['result']['unicastTable']['tableEntries'][k]['interface']
        k_type = mac[0]['result']['unicastTable']['tableEntries'][k]['entryType']
        k_vlan = mac[0]['result']['unicastTable']['tableEntries'][k]['vlanId']
            
        mac_Audit = {"Switch": node,"MAC ADDRESS": mac_add, "INTERFACE": int_add, "TYPE": k_type, "VLAN": k_vlan}
        mac_Store.append(mac_Audit)           
        k += 1
                            
##########  Writing the final lists of results into the various csv outputs  ################# 

with open('Device.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames= device_names)
    writer.writeheader()
    writer.writerows(Device_Store)

with open('Lldp.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames= lldp_names)
    writer.writeheader()
    writer.writerows(Lldp_Store)

with open('Arp.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames= arp_names)
    writer.writeheader()
    writer.writerows(Arp_Store)
    
with open('mac.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames= mac_names)
    writer.writeheader()
    writer.writerows(mac_Store)
    
with open('Interface.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames= interface_names)
    writer.writeheader()
    writer.writerows(Intf_Store)