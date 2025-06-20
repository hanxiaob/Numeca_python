#                                                                             #
#                         Print model test lines                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : V.Joly
#       Date	  : 21/08/2015
#______________________________________________________________________________
#
# Description: Marine Plugin for CFView
# Changes:
#
# DATE        IMPLEMENTER         	TYPE OF MODIFICATION
# 15-12-2017	  B. Teissedre		#28657 Change names of lines for towing tank lines creation with marine vocabulary
# Changes:
#
# DATE			IMPLEMENTER			TYPE OF MODIFICATION
# 08/01/2018	Baptiste Teissedre	#28657
#______________________________________________________________________________



import math, os
import numpy as np
from Tk import *

def Represent_towing_tank_lines():
	# Check limitation and store path and file info
	# _______________________________________________________________________________________________________________________
	# Get information on the project path and files
	
	print ' '
	print ' > START OF SCRIPT: REPRESENT_TOWINK_TANK_LINES'
	print ' '


	path = GetProjectPath()
	print ''
	print ' > Computation path: '+ path


	# Get cfv project name	
	cfvFile = GetProjectName()
	computation = cfvFile[:-4]


	stop = 0
	# Get sim file path	
	simFile = computation + '.sim'
	simFile = path + os.sep + simFile
	print ' > Sim file: '+  simFile
	if (os.path.exists(simFile) == 0): # Stop plugin if no sim file in computation folder
		print " > SIM file is not present in the computation path."
		Warning("SIM file is not present in the computation path.")
		stop = 1


	# Get the body_param.dat files
	paramFile = computation + '_body_param.dat'
	paramFile = path + os.sep + paramFile
	print ' > Body parameters file: '+  paramFile
	if (os.path.exists(paramFile) == 0): # Stop plugin if no body_param file in computation folder
		print ' > body_param.dat file is not present in the computation path.'
		Warning("body_param.dat file is not present in the computation path.")
		stop = 1


	# Get isis2cfview.input
	i2cFile = path + os.sep + 'isis2cfview.input'
	print ' > isis2cfview.input file: ' + i2cFile
	if (os.path.exists(i2cFile) == 0):    # Stop plugin if isis2cfview_file not in computation folder
		print " > isis2cfview.input file is not present in the computation path."
		Warning("isis2cfview.input file is not present in the computation path.")
		stop = 1


	# Body number limitation
	f = open(paramFile, 'r')
	paramLines = f.readlines()
	f.close()
	nBodyActive = 0
	nMovingBodies = 0
	nFixedBodies = 0
	nBodies = 0
	for i in range(len(paramLines)): # Get number of fixed and moving bodies
		if ('Number of moving bodies' in paramLines[i]):
			nMovingBodies = paramLines[i+2].split()
			nMovingBodies = int(nMovingBodies[0])
			print ' > Number of moving bodies: ' + str(nMovingBodies)
		if ('Number of fixed bodies' in paramLines[i]):
			nFixedBodies = paramLines[i+2].split()
			nFixedBodies = int(nFixedBodies[0])
			print ' > Number of fixed bodies: ' + str(nFixedBodies)
			
	nBodies = nMovingBodies + nFixedBodies
	if (nBodies > 1):  # If nBodies > 1 stop plugin
		print ' > This plugin is not available when more than one body is defined'
		Warning("This plugin is not available when more than one body is defined")
		nBodyActive = 1
	else:                                   # Else get body name in body_param file
		for i in range(len(paramLines)):
			if ('#NI_BEGIN BODY' in paramLines[i]):
				bodyName = paramLines[i+1].split()[2:]
				if len(bodyName)>1:
					Body = bodyName[0]
					for i in range(1, len(bodyName)):
						Body = Body + ' ' + bodyName[i]
					break
				else : Body = bodyName[0]
		print ' > Body name: ' + str(Body)
	bodyName = Body



	selectedSurfaces = GetViewActiveSurfacesList() # Store selected surfaces before 2D/3D checking

	# Check 2D/3D first and stop if 2D
	qnt_exist_1 = 0
	qnt_exist_2 = 0
	qnt_exist_1 = QntFieldExist('Relative Velocity_Z')
	qnt_exist_2 = QntFieldExist('Velocity_Z')
	if qnt_exist_1 == 1:
		QntFieldRemove('Relative Velocity_Z')
	if qnt_exist_2 == 1:
		QntFieldRemove('Velocity_Z')
	if QntFieldExist('Relative Velocity') == 1:
		QntFieldDerived(0 ,'Relative Velocity_Z' ,'Relative Velocity_Z' ,'' ,'0')
		QntFieldVector('Relative Velocity_Z')
	if QntFieldExist('Velocity') == 1:
		QntFieldDerived(0 ,'Velocity_Z' ,'Velocity_Z' ,'' ,'0')
		QntFieldVector('Velocity_Z')
	SelectFromProjectRegExp('')
	range_vel = []
	range_vel = QuantityRangeActiveSurfaces()
	check_2d = 0
	if range_vel[0] == range_vel[1] and range_vel[0] == 0:
		check_2d = 1
	# Clean temporary quantities
	qnt_exist_1 = QntFieldExist('Relative Velocity_Z')
	qnt_exist_2 = QntFieldExist('Velocity_Z')
	if qnt_exist_1 == 1:
		QntFieldRemove('Relative Velocity_Z')
	if qnt_exist_2 == 1:
		QntFieldRemove('Velocity_Z')
	if check_2d == 1:  # If 2D project stop plugin
		print " > This plugin is not available for 2D projects."
		Warning("This plugin is not available for 2D projects.")



	UnselectTypeFromView('') # Unselect all
	for i in range(0, len(selectedSurfaces)):
		SelectFromViewRegExp(selectedSurfaces[i])# Reselect previous active surface

	# Remove external, mirror, iso and fnmb surfaces from selection
	noPrint = 0
	UnselectTypeFromView('EXT')
	UnselectTypeFromView('MIR')
	UnselectTypeFromView('FNMB')
	UnselectFromViewRegExp('*Iso*')
	UnselectFromViewRegExp('*ISO*')
	UnselectFromViewRegExp('*iso*')

	selectedSurfaces = GetViewActiveSurfacesList() # Selected surfaces without ext, mir, fnmb and iso
	if selectedSurfaces == (): # If no body surface selected, stop plugin
			print " > No body surfaces selected."
			Warning("No body surfaces selected.")
			noPrint = 1


	# _______________________________________________________________________________________________________________________



	pad =  1
	class Dialogue(DialogueBox):

		def get_info(self): # Pre filling of dialogue box

			LRefx = 0
			LRefz = 0
			xDir = 0      # Positive X direction by default
			xStart = 0
			zStart = 0
			
		#---Pre filling of user interface ________________________________________________________________________________________________________________
			
			if nMovingBodies == 1: # If one moving body, get mvt_file info
				# Get Mvt_<body>.dat file
				mvtFile = 'Mvt_' + str(bodyName) + '.dat'
				mvtFile = path + os.sep + mvtFile
				print ' > Mvt file: '+  mvtFile
				if (os.path.exists(mvtFile) == 0):
					print ' > Mvt file is not present in the computation path.'
					Warning("Mvt file is not present in the computation path.")
				else:
					f = open(mvtFile,'r')
					mvtLines = f.readlines() # Mvt file lines number
					f.close()
			
					i = 0
					variablesLines = []
					while i < len(mvtLines)-1: # Check the header
						if 'Tx0' in mvtLines[i]:
							variablesLines = mvtLines[i+2].split(',')
							break
						else:
							i = i+1	
					
					i = 0
					Vx = 0
					xDir = 0
					# Read data from Mvt file to get mvt direction 
					while i < len(variablesLines)-1: # Check Vx value
						if 'Vx' in variablesLines[i]:				
							Vx = float(mvtLines[len(mvtLines)-1].split()[i])
							if Vx < 0: # Check Vx orientation
								xDir = 1
							print ' > Vx found in Mvt file = '+ str(Vx) + ' m/s'
							break
						else:
							i = i+1
			
			# Check information in Sim file for reference length and reference point
			f = open(simFile, 'r')
			simLines = f.readlines()
			f.close()
			for i in range(len(simLines)):
				if ('REFERENCE LENGTH' in simLines[i]): # Read vertical reference length
					LRefx = float(simLines[i+2].split()[0])
					print ' > Reference length recorded [m]: '+ str(LRefx)
					
			# Check for minimum and maximum coordinates (only if travelling shot in x)
			travellingshotX = 0
			f = open(i2cFile, 'r')
			i2cLines = f.readlines()
			trshotBody = 0
			f.close()
			
			for i in range(len(i2cLines)):# Read i2c_file to get traveling shot input
				if ('BODY INDEX FOR TRAVELLING SHOT'in i2cLines[i]): 
					trshotBody = i2cLines[i+1].split()						
					if (trshotBody == 0):
						travellingshotX = 0
						break
								
				if ('DOF ACTIVATION FOR TRAVELLING SHOT' in i2cLines[i]):
					if (trshotBody != 0):
						travellingshotX = int(i2cLines[i+1].split()[0])

			if travellingshotX == 1:
				if QntFieldExist('x')== 1:
					QntFieldRemove('x')
				QntFieldDerived(0 ,'x' ,'x' ,'' ,'0')
				[xmin, xmax]= QuantityRangeActiveSurfaces()
				QntFieldRemove('x')
				
				if xDir == 1: #negative orientation
					xStart = xmax
				else:
					xStart = xmin
			else:
				xStart = 0.0
				
			# Check for minimum and maximum coordinates in Z
			if QntFieldExist('z')== 1:
				QntFieldRemove('z')
			QntFieldDerived(0 ,'z' ,'z' ,'' ,'0')
			[zStart, zEnd]= QuantityRangeActiveSurfaces()
			QntFieldRemove('z')
			LRefz = math.fabs(zEnd- zStart)
			
			return [LRefx, LRefz, xDir, xStart, zStart]
			
			
		# Interface display method
		def change_frame(self):
			
			if self.orientationSelection.getValue() == "1":
				self.verticalFrame.pack(side="top", anchor ="w",  padx=pad,pady=pad, fill = 'x')
				self.horizontalFrame.unpack()
			else:
				self.horizontalFrame.pack(side="top", anchor = "w", padx=pad,pady=pad, fill = 'x')
				self.verticalFrame.unpack()
				
		# Interface display method
		def xChangeMethod(self):
			
			if self.xMethodSelection.getValue() == "1":
				self.xList.pack(side="bottom",anchor="w", padx=pad,pady=pad)
				self.xStep.unpack()
				self.labelx.pack(side = "bottom",anchor="w", padx=pad,pady=pad)
			else:
				self.xStep.pack(side="bottom",anchor="w", padx=pad,pady=pad)
				self.xList.unpack()
				self.labelx.unpack()

		def zChangeMethod(self):
			if self.zMethodSelection.getValue() == "1":
				self.zList.pack(side="top",anchor="w", padx=pad,pady=pad)
				self.zStep.unpack()
				self.labelz2.pack(side = "bottom",anchor="w", padx=pad,pady=pad)

			else:
				self.zStep.pack(side="top",anchor="w", padx=pad,pady=pad)
				self.zList.unpack()
				self.labelz2.unpack()



		#---Interface definition ________________________________________________________________________________________________________________
		def __init__(self):
			DialogueBox.__init__(self, "Drawing model test lines" )
			
			[xLRefDef, LRefz, xDir, xStart, zStart] = self.get_info()

			# Choice of lines 
			orientationFrame = self.labelframe(label=" Lines ").pack(side="top", anchor = "w", padx=pad,pady=pad, fill = 'x')
			self.orientationSelection = Variable(1)
			orientationFrame.radiobutton("Section lines",self.orientationSelection, value=1, command=Command(self,Dialogue.change_frame)).pack(side = "left", padx=pad,pady=pad)
			orientationFrame.radiobutton("Waterlines",self.orientationSelection, value=0, command=Command(self,Dialogue.change_frame)).pack(side = "left", padx=pad,pady=pad)

			self.verticalFrame = self.frame().pack(side="top", anchor = "w", padx=pad,pady=pad, fill = 'x')
			self.horizontalFrame = self.frame()

			# Vertical lines parameters
			xSettings = self.verticalFrame.labelframe(label="Settings").pack(side="top", anchor = "w", padx=pad,pady=pad, fill = 'x')
			xDirectionFrame = xSettings.frame().pack(side="top", anchor = "w", padx=pad,pady=pad)
			xMvtDirectionFrame = xSettings.frame().pack(side="top", anchor = "w",  padx=pad,pady=pad)
			xMethodFrame = xSettings.frame().pack(side="top", anchor = "w", padx=pad,pady=pad)
			xStartingPointFrame = xSettings.frame().pack(side="top", anchor = "w", padx=pad,pady=pad)

			# Reading parameters
			self.xStart = xStartingPointFrame.entry(label="Starting point Ps (X) " , width = 20, labelwidth= 25, value = xStart, unit='\[m]').pack(side = "top",anchor="w", padx=pad,pady=pad)
			self.LRefx = xStartingPointFrame.entry(label="Drawing length DL " , width = 20, labelwidth=25, value = xLRefDef, unit='\[m]').pack(side="top",anchor="w", padx=pad,pady=pad)
			
			self.xMethodSelection = Variable(1)
			xMethod = xMethodFrame.label(text="Drawing method").pack(side = "top",anchor="w", padx=pad,pady=pad)
			xMethodFrame.radiobutton("List           ",self.xMethodSelection, value=1, command=Command(self,Dialogue.xChangeMethod)).pack(side="left", anchor = "w", padx=pad,pady=pad)
			xMethodFrame.radiobutton("Interval",self.xMethodSelection, value=0, command=Command(self,Dialogue.xChangeMethod)).pack(side="left", padx=pad,pady=pad)
			
			self.xList = xStartingPointFrame.entry(label="Position list (c1 c2...cmax)", width = 20, labelwidth = 25, value = '').pack(side = "bottom",anchor="w", padx=pad,pady=pad)
			self.xStep = xStartingPointFrame.entry(label="Interval " , width = 20, labelwidth=25, value = 0, unit='\[m]')

			self.labelx = xSettings.label(text="Line location= Ps + (ci/cmax)*DL").pack(side = "bottom",anchor="w", padx=pad,pady=pad)
			#self.selectDirX = Variable(1)
			#xOrientation = xDirectionFrame.label(text="Drawing direction").pack(side = "top",anchor="w", padx=pad,pady=pad)
			#xDirectionFrame.radiobutton("Bow to aft",self.selectDirX, value=1).pack(side="left", padx=pad,pady=pad)
			#xDirectionFrame.radiobutton("Aft to bow",self.selectDirX, value=0).pack(side="left", padx=pad,pady=pad)
			
			if xDir == 0:
				self.xMvtDirSelect = Variable(1)
			else:
				self.xMvtDirSelect = Variable(0)
			xMvtDir = xMvtDirectionFrame.label(text="Drawing direction").pack(side = "top",anchor="w", padx=pad,pady=pad)
			xMvtDirectionFrame.radiobutton("Positive X",self.xMvtDirSelect, value=1).pack(side="left", padx=pad,pady=pad)
			xMvtDirectionFrame.radiobutton("Negative X",self.xMvtDirSelect, value=0).pack(side="left", padx=pad,pady=pad)
				
				
				
			# Horizontal lines parameters
			zSettings = self.horizontalFrame.labelframe(label="Settings").pack(side="top", anchor = "w", padx=pad,pady=pad, fill = 'x')
			zMethodFrame = zSettings.frame().pack(side="top", anchor ="w", padx=pad,pady=pad)
			zStartingPointFrame = zSettings.frame().pack(side="left", padx=pad,pady=pad)
			
			# Reading parameters
			self.zStart = zStartingPointFrame.entry(label="Starting point Ps (Z) " , width = 20, labelwidth = 25, value = zStart, unit='\[m]').pack(side = "top",anchor="w", padx=pad,pady=pad)
			self.LRefz = zStartingPointFrame.entry(label="Drawing length DL " , width = 20, labelwidth = 25, value = LRefz, unit='\[m]').pack(side = "top",anchor="w", padx=pad,pady=pad)
			
			labelz = zMethodFrame.label(text="Drawing from bottom to deck").pack(side = "top", anchor="w", padx=pad,pady=pad)
			labelzspace = zMethodFrame.label(text="   ").pack(side = "top", anchor="w", padx=pad,pady=pad)
			self.zMethodSelection = Variable(1)
			zMethod = zMethodFrame.label(text="Drawing method").pack(side = "top", anchor="w", padx=pad,pady=pad)
			zMethodFrame.radiobutton("List           ",self.zMethodSelection, value=1, command=Command(self,Dialogue.zChangeMethod)).pack(side="left", anchor = "w", padx=pad,pady=pad)
			zMethodFrame.radiobutton("Interval",self.zMethodSelection, value=0, command=Command(self,Dialogue.zChangeMethod)).pack(side="top", padx=pad,pady=pad)

			
			self.zList = zStartingPointFrame.entry(label="Position list (c1 c2...cmax)", width = 20, labelwidth = 25, value = '').pack(side = "top",anchor="w", padx=pad,pady=pad)
			self.zStep = zStartingPointFrame.entry(label="Interval " , width = 20, labelwidth=25, value = 0 , unit='\[m]')
			self.labelz2 = zStartingPointFrame.label(text="Line location= Ps + (ci/cmax)*DL").pack(side = "bottom",anchor="w", padx=pad,pady=pad)

			# Close, delete and apply button
			close_frame = self.frame().pack(side = "bottom", anchor = "e")
			optionFrame = self.frame().pack(side="bottom", anchor = "e")
			
			apply  = optionFrame.button(text="Draw lines", command = Command(self,Dialogue.apply ))
			deleteLines = optionFrame.button(text="Delete lines", command = Command(self,Dialogue.deleteLines))
			apply.pack(side = "left", anchor = "w")
			deleteLines.pack(side = "right")
			
			closePlug = close_frame.button(text="     Close     ", command = Command(self,Dialogue.closePlug))
			closePlug.pack(side = "bottom", anchor="se")
			
			self.showCentered()



		#---Computation script ________________________________________________________________________________________________________________
		
		
		def apply(self):

			# Variable initialization
			cardanActive = 0
			trans = np.zeros((3))
			Cx = 0.0
			Cy = 0.0
			Cz = 0.0
			anglex = 0.0
			angley = 0.0
			anglez = 0.0
			xRef = 0.0
			yRef = 0.0
			zRef = 0.0

			# Get initial position from SIM file (cardan angle, initial GC/reference point position)
			f = open(simFile, 'r')
			simLines = f.readlines()
			print '------------------------------------------------------------------------------------------------'
			for i in range (len(simLines)):
				
			# Check if cardan angles are active. If yes, save them in angle variables	
				if ('CARDAN ANGLES'in simLines[i]):
					if ('YES' in simLines[i+2]):
						cardanActive = 1			
						print ' > Cardan angles are active in this computation'
						
				if (('ORIENTATION' in simLines[i]) & (cardanActive ==1)): # Stock Cardan angles
					Cx = float(simLines[i+2].split()[0])
					Cy = float(simLines[i+2].split()[1])
					Cz = float(simLines[i+2].split()[2])
					print ' > Cardan angle values recorded [rad]:'
					print ' > ' + '(' + str(Cx) + ',' + str(Cy) + ',' + str(Cz) + ')'
					
				if ('REFERENCE POINT' in simLines[i]) and ('BODY' in simLines[i]): # Read reference point (imposed motion case)
					xRef = float(simLines[i+2].split()[0])
					yRef = float(simLines[i+2].split()[1])
					zRef = float(simLines[i+2].split()[2])
					print ' > Reference point recorded [m]: '+ '(' + str(xRef) + ',' + str(yRef) + ',' + str(zRef) + ')'
					
				if ('POSITION GC' in simLines[i]): # Read initial CG position (solved motion case)
					xRef = float(simLines[i+2].split()[0])
					yRef = float(simLines[i+2].split()[1])
					zRef = float(simLines[i+2].split()[2])
					print ' > Initial GC position recorded [m]: '+ '(' + str(xRef) + ',' + str(yRef) + ',' + str(zRef) + ')'
					
			f.close()


			# Get Mvt_<body>.dat file
			mvtFile = 'Mvt_' + str(bodyName) + '.dat'
			mvtFile = path + os.sep + mvtFile
			if (os.path.exists(mvtFile) == 0):
				print ' > No moving body '
			else:
				#Get final position of body from Mvt file
				f = open(mvtFile, 'r')
				mvtLines = f.readlines()
				
				# Read mvt_file to get Tx Ty Tz Rx Ry Rz
				for i in range(len(mvtLines)):
					if ('VARIABLES' in mvtLines[i]):
						dofs = mvtLines[i].split(',')
						#print dofs
						for j in range(0, len(dofs)):
									
							if (dofs[j] == '"Tx0"'):   # If Tx in dofs get Tx
								trans[0] = float(mvtLines[len(mvtLines)-1].split()[j]) - xRef
							
							if (dofs[j] == '"Ty0"'):   # If Ty in dofs get Ty
								trans[1] += float(mvtLines[len(mvtLines)-1].split()[j]) - yRef
								
							if (dofs[j] == '"Tz0"'):   # If Tz in dofs get Tz
								trans[2] += float(mvtLines[len(mvtLines)-1].split()[j]) - zRef
							
							
							if (dofs[j] == '"Rx0"' or dofs[j] == '"Rx0"\n' or dofs[j] == '"Rx2"' or dofs[j] == '"Rx2"\n'): # If Rx in dofs get Rx
								anglex = float(mvtLines[len(mvtLines)-1].split()[j])  
								if (anglex > 2*np.pi): anglex = anglex % 2*np.pi # If angle > 2Pi then euclidian division
								
								anglex = anglex-Cx  # Rx = Rx - Roll
								#print ' anglex = ' + str(anglex)
								
								
							if (dofs[j] == '"Ry0"' or dofs[j] == '"Ry0"\n' or dofs[j] == '"Ry1"' or dofs[j] == '"Ry1"\n'): #If Ry in dofs get Ry
								angley = float(mvtLines[len(mvtLines)-1].split()[j])  
								if (angley > 2*np.pi): angley = angley % 2*np.pi # If angle > 2Pi then euclidian division
								
								angley = angley-Cy # Ry = Ry - Pitch
								#print 'angley = ' + str(angley)
								
								
							if (dofs[j] == '"Rz0"' or dofs[j] == '"Rz0"\n' or dofs[j] == '"Rz1"'): # If Rz in dofs get Rz
								anglez = float(mvtLines[len(mvtLines)-1].split()[j])   
								if (anglez > 2*np.pi): anglez = anglez % 2*np.pi # If angle > 2Pi then euclidian division
								
								anglez = anglez-Cz  # Rz = Rz - Yaw
								#print 'anglez = ' + str(anglez)

								
							if ('"Vx"' in dofs[j] or '"Vy"' in dofs[j] or '"Vz"' in dofs[j] or 'dR' in dofs[j]):
								break
						break

				f.close()


			# Check travelling shot used in isis2cfview
			f = open(i2cFile, 'r')
			i2cLines = f.readlines()
			trshotBody = 0
			
			for i in range(len(i2cLines)):# Read i2c_file to get traveling shot input
					
				if ('BODY INDEX FOR TRAVELLING SHOT'in i2cLines[i]): 
					trshotBody = i2cLines[i+1].split()
						
					if (trshotBody == 0):
						break
							
				if ('DOF ACTIVATION FOR TRAVELLING SHOT' in i2cLines[i]):
					if (trshotBody != 0):
							trshot = i2cLines[i+1].split()
							print ' > Travelling shot parameters:'
							print ' > ' + str(trshot)
										
							if (int(trshot[0]) == 1): # If traveling shot active, no translation
								trans[0] = 0.0
					
							if (int(trshot[1]) == 1):
								trans[1] = 0.0
				
							if (int(trshot[2]) == 1):
								trans[2] = 0.0
					
							if (int(trshot[3]) == 1): # If traveling shot active, no rotation
								anglex = 0
					
							if (int(trshot[4]) == 1):
								angley = 0
								
							if (int(trshot[5]) == 1):
								anglez = 0
							break
			
			f.close()
			
			#---Check if user parameters are float number  ________________________________________________________________________________________________________________
			noPrint = 0 # Stopping variable
			
			LRefxVerif = self.LRefx.getStringValue().split()
			LRefzVerif = self.LRefz.getStringValue().split()

			xStartVerif = self.xStart.getStringValue().split()
			zStartVerif = self.zStart.getStringValue().split()
			
			xStepVerif = self.xStep.getStringValue().split()
			zStepVerif = self.zStep.getStringValue().split()
			
			if LRefxVerif == []: 
				LRefx = 0
			else:
				LRefTest = 0
				# Check if entry is a float number and read it
				while LRefTest == 0:
					try:
						LRefTest = 1
						float(self.LRefx.getFloatValue())
						LRefx = self.LRefx.getFloatValue() # Horizontal reference length
						break
					except ValueError:
						print(" > X Reference length must be a positive float number.")
						Warning("X Reference length must be a positive float number.")
						noPrint = 1
			
			
			if LRefzVerif == []: 
				LRefz = 0
			else:
				LRefTest = 0
				# Check if entry is a float number and read it
				while LRefTest == 0:
					try:
						LRefTest = 1
						float(self.LRefz.getFloatValue())
						LRefz = self.LRefz.getFloatValue() # Vertical reference length 
						break
					except ValueError:
						print(" > Z Reference length must be a positive float number.")
						Warning("Z Reference length must be a positive float number.")
						noPrint = 1
			
			
			
			if xStartVerif == []: 
				xStart = 0
			else:
				LRefTest = 0
				# Check if entry is a float number and read it
				while LRefTest == 0:
					try:
						LRefTest = 1
						float(self.xStart.getFloatValue())
						xStart = self.xStart.getFloatValue()   # X Space step
						break
					except ValueError:
						print(" > Starting point coordinate along X axis must be a float number.")
						Warning("Starting point coordinate along X axis must be a float number.")
						noPrint = 1
			
			
			if zStartVerif == []: 
				zStart = 0
			else:
				LRefTest = 0
				# Check if entry is a float number and read it
				while LRefTest == 0:
					try:
						LRefTest = 1
						float(self.zStart.getFloatValue())
						zStart = self.zStart.getFloatValue()   # Z Space step
						break
					except ValueError:
						print(" > Starting point coordinate along Z axis must be a float number.")
						Warning("Starting point coordinate along Z axis must be a float number.")
						noPrint = 1
			
			
			if xStepVerif == []: 
				xStep = 0
			else:
				LRefTest = 0
				# Check if entry is a float number and read it
				while LRefTest == 0:
					try:
						LRefTest = 1
						float(self.xStep.getFloatValue())
						xStep = self.xStep.getFloatValue() # X coordinate of starting point
						break
					except ValueError:
						print(" > X interval must be a positive float number.")
						Warning("X interval must be a positive float number.")
						noPrint = 1
				#Check it is a single value and not a list
				xSteptest = self.xStep.getStringValue()
				xSteptest = xSteptest.strip()
				xSteptest = xSteptest.split()
				if len(xSteptest) >1:
					print(" > X interval must be a positive float number.")
					Warning("X interval must be a positive float number.")
					noPrint = 1
		
			
			if zStepVerif == []: 
				zStep = 0
			else:
				LRefTest = 0
				# Check if entry is a float number and read it
				while LRefTest == 0:
					try:
						LRefTest = 1
						float(self.zStep.getFloatValue())
						zStep = self.zStep.getFloatValue() # Z coordinate of starting point
						break
					except ValueError:
						print(" > Z interval must be a positive float number.")
						Warning("Z interval must be a positive float number.")
						noPrint = 1
				#Check it is a single value and not a list
				zSteptest = self.zStep.getStringValue()
				zSteptest = zSteptest.split()
				if len(zSteptest) > 1:
					print(" > Z interval must be a positive float number.")
					Warning("Z interval must be a positive float number.")
					noPrint = 1
		
			
			
			xList = []
			zList = [] 
			
			# Reading user parameters 
			selectDirX = self.orientationSelection.getValue()	# Vertical drawing direction selection
			print 'TEMP' +str(selectDirX)
			xMvtDirSelect = self.xMvtDirSelect.getValue()	# Moving direction selection
			xMethodSelection = self.xMethodSelection.getValue()   # Lines drawing method selection
			zMethodSelection = self.zMethodSelection.getValue()   # Line drawing method selection
			
			xLineName = self.xList.getStringValue().split()  # List used to name vertical isolines
			zLineName = self.zList.getStringValue().split()  # List used to name horizontal isolines
			
			xList = self.xList.getStringValue().split() # Listing of vertical drawing proportionnal coordinates 
			zList = self.zList.getStringValue().split() # Listing of horizontal drawing proportionnal coordinates 
			
			if noPrint == 0:
				
				# Check if no negative user value, if yes, error message and stop plugin
				xListVerif = xList
				zListVerif = zList
				
				i = 0
				if xList != []:
					for i in range(len(xList)):
						xListVerif[i] = xList[i]
					
					LRefTest = 0
					for i in range(len(xListVerif)):
						# Check if only float numbers in zList
						while LRefTest < i+1:
							try:
								LRefTest = LRefTest + 1
								float(xListVerif[i])
								break
							except ValueError:
								print(' > List of section lines positions has to be float numbers.')
								Warning(' > List of section lines positions has to be float numbers.')
								noPrint = 1
				
				
				i = 0
				if zList != []:
					for i in range(len(zList)):
						zListVerif[i] = zList[i]
					
					LRefTest = 0
					for i in range(len(zListVerif)):
						# Check if only float numbers in zList
						while LRefTest < i+1:
							try:
								LRefTest = LRefTest + 1
								float(zListVerif[i])
								break
							except ValueError:
								print(' > List of waterlines positions has to be float numbers.')
								Warning(' > List of waterlines positions has to be float numbers.')
								noPrint = 1
				
				if xList == []:
					xList = [1]
				if zList == []:
					zList = [1]
				a = float(min(xList))
				b = float(min(zList))
				
				if ((xStep < 0) or (zStep < 0)): # No negative interval
					print ' > Interval has to be a positive float number.'
					Warning("Interval has to be a positive float number.")
					noPrint = 1
					
				if (( a < 0) or (b < 0)): # No negative float in positions list
					print ' > List elements have to be positive float numbers.'
					Warning("List elements have to be positive float numbers.")
					noPrint = 1
				
				if (( LRefx < 0) or (LRefz < 0)): # No negative reference length 
					print ' > Reference length has to be a positive float number.'
					Warning("Reference length has to be a positive float number.")
					noPrint = 1
				
				if xList == [1]:
					xList = []
				if zList == [1]:
					zList = []
			
			
			#  ________________________________________________________________________________________________________________
			
			
			# Normal definition whithout rotation
			xNormal = [1,0,0] 
			yNormal = [0,1,0]
			zNormal = [0,0,1]
			
			if noPrint == 0:
				# Starting point position vector
				
				print ' > Starting point = ' + str([xStart, 0.0, zStart])
				
				nStart = [xStart - xRef, 0 - yRef, zStart - zRef]
				print ' > nStart = ' + str(nStart)
				print '------------------------------------------------------------------------------------------------'
				
				
				# Compute plane normal with rotation matrix
				# _______________________________________________________________________________________________________________________

				# Rotation around Z-axis first
				# Cardan rotation first
				c=np.cos(Cz)
				s=np.sin(Cz)
				N = ([[c+(1-c)*zNormal[0]**2, (1-c)*zNormal[0]*zNormal[1]-s*zNormal[2], (1-c)*zNormal[0]*zNormal[2]+s*zNormal[1]],
						[(1-c)*zNormal[0]*zNormal[1]+s*zNormal[2], c+(1-c)*zNormal[1]**2, (1-c)*zNormal[1]*zNormal[2]-s*zNormal[0]],
						[(1-c)*zNormal[0]*zNormal[2]-s*zNormal[1], (1-c)*zNormal[1]*zNormal[2]+s*zNormal[0], c+(1-c)*zNormal[2]**2]])
				# New axis computation
				xNormal = np.dot(N, xNormal)
				yNormal = np.dot(N, yNormal)
				zNormal = np.dot(N, zNormal)
				nStart = np.dot(N, nStart)
				#print 'N = ' + str(N)

				# Motion rotation aroud Z axis 
				c=np.cos(anglez)
				s=np.sin(anglez)
				N2 = ([[c+(1-c)*zNormal[0]**2, (1-c)*zNormal[0]*zNormal[1]-s*zNormal[2], (1-c)*zNormal[0]*zNormal[2]+s*zNormal[1]],
						[(1-c)*zNormal[0]*zNormal[1]+s*zNormal[2], c+(1-c)*zNormal[1]**2, (1-c)*zNormal[1]*zNormal[2]-s*zNormal[0]],
						[(1-c)*zNormal[0]*zNormal[2]-s*zNormal[1], (1-c)*zNormal[1]*zNormal[2]+s*zNormal[0], c+(1-c)*zNormal[2]**2]])

				xNormal = np.dot(N2, xNormal)
				yNormal = np.dot(N2, yNormal)
				zNormal = np.dot(N2, zNormal)
				nStart = np.dot(N2, nStart)
				#print 'N2 = ' + str(N2)

				# ________________________________________________

				# Rotation around Y axis 
				c=np.cos(Cy)
				s=np.sin(Cy)
				M = ([[c+(1-c)*yNormal[0]**2, (1-c)*yNormal[0]*yNormal[1]-s*yNormal[2], (1-c)*yNormal[0]*yNormal[2]+s*yNormal[1]],
						[(1-c)*yNormal[0]*yNormal[1]+s*yNormal[2], c+(1-c)*yNormal[1]**2, (1-c)*yNormal[1]*yNormal[2]-s*yNormal[0]],
						[(1-c)*yNormal[0]*yNormal[2]-s*yNormal[1], (1-c)*yNormal[1]*yNormal[2]+s*yNormal[0], c+(1-c)*yNormal[2]**2]])

				xNormal = np.dot(M, xNormal)
				yNormal = np.dot(M, yNormal)
				zNormal = np.dot(M, zNormal)
				nStart = np.dot(M, nStart)
				#print 'M = ' + str(M)
				
				c=np.cos(angley)
				s=np.sin(angley)
				M2 = ([[c+(1-c)*yNormal[0]**2, (1-c)*yNormal[0]*yNormal[1]-s*yNormal[2], (1-c)*yNormal[0]*yNormal[2]+s*yNormal[1]],
						[(1-c)*yNormal[0]*yNormal[1]+s*yNormal[2], c+(1-c)*yNormal[1]**2, (1-c)*yNormal[1]*yNormal[2]-s*yNormal[0]],
						[(1-c)*yNormal[0]*yNormal[2]-s*yNormal[1], (1-c)*yNormal[1]*yNormal[2]+s*yNormal[0], c+(1-c)*yNormal[2]**2]])

				xNormal = np.dot(M2, xNormal)
				yNormal = np.dot(M2, yNormal)
				zNormal = np.dot(M2, zNormal)
				nStart = np.dot(M2, nStart)
				#print 'M2 = ' + str(M2)

				# ________________________________________________

				# Rotation around X axis
				c=np.cos(Cx)
				s=np.sin(Cx)
				L = ([[c+(1-c)*xNormal[0]**2, (1-c)*xNormal[0]*xNormal[1]-s*xNormal[2], (1-c)*xNormal[0]*xNormal[2]+s*xNormal[1]],
						[(1-c)*xNormal[0]*xNormal[1]+s*xNormal[2], c+(1-c)*xNormal[1]**2, (1-c)*xNormal[1]*xNormal[2]-s*xNormal[0]],
						[(1-c)*xNormal[0]*xNormal[2]-s*xNormal[1], (1-c)*xNormal[1]*xNormal[2]+s*xNormal[0], c+(1-c)*xNormal[2]**2]])

				xNormal = np.dot(L, xNormal)
				yNormal = np.dot(L, yNormal)
				zNormal = np.dot(L, zNormal)
				nStart = np.dot(L, nStart)
				#print 'L = ' + str(L)

				c=np.cos(anglex)
				s=np.sin(anglex)
				L2 = ([[c+(1-c)*xNormal[0]**2, (1-c)*xNormal[0]*xNormal[1]-s*xNormal[2], (1-c)*xNormal[0]*xNormal[2]+s*xNormal[1]],
						[(1-c)*xNormal[0]*xNormal[1]+s*xNormal[2], c+(1-c)*xNormal[1]**2, (1-c)*xNormal[1]*xNormal[2]-s*xNormal[0]],
						[(1-c)*xNormal[0]*xNormal[2]-s*xNormal[1], (1-c)*xNormal[1]*xNormal[2]+s*xNormal[0], c+(1-c)*xNormal[2]**2]])

				xNormal = np.dot(L2, xNormal)
				yNormal = np.dot(L2, yNormal)
				zNormal = np.dot(L2, zNormal)
				nStart = np.dot(L2, nStart)
				#print 'L2 = ' + str(L2)
			
				# ________________________________________________

				print ' > Total translation [m]', trans
				print ' > Rotation angles [rad]', anglex, angley, anglez

				print '------------------------------------------------------------------------------------------------'
				print ' > xNormal = ' + str(xNormal)
				print ' > zNormal = ' + str(zNormal)
				
				
				# Final starting point position (translation + rotation)
				nFinal = [nStart[0] + trans[0] + xRef, nStart[1] + trans[1] + yRef, nStart[2] + trans[2] + zRef]
				print ' > Final point = ' + str(nFinal)
				xStart = nFinal[0]
				yStart = nFinal[1]
				zStart = nFinal[2]

				print '------------------------------------------------------------------------------------------------'
				
			
			#---Lines coordinates ________________________________________________________________________________________________________________
			#---Vertical lines ________________________________________________________________________________________________________________
			if noPrint == 0:
				dx = 0
				dz = 0
				if xMethodSelection == '1': # List method
					if xList != []:
						for i in range(len(xList)):
							xList[i] = float(xList[i])

						# Space step definition (length/higher element)
						if max(xList) > 0:
							dx = LRefx/max(xList)
						elif max(xList) == 0:
							dx = LRefx
							
				elif xMethodSelection == '0': # Space step method (define coordinates list)
					if ((xStep != 0) == True):
						length = math.floor(LRefx/xStep)+1
						xList = list(range(int(length)))
						dx = xStep
						xLineName = range(int(length))
					else:
						length = 0
						xList = list(range(int(length)))
						dx = xStep
						xLineName = range(int(length))
					
				# Intersections coordinates (X)
				if xMvtDirSelect == '1': # Positive X
					for i in range(0,len(xList)):
						xList[i] = xStart + xList[i]*dx
				else:                    # Negative X
					for i in range(0,len(xList)):
						xList[i] = xStart - xList[i]*dx
				
				
				#---Horizontal line ________________________________________________________________________________________________________________
				if zMethodSelection == '1':  # List method
					if zList != []:
						for i in range(len(zList)):
							zList[i] = float(zList[i])
							
						# Space step definition
						if abs(max(zList)) > 0:
							dz = LRefz/abs(max(zList))
						elif max(zList) == 0:
							dz = LRefz
									
				elif zMethodSelection == '0':  # Space step method
					if ((zStep != 0) == True):
						length = math.floor(LRefz/zStep)+1 # Number of lines to draw 
						zList = list(range(int(length)))
						dz = zStep
						zLineName = range(int(length))
					else:
						length = 0
						zList = list(range(int(length)))
						dz = zStep
						zLineName = range(int(length))
						
				# Intersections coordinates (Z)
				for i in range(0,len(zList)):
					zList[i] = zStart + zList[i]*dz
				
				
			#---Surfaces selection  ________________________________________________________________________________________________________________
			# Remove external, mirror and fnmb surfaces from selection
			UnselectTypeFromView('EXT')
			UnselectTypeFromView('MIR')
			UnselectTypeFromView('FNMB')
			UnselectFromViewRegExp('*Iso*')
			UnselectFromViewRegExp('*ISO*')
			UnselectFromViewRegExp('*iso*')	

			selectedSurfaces = GetViewActiveSurfacesList() # Store selected surfaces without ext, mir, fnmb
			if selectedSurfaces == (): # If no body surface selected, no drawing
					print " > No body surfaces selected."
					Warning("No body surfaces selected.")
					noPrint = 1
			
			
			if noPrint == 0: # If body surfaces selected and no negative user parameter
				
				#---Vertical lines ________________________________________________________________________________________________________________
				# Model lines drawing
				if selectDirX == "1":
					i = 0
					normal = xNormal
					xLine = 'Section_Line_'
					while i <= len(xList)-1:
						point = [float(xList[i]),yStart,zStart] # Belonging point used to define plane equation
						xLine = 'Section_Line_' + str(xLineName[i]) 
						if QntSurfaceExist(xLine) == 1: # If quantity name already used
							xLine = xLine + '_New'

						# Plane equation definition
						planeEquation = str(normal[0])+'*x+'+str(normal[1])+'*y+'+str(normal[2])+'*z-('+str(normal[0]*point[0]+normal[1]*point[1]+normal[2]*point[2])+')'
						print planeEquation
						# Plane quantity creation
						QntSurfaceDerived(0 ,xLine ,planeEquation)
						
						# Model lines drawing (isoline 0)
						SetQuantityIsolineColorLock(xLine, 1)
						SclIsolineValue(0)
						
						SelectIsolineCurves('Isoline ' + xLine + ' = 0')
						UpdateLineType(0,0,0,0,0,0,1,2)
				
						# Remove quantity and color map
						RprColormap(0)
						QntSolidRemove(xLine)
						
						i = i+1
				
				#---Horizontal lines ________________________________________________________________________________________________________________
				# Model lines drawing
				else:
					i = 0
					normal = zNormal
					zLine = 'Waterline_'
					while i <= len(zList)-1:
						point = [xStart,yStart,float(zList[i])] # Belonging point used to define plane equation
						zLine = 'Waterline_' + str(zLineName[i])
						if QntSurfaceExist(zLine) == 1: # If quantity name already used
							zLine = zLine + '_New'
							
						# Plane equation definition
						planeEquation = str(normal[0])+'*x+'+str(normal[1])+'*y+'+str(normal[2])+'*z-('+str(normal[0]*point[0]+normal[1]*point[1]+normal[2]*point[2])+')'
						print planeEquation
						# Plane quantiy creation
						QntSurfaceDerived(0 ,zLine ,planeEquation)
						
						# Model line drawing (isoline 0)
						SetQuantityIsolineColorLock(zLine, 1)
						SclIsolineValue(0)
						
						SelectIsolineCurves('Isoline ' + zLine + ' = 0')
						UpdateLineType(0,0,0,0,0,0,1,2)
						
						# Remove quantity and color map
						RprColormap(0)
						QntSolidRemove(zLine)
						
						i = i+1
				
				#26879 uselect last line when finished drawing	
				SelectBoundaryCurves('')
				
				print ''
				print ' > Model lines drawn '
				print ''


		def deleteLines(self):
			
			selectedSurfaces = GetViewActiveSurfacesList() # Store selected surfaces
			UnselectTypeFromView('') # Unselect all
			SelectTypeFromProject('SOL') # Select all solid surfaces
			
			# Remove isolines and solid quantities
			DeleteIsoline()
			QntSolidRemoveAll()
			UnselectTypeFromView('') # Unselect all

			for i in range(0, len(selectedSurfaces)):
				SelectFromViewRegExp(selectedSurfaces[i])# Reselect previous active surface

			print ''
			print ' > Model lines deleted '
			print ''
		
		
		def closePlug(self):
			
			self.close() 

			print ''
			print ' > END OF SCRIPT'
			print ''
			
			
	if ((check_2d == 0) and (noPrint == 0) and (nBodyActive == 0) and (stop == 0)): z = Dialogue() # Limitation
