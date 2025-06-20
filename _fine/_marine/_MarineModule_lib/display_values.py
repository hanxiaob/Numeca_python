#                                                                             #
#                         Display computation information                     #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	  : 2012
#______________________________________________________________________________
#
# Description: Display computation information
#
# Changes:
#
# DATE        IMPLEMENTER         TYPE OF MODIFICATION
#01-02-2017   A. del Toro         #26123 correction
#______________________________________________________________________________

import os

import CFView as cfv

#check the number of bodies
def nbBody(project_name):
	end = 0
	if project_name.find("cgns") == -1:
		domain =  cfv.NumberOfDomains()
		if domain != 1 :
			cfv.CFViewWarning ("This plugin only works with 1 domain. ")
			end = 1
	return end

#read the position in Display_Input
def readPosition(Display_Input):
	value = Display_Input['Position']
	if value == "0":
		position = (-0.8,0.75)
	elif value == "1":
		position = (0,0.75)
	elif value == "2":
		position = (0.8,0.75)
	elif value == "3":
		position = (-0.8,-0.75)
	elif value == "4":
		position = (0,-0.75)
	else :
		position = (0.8,-0.75)
	return position
	
#read efforts in Display_Input
def readEfforts(iteration,Display_Input,path):
	displayEfforts = ''
	keywordEfforts = ['Fx','Fy','Fz','Mx','My','Mz','FxP','FyP','FzP','MxP','MyP','MzP','FxV','FyV','FzV','MxV','MyV','MzV']
	for key in keywordEfforts:
		if Display_Input[key] == '1':
			efforts_name = key
			try:
				g = open(os.path.join(path,"eff_" + efforts_name + ".dat"),'r')
				efforts_contents = g.readlines()
				g.close()
				efforts_value = (efforts_contents[12 + int(iteration)].split())[2]
				efforts_value = "%.3e" % float(efforts_value)
				displayEfforts = displayEfforts + '|' + efforts_name + ' = ' + efforts_value
			except IOError:
				displayEfforts = displayEfforts + '|' + efforts_name + ' = ' + 'file is missing'
				
	return displayEfforts

#read the motions in Display_Input
def readTimeMotions(iteration,Display_Input,mvt_file):
	g = open(mvt_file,"r")
	mvt_contents = g.readlines()
	g.close
	displayMotions = ""
	keywordMotions = ['Tx0','Ty0','Tz0','Rx2','Ry1','Rz0','Vx','Vy','Vz','Ax','Ay','Az']
	for key in keywordMotions:
		if Display_Input[key] == '1':
			motions_name = key
			if mvt_contents[4].find(motions_name) >= 0:
				column_list = (mvt_contents[4]).split()
				motions_position = column_list.index(motions_name) - 2
				motions_value = ((mvt_contents[7 + int(iteration)]).split())[motions_position]
				motions_value = "%.3e" % float(motions_value)
				displayMotions = displayMotions +"|" + motions_name + " = " + motions_value 
	time = ((mvt_contents[7 + int(iteration)]).split())[0]
	time = "%.3e" % float(time)
	displaytime = "t = " + time 
	return displaytime,displayMotions,time

#read the number of cells in Display_Input
def readNumberofcells(time,Display_Input,path):
	displayNb_cells = ''
	if int(float(Display_Input['Number of cells'])) > 0:
		try:
			g = open(os.path.join(path,'nb_cell.dat'),'r')
			nb_cells_contents = g.readlines()
			g.close
			nb_cells = ((nb_cells_contents[3]).split())[2]
			for line in nb_cells_contents[3:]:
				if (line.split())[2] != nb_cells:
					if float((line.split())[0]) <= float(time):
						nb_cells = (line.split())[2]
					else:
						break
			displayNb_cells = '|' + 'Nb cells = ' + str(nb_cells)
		except IOError:
			cfv.CFViewWarning('The file nb_cell.dat is missing, impossible to read values. ')
			displayNb_cells = '|' + 'Nb cells = ' + 'file is missing'
	return displayNb_cells	

#read the actuator disk data in Display_Input and *.std file
def readActuator(iteration,Display_Input,sim_file):
	displayActuator = ''
	std_file = sim_file[:-3] + 'std'
	if Display_Input['Thrust'] == '1' or Display_Input['Torque'] == '1':
		try:
			f = open(std_file,'r')
			std_contents = f.readlines()
			f.close()
			g = open(sim_file,'r')
			sim_contents = g.readlines()
			g.close()
			nbActuatorDisk = int(sim_contents[2 + sim_contents.index('*** ACTUATOR DISK : NUMBER\n')])
			if nbActuatorDisk > 1:
				cfv.CFViewWarning('More than one actuator disk -> This macro cannot be used. ')
			else:
				for i in std_contents:
					# AdT 160211 Bug #26123
					line = i.split()
					if len(line) > 0 and line[0] == 'Imposed':
						if line[1] == 'thrust':
							thrust = float(line[3])
						elif line[1] == 'torque':
							torque = float(line[3])
				if Display_Input['Thrust'] == '1' and Display_Input['Torque'] == '1':
					thrust = "%.3e" % float(thrust)
					displayActuator = '|' + 'Thrust = ' + thrust
					torque = "%.3e" % float(torque)
					displayActuator = displayActuator + '|' + 'Torque = ' + torque
				elif Display_Input['Thrust'] == '1':
					thrust = "%.3e" % float(thrust)
					displayActuator = '|' + 'Thrust = ' + thrust
				elif Display_Input['Torque'] == '1':
					torque = "%.3e" % float(torque)
					displayActuator = '|' + 'Torque = ' + torque
		except IOError:
			cfv.CFViewWarning('The .std file is missing, impossible to read values. ')
			displayActuator = '|' + 'Thrust = file is missing'
			if Display_Input['Torque'] == '1':
				displayActuator = displayActuator + '|' + 'Torque = file is missing'
	return displayActuator

#determine the iteration number if there are probes, with the name if it is a steady case and with GetTimeSteps if it isn't,
def iterationId(path,project_name,mvt_file):
	probe = 1
	numbertimesteps = cfv.NumberOfTimeSteps()
	if numbertimesteps > 1:
		iteration = str(GetTimeStep())
	else:
		iteration = (project_name.split("."))[-2]
		#retire the extension
		iteration = iteration[-6:]
		try:
			int(iteration)
		except ValueError:
			iteration = lastIteration(mvt_file)
			probe = 0
	if probe == 1:
		#select the probe number = iteration number
		probe_file = os.path.join(path,"Probe_History.dat")
		f = open(probe_file,"r")
		probe_contents = f.readlines()
		f.close()
		iteration = ((probe_contents[2 + int(iteration)]).split(":"))[2]
	return iteration

#determine the last iteration in a case with no probe
def lastIteration(mvt_file):
	f = open(mvt_file,"r")
	n = 0 
	for line in f:
		n += 1
	iteration = n - 8
	return iteration

#display all variables
def display(position,iteration,Display_Input,mvt_file,path,sim_file):
	cfv.DeleteText('display')
	displayTimeMotions = readTimeMotions(iteration,Display_Input,mvt_file)
	displayTime = displayTimeMotions[0]
	displayMotions = displayTimeMotions[1]
	time = displayTimeMotions[2]
	displayEfforts = readEfforts(iteration,Display_Input,path)
	displayNb_cells = readNumberofcells(time,Display_Input,path)
	displayActuator = readActuator(iteration,Display_Input,sim_file)
	display = str(displayTime  + displayEfforts + displayMotions + displayNb_cells + displayActuator)
	cfv.InsertText2("display",position[0],position[1],0,display)
	
	print " > Values have been displayed in CFView " 
			
	print ' '
	print ' > END OF SCRIPT'
	print ' '

def main(position,path,project_name,Display_Input,mvt_file,sim_file):
	if os.path.exists(os.path.join(path,"Probe_History.dat")) == 1:
		iteration = iterationId(path,project_name,mvt_file)
	else:
		iteration = lastIteration(mvt_file)
	display(position,iteration,Display_Input,mvt_file,path,sim_file)
