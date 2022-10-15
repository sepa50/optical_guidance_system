import time
import sys

from pymavlink import mavutil

master = mavutil.mavlink_connection('/dev/ttyTHS1',115200)

master.wait_heartbeat()

print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))
#the_connection.mav.param_request_list_send(the_connection.target_system, the_connection.target_component)

#master.mav.param_request_list_send(master.target_system, master.target_component)

#master.param_fetch_all()

def request_message_interval(master, message_input, frequency_hz):

	message_name = "MAVLINK_MSG_ID_" + message_input

	message_id = getattr(mavutil.mavlink, message_name)

	master.mav.command_long_send(

		master.target_system, master.target_component,

		mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,

		message_id,

		1e6 / frequency_hz,
		0,

		0, 0, 0, 0)

   

	print("Requested the message successfully.")

   

def get_requested_data(master, message_name, dict_key):

	try:
		
		#message_index = 0

		dict1 = master.recv_match(type= message_name, blocking=True, timeout=0.1).to_dict()
		

		#dict_value = dict1[dict_key]

       
		#toWrite = "Message_Index, " + message_index + " :" + str(dict_value)
		print(dict1)

	except:

		pass

#request_message_interval(master, "VFR_HUD", 1)
#while True:
#    try:
#        get_requested_data(master, "VFR_HUD", 'alt', "m", save_name)
#   except:
#       pass
request_message_interval(master, "GLOBAL_POSITION_INT",10.0)
while True:	
	try:
		
		get_requested_data(master,'GLOBAL_POSITION_INT', 'lat')
	except:
		pass
		


#while True:
#	time.sleep(0.1)
#	try:
#		print("im doing nothing :(")
#		message = master.recv_match(type='PARAM_VALUES', blocking=True, timeout = 1).to_dict()
##			break
#	print(message)
#	except Exception as error:
#		print (error)
#		sys.exit(0)
