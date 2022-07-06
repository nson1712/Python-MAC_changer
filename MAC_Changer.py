
from cProfile import run
from operator import ge
import subprocess
import re
from turtle import update 
import winreg 
import codecs 

print("##############################################################")
print("1) Make sure you run this script with administrator privileges")
print("2) Make sure that the WiFi adapter is connected to a network")
print("##############################################################\n")

# If the MAC address change fails try setting the second character to 2 or 6 or A or E,
# for example: 0A1122334455 or 0A5544332211

mac_to_change_to = ["0A1122334455", "0E1122334455", "021122334455", "061122334455"]
#create an empty list to store all the MAC addresses
mac_addresses = list()
#Regex pattern of MAC addresses
macAddRegex = re.compile(r'([A-Za-z0-9]{2}[-:]){5}([A-Za-z0-9]{2})')
#Regex for transport name
transportName = re.compile("({.+})")
#Regex to pick out the adapter index
adapterIndex = re.compile("([0-9]+)")
# Use Python to run the getmac command, and then capture the output. 
# We split the output at the newline so that we can work with the individual lines 
getmac_output = subprocess.run("getmac", capture_output=True, shell = True).stdout.decode().split("\r\n")

#loop through the output
for macAdd in getmac_output:
    #regex find MAC addressed
    macFind = macAddRegex.search(macAdd)
    #find the transport name
    transportFind = transportName.search(macAdd)
    #if don't find the tranport name or MAC add, option wont be listed
    if macFind == None or transportFind == None:
        continue
    #append a tupple with the MAC add and Transport name to a list
    mac_addresses.append((macFind.group(0),transportFind.group(0)))
    

print("Which MAC address do you want to update?")
for index,item in enumerate(mac_addresses):
    print(f"{index} - Mac Address: {item[0]} - Transport Name: {item[1]}")

option = input("select the menu item number corresponding to the MAC that you want to change: ")

#create a menu
while True: 
    print("Which MAC Address do u want to use? This will change your Network card's MAC Address!")
    for index,item in enumerate(mac_to_change_to):
        print(f"{index} - MAC Address: {item}")

    update_option = input("Select the menu item number to the new MAC Address: ")
    #check 
    if (int(update_option) >= 0 and int(update_option) <len(mac_to_change_to)):
        print(f"Your MAC Address will be changed to: {mac_to_change_to[int(update_option)]}")
        break
    else:
        print("You didn't select a valid option. Pls try again!")

#append the folders where we'll search the values
controller_key_part = r"SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

#connect to HKEy_LOCAL_MACHINE registry
with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
    #create a list for 14 folder, transport value for you Mac Address should fall within this range
    controller_key_folder = [("\\000" + str(item) if item < 10 else "\\00" for item in range(10,15))]
    for key_folder in controller_key_folder:
        #try to open the key, if we can't just except and pass
        try:
            #specify the registry we connected to, the controller key
            with winreg.OpenKey(hkey, controller_key_part + key_folder, 0 , winreg.KEY_ALL_ACCESS) as regkey:
                #look at the values under each key and see if we can find "NetCfgInstanceId" with the same Transport Id as the one we selected
                try:
                    #values start at 0 in registry, we count through them
                    #continue until WindowsError(then just pass)
                    #start with the next folder until find the correct key
                    count = 0
                    while True: 
                        #unpack each individual winreg value to: name, value, type
                        name, value, type = winreg.EnumValue(regkey,count)
                        #count + 1 to go to the next value
                        count += 1
                        #check to see if "NetCfgInstanceId" is equal to Transport number for our selected MAC add
                        if name == "NetCfgInstancedId" and value == mac_addresses[int(option)[1]]:
                            new_mac_address = mac_to_change_to[int(update_option)]
                            winreg.SetValueEx(regkey, "Network Address", 0, winreg.REG_SZ, new_mac_address)
                            print("Successly matched Transport Number")
                            break
                        

                except WindowsError:
                    pass
        except:
            pass


run_disable_enable = input("Do you want to disable and reenable your wireless device(s)? Press Y or y to continue: ")

if run_disable_enable.lower() == 'y':
    run_last_part = True
else:
    run_last_part = False 

while run_last_part:
    #get a list of all network adapters. You have to ignore errors, as it doesn't like the format the command returns the data in
    network_adapter = subprocess.run(['vmic', 'nic', 'get', 'index,name'], capture_output=True, shell=True).stdout.decode(encoding='utf-8', errors = 'ignore').split('\r\r\n')
    for adapter in network_adapter:
        #get the index for each adapter
        adapter_index_find = adapterIndex.search(adapter.lstrip())
        #if there is an index and adapter has wireless in description we are going to disable and enable the adapter
        if (adapter_index_find and "Wireless" in adapter):
            disable = subprocess.run(['wmic', 'path', 'win32_networkadapter', 'where', f'index={adapter_index_find.group(0)}', 'call', 'disable'], capture_output=True, shell=True)
            #if the return code is 0 that we successfully disabled the adapter
            if (disable.returncode == 0):
                print(f"Disabled {adapter.lstrip()}")
            enable = subprocess.run(['wmic', 'path', 'win32_networkadapter', f'index={adapter_index_find.group(0)}', 'call', 'enable'], capture_output=True, shell=True)
            if (enable.returncode == 0):
                print(f"Enabled {adapter.lstrip()}")

    getmac_output = subprocess.run('getmac', capture_output=True, shell = True).stdout.decode()
    #Recreate the MAC address as not shows up in get mac XX-XX-XX-XX-XX-XX format from the 12 character string we have. We split the string into strings of length 2 using list comprehensions and then use "-".join(list) to create the address
    mac_add = "-".join([(mac_to_change_to[int(update_option)][i:i+2]) for i in range(0, len(mac_to_change_to[int(update_option)]), 2)])
    #Check if MAC addr we changed to is in getmac output, if so we have been successful
    if mac_add in getmac_output:
        print("MAC Address success")
        break 




        

        
        