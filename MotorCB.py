import os
import datetime
import keyboard
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO  #installed as sudo-apt get install python3-dev python3-rpi.gpio
import smbus
from scd30_i2c import SCD30
from time import sleep
import time
import ADS1256
import numpy as np
import urllib.request as URL

os.system('clear')
GPIO.setmode(GPIO.BCM)  #GPIO numbering
#display = Adafruit_SSD1306.SSD1306_128_64(rst=None)
GPIO.setwarnings(False)
print("Setting Pins")
MPWM = 13  #Set PWM line to pin 12 on Raspi (GPIO 12/Pin 32 has hardware PWM)
LPWM = 23  # Set PWM to pin 23 on Raspi for LED lights
DIR = 16  #Set directional pin to 8 on Raspi
M2PWM = 19
#DIR2 = 16
PUMP1 = 22
PUMP2 = 10
FAN = 9
#HPIN = 26
SOLA1 = 27
SOLA2 = 18
SOLB1 = 17
SOLB2 = 15
SOLC1 = 14
SOLC2 = 4
HEAT = 8
sleep(0.5) 
print("Setting Default Duty/Freq")
MDUTY = 0  # Initial duty cycle set to 40%
PDUTY = 100  # Initial pump duty cycle set to 50%
LDUTY = 100  # LED Duty Cycle set to 100%
MFREQ = 1024  # PWM frequency 1024hz
LFREQ = 1024  # LED PWM Frequency 1024hz
PFREQ = 1024  # Pump PWM frequency 1024hz
p_initial = 1 #preset level for initial filling of chamber
p_preset = 1.3 #preset voltage level for water level sensor
preset = 1
sleep(0.5)
print("Setting GPIO as Outputs")
GPIO_initial_logic = (HEAT, MPWM, M2PWM, DIR, PUMP1, PUMP2, SOLA1, SOLA2, SOLB1, SOLB2, SOLC1, SOLC2, LPWM, FAN) #, SOLA1, SOLA2, SOLB1, SOLB2, SOLC1, SOLC2)
GPIO.setup(GPIO_initial_logic, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(MPWM, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(M2PWM, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(DIR, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(PUMP1, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(PUMP2, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(SOLA1, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(SOLA2, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(SOLB1, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(SOLB2, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(SOLC1, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(SOLC2, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(LPWM, GPIO.OUT)  # set motor PWM pin on Raspi as output
#GPIO.setup(FAN, GPIO.OUT)  # set motor PWM pin on Raspi as output

#GPIO.setup(HPIN, GPIO.IN)
sleep(0.5)
print("Setting All Pins to Low")
GPIO_initial_set = (HEAT, MPWM, M2PWM, DIR, PUMP1, PUMP2, SOLA1, SOLA2, SOLB1, SOLB2, SOLC1, SOLC2, LPWM, FAN)
GPIO.output(GPIO_initial_set, GPIO.LOW)

mstatus = 0  #status condition for updating PWM
lstatus = 0  #status condition for updating PWM
p1status = 0  #status condition for updating PWM
p2status = 0
fstatus = 0
sleep(0.5)
print("Setting PWMs")
pwmi = GPIO.PWM(MPWM, MFREQ)  # Assign PWM and FREQ (channel + Freq) values to pwmi function variable
pwms = GPIO.PWM(LPWM, LFREQ)  #Assign PWM and FREQ values to pwms (lights) function variable
pwmp1 = GPIO.PWM(PUMP1, LFREQ)
pwmp2 = GPIO.PWM(PUMP2, LFREQ)
i=1  #true false variable for program exit
sleep(0.5)

print("Pin Settings Complete \n")
sleep(0.5)
print("Setting I2C Devices")
try:
	scd30 = SCD30()
	scd30.set_measurement_interval(2)
	scd30.start_periodic_measurement()
except:
	print("SCD30 Error")
try:
	ADC = ADS1256.ADS1256()
	ADC.ADS1256_init()
	#Initialize the display
	display.begin()
	display.clear()
	display.display()
	displayWidth = display.width
	displayHeight = display.height
	image = Image.new('1', (displayWidth, displayHeight))
	draw = ImageDraw.Draw(image)
	font = ImageFont.load_default()
	draw.text((0,0), "Initializing...", font = font, fill = 255)
	display.image(image)
	display.display()
	sleep(2)
	display.clear()
	display.display()
	sleep(1)
	draw.rectangle((0,0,displayWidth,displayHeight), outline =0, fill=0) 
	draw.text((0,16), "Awaiting Input", font = font, fill = 255)
	display.image(image)
	display.display()
except:
	print("OLED Error")

print("Complete")

#Analog Water Level Sensor Adjustement#
a1_adj = -0.0115  #zero out water level sensing so 0 volts is completely dry
a2_adj = -0.0115
a3_adj = -0.01
o_2 = str("NA")

def main_menu():
	global i
	print("""
	------------------------------------------------
	 Enter '1' to access motor controls \n 
	 Enter '2' to access light controls \n 
	 Enter '3' to access fan control \n
	 Enter '4' to access sensor data \n
	 Enter '5' to access pump control \n 
	 Enter '6' to access monitor mode (Press CTRL+C to Exit mode)\n
	 Enter '7' to enter automation\n
	 Enter '8' to exit program\n
	 Enter '0' at any point to return to main menu\n
	------------------------------------------------""")
	uinput = int(input("Please enter command: "))
	if uinput == 1:
		motor_menu()
	elif uinput == 2:
		lite_menu()
	elif uinput == 3:
		fan_menu()
	elif uinput == 4:
		sense_menu()
	elif uinput == 5:
		pump_menu()
	elif uinput == 6:
		monitor_mode()
	elif uinput == 7:
		auto()
		#rpm()
	elif uinput == 8:
		i = 0
	elif uinput == 9:
		image()
	elif uinput == 0:
		print("\n This is the main menu!! \n")
	else:
		print("Unknown Command")

def motor_menu():
	global MDUTY
	global MFREQ
	global mstatus
	print("-----------------------------\n"
		"Press 1 to Change PWM Duty Cycle\n"
		"Press 2 to Change PWM Frequency \n"
		"Press 3 to Activate Motor (Current Settings= " + str(MDUTY) + " %" + " & " + str(MFREQ) + "Hz \n"
		"Enter 4 to Deactivate Motor (Current Setting= " + str(MDUTY) + " %" + " & " + str(MFREQ) + "HZ)\n"
		"Enter 5 to Ramp Motor\n"
		"Enter 0 to return to Main Menu\n")
	minput = int(input("Please enter command: "))
	if minput == 1:
		try:
			new_pwm = int(input("Please enter a new PWM Duty Cycle (0-100): \n"))
			if new_pwm > 100:
				print("Unacceptable High Value")
				motor_menu()
			elif new_pwm < 0:
				print("Unacceptable Low Value")
				motor_menu()
			elif 100 >= new_pwm >=0:
				MDUTY = new_pwm
				print("New Value Assigned: " + str(MDUTY) + "% \n")
				if mstatus == 1:
					pwmi.start(MDUTY)
					print("Duty Cycle Updated")
					sleep(0.5)
				else: 
					motor_menu()
			else:
				print("Unacceptable Input")
		except:
			print("Unknown Try/Except Error")
	elif minput == 2:
		try:
			new_freq = int(input("Please enter a new PWM Frequency (10-8000): \n"))
			if new_freq > 20000:
				print("Unacceptable High Value")
				motor_menu()
			elif new_freq < 10:
				print("Unacceptable Low Value")
				motor_menu()
			elif 20000>= new_freq >= 10:
				MFREQ = new_freq
				print("New Value Assigned: " + str(MFREQ) + "Hz \n")
				motor_menu()
		except:
			print("Unknown Try/Except Error")
	elif minput == 3:
		try:
			RPWM = MDUTY
			print("Max PWM: " + str(RPWM) + "% \n")
			sleep(0.5)
			RPWMM = (RPWM * 10)
			GPIO.output(DIR, GPIO.HIGH)
			for r in range(RPWMM):
				RPWMD = r / 10
				pwmi.start(RPWMD)
				print("Duty Cycle= " + '{:.2f}'.format(RPWMD))
				sleep(0.05)
			mstatus = 1
			sleep(0.5)
			print("\n---------Motor at Full Speed----------- \n")
			sleep(0.5)
		except:
			print("Motor Exception Error")
	elif minput == 4:
		try:
			RPWM = MDUTY
			RPWMM = (RPWM * 10)
			for d in range(RPWMM):
				DPWMD = float(RPWM)-(d/10)
				pwmi.start(DPWMD)
				print("Duty Cycle= " + '{:.2f}'.format(DPWMD))
				sleep(0.05)
			GPIO.output(DIR, GPIO.LOW)
			pwmi.start(0)
			mstatus = 0
			sleep(0.5)
			print("\n---------Motor Deactivated---------- \n")
			sleep(0.5)
			motor_menu()
		except:
			print("Motor Exception Error")
	elif minput == 5:
		try:
			m_ramp()
			motor_menu()
		except:
			print("Motor Exception Error")
	elif minput == 0:
		try:
			main_menu()
		except:
			print("Motor Exception Error")

def lite_menu():
	global LDUTY
	global LFREQ
	global lstatus
	print("""----------------------\n
Enter 1 to adjust light PWM\n
Enter 2 to change light FREQ \n
Enter 3 to turn on lights\n
Enter 4 to turn off lights\n
Enter 0 to return to Main Menu\n""")
	linput = int(input("Please enter command: " ))
	if linput == 1:
		try:
			new_lpwm = int(input("\nAdjust Lighting Duty Cycle (0-100: 0 to turn off, 100 full brightness)\n" + "Current Setting: " + str(LDUTY) + "\n"+ "New Setting: "))
			if new_lpwm > 100:
				print("Unacceptable High Value")
				lite_menu()
			elif new_lpwm < 0:
				print("Unacceptable Low Value")
				lite_menu()
			elif 100 >= new_lpwm >= 0:
				LDUTY = new_lpwm
				print("New Value Assigned: " + str(LDUTY) + "% \n")
				lite_menu()
				if lstatus == 1:
					pwms.start(LDUTY)
					print("Duty Cycle Updated")
					sleep(0.5)
					lite_menu()
				else:
					pass
			else:
				print("Unacceptable Input")
		except:
			print("Unknown Try/Except Error")
	elif linput == 2:
		try:
			new_lfreq = int(input("Please enter a new Light PWM Frequency (10-8000): \n" 
			+ "Current Setting: " + str(LFREQ) + "\nNew Setting: "))
			if new_lfreq > 8000:
				print("Unacceptable High Value")
				lite_menu()
			elif new_lfreq < 10:
				print("Unacceptable Low Value")
				lite_menu()
			elif 8000 >= new_lfreq >= 10:
				LFREQ = new_lfreq
				print("New Value Assigned: " + str(LFREQ) + "Hz \n")
				sleep(0.5)
				lite_menu()
		except:
			print("Unknown Try/Except Error")
	elif linput == 3:
		try:
			GPIO.output(LPWM, GPIO.HIGH)
			pwms.start(LDUTY)
			lstatus=1
			sleep(0.5)
			print("\nLights Activated\n")
			sleep(0.5)
			lite_menu()
		except:
			print("Unknown Try/Except Error")
	elif linput == 4:
		try:
			GPIO.output(LPWM, GPIO.LOW)
			pwms.start(0)
			lstatus=0
			sleep(0.5)
			print("\nLights Deactivated\n")
			lite_menu()
		except:
			print("Unknown Try/Except Error")
	elif linput == 0:
		try:
			main_menu()
		except:
			pass

def fan_menu():
	global fstatus
	finput=int(input("Enter 1 to activate fans. Enter 3 to turn off fans: "))
	if finput == 1:
		try:
			GPIO.output(FAN, GPIO.HIGH)
			sleep(0.5)
			print("Fans Activated")
			fstatus = 1
		except:
			print("Fan Exception")
	elif finput == 3:
		try:
			GPIO.output(FAN, GPIO.LOW)
			sleep(0.5)
			print("Fans Deactivated")
			fstatus = 0
		except:
			print("Fan Exception")
	else:
		pass

def m_ramp():
	global TPWM
	global RPWM
	print("-"*40)
	print("\nThis function will stop the motor, pause, and ramp up over a period of time to a specified PWM. "
		  "What is the maximum PWM duty cycle you wish to stop at?")
	rpwm_input = int(input("Max Duty Cycle: "))
	TPWM = int(input("How long would you like to hold this max speed?: "))
	sleep(1)
	try:
		new_rpwm = rpwm_input
		if new_rpwm > 100:
			print("Unacceptable High Value")
		elif new_rpwm < 0:
			print("Unacceptable Low Value")
		elif 100 >= new_rpwm >= 0:
			RPWM = new_rpwm
			print("Max PWM: " + str(RPWM) + "% \n")
			sleep(0.5)
			print("Stopping Motor")
			pwmi.start(0)
			sleep(5)
			print("Starting Ramp")
			sleep(1)
			RPWMM = (RPWM * 10)
			for r in range(RPWMM):
				RPWMD = r/10
				pwmi.start(RPWMD)
				print("Duty Cycle= " + '{:.2f}'.format(RPWMD))
				sleep(0.05)
			print("Holding...")
			sleep(TPWM)
			print("Ramping Down Motor")
			for d in range(RPWMM):
				DPWMD = float(RPWM)-(d/10)
				pwmi.start(DPWMD)
				print("Duty Cycle= " + '{:.2f}'.format(DPWMD))
				sleep(0.05)
			pwmi.start(0)
			mstatus = 0
			sleep(5)
		else:
			print("unacceptable Input")
	except KeyboardInterrupt:
		pwmi.start(0)
		sleep(0.1)
	except:
		print("Unknown Try/Except Error")
def pump_menu():
	global p1status
	global p2status
	global PDUTY
	global p_preset
	GPIO_set_empty = [PUMP2, SOLB1, SOLB2] #Pins to activate to empty system
	GPIO_set_fill = [PUMP1, SOLA1, SOLA2] #Pins to activate to fill system
	pinput = int(input("""--------------------\n
	Enter 1 to adjust pump PWM\n
	Enter 2 to adjust pump PWM Frequency\n
	Enter 3 to activate Pump 1\n
	Enter 4 to activate Pump 2\n
	Enter 5 to deactivate Pump 1\n
	Enter 6 to deactivate Pump 2\n
	Enter 7 to fill to pre-set level\n
	Enter 8 to empty chamber\n
	Enter 0 to return to Main Menu\n"""))
	if pinput == 1:
		try:
			new_ppwm = int(input("\nAdjust PWM Duty Cycle (0-100)\n" + 
			 "Current Setting: " + str(PDUTY) + "\n" + "New Setting: "))
			if new_ppwm > 100:
				print("Unacceptable High Value")
				pump_menu()
			elif new_ppwm < 0:
				print("Unacceptable Low Value")
				pump_menu()
			elif 100 >= new_ppwm >= 0:
				PDUTY = new_ppwm
				print("New Value Assigned: " + str(PDUTY) + "% \n")
				if p1status == 1:
					pwmp1.start(PDUTY)
					print("Duty Cycle Updated")
					sleep(0.5)
					pump_menu()
				else:
					pump_menu()
			else:
				print("Unacceptable Input")
		except:
			print("Pump Exception")
	elif pinput == 2:
		try:
			new_pfreq = int(input("Please enter a new PWM Frequency (10-10000): \n"))
			if new_pfreq > 10000:
				print("Unacceptable High Value")
				pump_menu()
			elif new_pfreq < 10:
				print("Unacceptable Low Value")
				pump_menu()
			elif 10000 >= new_pfreq >= 10:
				PFREQ = new_pfreq
				print("New Value Assigned: " + str(PFREQ) + "Hz \n")
				pump_menu()
		except:
			print("Pump Exception")
	elif pinput == 3:
		try:
			GPIO.output(GPIO_set_fill, GPIO.HIGH)
			pwmp1.start(PDUTY)
			p1status = 1
			sleep(0.5)
			print("Filling Pump 1 Activated")
			pump_menu()
		except:
			print("Pump Exception")
	elif pinput == 4:
		try:
			GPIO.output(PUMP2, GPIO.HIGH)
			GPIO.output(SOLB1, GPIO.HIGH)
			GPIO.output(SOLB2, GPIO.HIGH)
			pwmp2.start(PDUTY)
			p2status = 1
			sleep(0.5)
			print("Empty Pump 2 Activated")
			pump_menu()
		except:
			print("Pump 2 Exception")
	elif pinput == 5:
		try:
			GPIO.output(GPIO_set_fill, GPIO.LOW)
			pwmp1.start(0)
			sleep(0.5)
			p1status = 0
			sleep(0.5)
			print("Filling Pump 1 Deactivated")
			pump_menu()
		except:
			print("Pump Exception")
	elif pinput == 6:
		try:
			GPIO.output(PUMP2, GPIO.LOW)
			pwmp2.start(0)
			GPIO.output(SOLB1, GPIO.LOW)
			GPIO.output(SOLB2, GPIO.LOW)
			sleep(0.5)
			p2status = 0
			sleep(0.5)
			print("Empty Pump 2 Deactivated")
			pump_menu()
		except:
			print("Pump Exception")
	elif pinput == 7:
		try:
			pump_fill(preset)
		except:
			print("Pump Filling Exception")
	elif pinput == 8:
		try:
			pump_empty(preset)
		except:
			print("Pump Empty Exception")
	elif pinput == 0:
		try:
			main_menu()
		except:
			pass

def sense_menu():
	global p1status
	global mstatus
	global lstatus
	global fstatus
	print("Finding I2C Devices:")
	bus = smbus.SMBus(1)
	for device in range(128):
		try:
			bus.read_byte(device)
			print(hex(device))
		except:
			pass
	sleep(1)
	print("Hardware Systems (1 is Active. 0 is Inactive)\n" + "-"*20)
	print("PUMP: " + str(p1status) + "\nMOTOR: " + str(mstatus) + "\nLIGHTS: " + str(lstatus)+ "\nFANS: " + str(fstatus))
	sleep(1)
	print("Taking Environmental Measurements")
	if scd30.get_data_ready():
		m = scd30.read_measurement()
		if m is not None:
			print(f"CO2: {m[0]:.2f}ppm, Temp: {m[1]:.2f}'C, RH: {m[2]:.2f}%")
	main_menu()

def monitor_mode():
	try:
		while True:
			os.system('clear')
			ctime = datetime.datetime.now()
			ADC_Value = ADC.ADS1256_GetAll()
			if ADC_Value is not None:
				print("-"*40)
				print("1 ADC Voltage = %1f"%(ADC_Value[1]*5.0/0x7fffff))
				print("2 ADC Voltage = %1f"%(ADC_Value[2]*5.0/0x7fffff))
				print("3 ADC Voltage = %1f"%(ADC_Value[3]*5.0/0x7fffff+a1_adj))
				print("4 ADC Voltage = %1f"%(ADC_Value[4]*5.0/0x7fffff+a2_adj))
			else:
				pass
			sleep(1.5)
			try:
				m = scd30.read_measurement()
				if m:
					print(f"CO2: {m[0]:.2f}ppm\nTemp: {m[1]:.2f}'C\nRH: {m[2]:.2f}%\nO2: "+ o_2)				
					print("Press CTRL+C to Exit Monitor Mode")
					print("Last Updated: " + str(ctime))
					print("-"*40)
					display.clear()
					display.display()
					draw.rectangle((0,0,displayWidth,displayHeight), outline=0, fill=0)
					draw.text((0, 0), "CO2: " + str(m[0]), font=font, fill=255)
					draw.text((0, 16), "Temp: " + str(m[1]), font = font, fill=255)
					draw.text((0, 32), "RH: " + str(m[2]), font = font, fill = 255)
					draw.text((0, 48), "O2: " + str(o_2), font = font, fill = 255)
					display.image(image)
					display.display()
				else:
					pass
				sleep(3.5)
			except:
				pass
	except KeyboardInterrupt:
		main_menu()
	except:
		print("Monitor Mode Error")
def rpm():
	print("Currently Disabled")
	#run_time = 30 #seconds
	#i = 0
	#HPIN_status = False
	#start = time.time()
	#while (time.time()-start) < run_time:
	#	if GPIO.input(HPIN) == True and HPIN_status == False:
	#		i += 1
	#		HPIN_status = True
	#		print(i)
	#	elif GPIO.input(HPIN) == False:
	#		HPIN_status = False
	#		pass
	#	else:
	#		pass
	#rpm_reading = (i/run_time) * 60
	#print(rpm_reading)

def pump_fill(preset):
	global p_preset
	global p_avg
	try:
		fill_status = True
		while fill_status:
			p_array = []
			for i in range(3):
				ADC_Value_3 = ADC.ADS1256_GetChannalValue(3)
				p = float(ADC_Value_3 * 5.0 / 0x7fffff + a1_adj)
				p_array.append(p)
				print("Getting Data Points")
				print(p)
				sleep(3)
			p_avg = np.sum((p_array)/3)
			print("Average: ", p_avg)
			p_diff = float(p_array[0] - p_array[2])
			print("Difference: ", p_diff)
			GPIO_set_fill = (PUMP1, SOLA1, SOLA2) #Pins to activate to fill system
			if p_avg < preset and abs(p_diff) < 0.05:
				GPIO.output(GPIO_set_fill, GPIO.HIGH)
				pwmp1.start(PDUTY)
				p1status = 1
				print("Filling...\n")
				sleep(3)
				GPIO.output(GPIO_set_fill, GPIO.LOW)
				pwmp1.start(0)
			elif p_avg >= preset and abs(p_diff) < 0.05:
				GPIO.output(GPIO_set_fill, GPIO.LOW)
				pwmp1.start(0)
				p1status = 0
				print("Water Level Reached\n")
				fill_status = False
	except KeyboardInterrupt:
		pump_menu()

def pump_empty(preset):
	global p_preset
	global p_avg
	try:
		empty_status = True
		GPIO_set_empty = [PUMP2, SOLC1, SOLC2] #Pins to empty pump
		while empty_status:
			p_array = []
			for i in range(3):
				ADC_Value_3 = ADC.ADS1256_GetChannalValue(3)
				p = float(ADC_Value_3 * 5.0 / 0x7fffff + a1_adj)
				p_array.append(p)
				print("Getting Data Point: ", p)
				sleep(3)
			p_avg = np.sum(p_array)/3
			print("Average: ", p_avg)
			p_diff = float(p_array[0] - p_array[2])
			print("Difference: ", p_diff)
			if p_avg > preset and abs(p_diff) < 0.05:
				GPIO.output(GPIO_set_empty, GPIO.HIGH)
				pwmp2.start(PDUTY)
				p2status = 1
				print("Emptying...\n")
				sleep(3)
				GPIO.output(GPIO_set_empty, GPIO.LOW)
				pwmp2.start(0)
			elif p_avg <= preset and abs(p_diff) < 0.05:
				p2status = 0
				print("Water Level Reaced\n")
				empty_status = False

	except KeyboardInterrupt:
		pump_menu()

def light_pulse(x): #x is number of times to pulse the light
	for i in range(x):
		GPIO.output(LPWM, GPIO.HIGH)
		pwms.start(LDUTY)
		sleep(0.2)
		GPIO.output(LPWM, GPIO.LOW)
		pwms.start(0)
		sleep(0.2)
		
	
def auto():
	start_time = datetime.time() #take the time to reference future automation
	try:
		ainput = input("This option will start the automation system. Enter 1 to start. 0 to go back. ")
		if ainput == 1:
			RPWM = MDUTY
			print("Max PWM: " + str(RPWM) + "% \n")
			sleep(0.5)
			RPWMM = (RPWM * 10)
			GPIO.output(DIR, GPIO.HIGH)
			for r in range(RPWMM):
				RPWMD = r / 10
				pwmi.start(RPWMD)
				print("Duty Cycle= " + '{:.2f}'.format(RPWMD))
				sleep(0.05)
			mstatus = 1
			sleep(0.5)
			print("\n---------Motor at Full Speed----------- \n")
			light_pulse(2)
			print("Waiting 10 seconds...")
			sleep(10)
			try:
				GPIO.output(FAN, GPIO.HIGH)
				sleep(0.5)
				print("Fans Activated")
				fstatus = 1
				light_pulse(3)
			except:
				print("Fan Exception")
			try:
				pump_fill(p_initial)
			except:
				print("Auto Pump Exception")
		elif ainput == 0:
			main_menu()
	except KeyboardInterrupt:
		pass
	except:
		print("Automation Exception Error")

#def image():
#	URL.urlretrieve("http://192.168.137.44/capture", "Images/%d.jpg", 
if __name__== '__main__':
	while i==1:
		try:
			main_menu()
#			os.system('clear')
		except KeyboardInterrupt:
			i=0
		except:
			print("Secondary Except Error")
	else:
		if mstatus == 1:
			for r in range(MDUTY):
				DDUTY = MDUTY - r
				pwmi.start(DDUTY)
				sleep(0.1)
				print(str(DDUTY))
		GPIO.output(LPWM, GPIO.LOW)
		GPIO.output(MPWM, GPIO.LOW)
		GPIO.output(FAN, GPIO.LOW)
		GPIO.output(PUMP1, GPIO.LOW)
		GPIO.output(PUMP2, GPIO.LOW)

