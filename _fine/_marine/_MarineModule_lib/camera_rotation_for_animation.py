#                                                                             #
#                         Camera rotation for animation                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : M. Holchaker
#       Date	  : 21/08/2015
#______________________________________________________________________________
#
# Description: Rotate geometry and save pictures to create an animation
# Changes:
#
# DATE        IMPLEMENTER         TYPE OF MODIFICATION
#22-08-2016   A. del Toro         #27382 correction
#______________________________________________________________________________

import os, math, sys
#sys,fileinput,string
from Tk import *
#import string
import CFView as c
import datetime

def Camera_rotation_for_animation():
  
	class MyDialogueCameraRotation(DialogueBox):
		
		def __init__(self):
	  
			print ' '
			print ' > START OF SCRIPT: CAMERA_ROTATION_FOR_ANIMATION'
			print ' '
			#If any condition is not met, end = 1 will be return to stop the script
			end = 0
				
			try :
				self.path = GetProjectPath()
				# AdT #26845 > Begin
				if sys.platform == 'win32':
					pathTemp2 = self.path.split('/')
					pathTemp1 = pathTemp2.pop(0)
					self.path = pathTemp1 + os.sep + os.path.join(*pathTemp2)
				# AdT #26845 > End
			except Exception:
				CFViewWarning("No project is currently opened. Press 'OK', open FINE/Marine results in CFView and launch this plugin again.")
				end = 1
			
			if end == 0:
				dims = GetProjectDimensions()
				if (dims[0] != 3 and dims[1] != 3):
					CFViewWarning("This plugin is not available for 2D projects.")
					end = 1
			
			if end == 0:
				project_name = GetProjectName()
				folder = (GetProjectPath().split('/'))[-1]
				self.sim_file = folder + ".sim"
				# AdT #26845 > Begin
				self.sim_file = os.path.join(self.path,self.sim_file)
				#Adding extension to get the body parameter file
				self.body_parameter_file = folder + "_body_param.dat"
				self.body_parameter_file = os.path.join(self.path,self.body_parameter_file)
				# AdT #26845 > End

				try:
					body_parameter = self.readBodyparameter()
					nbr_body = body_parameter[0]
					end = body_parameter[2]
					if end == 0:
						if nbr_body == 1:
							print ' > There is one body in the project.'
							center = body_parameter[1]
							centerX = float(center[0])
							centerY = float(center[1])
							centerZ = float(center[2])
							#value of Refer_length and Free_surface_location in sim_file
							# If .sim_file doesn't exist Refer_length = Free_surface_location = 0
							if (os.path.exists(self.sim_file) == 0):
								Refer_length = 0
								Free_surface_location = 0
								CFViewWarning( " SIM file is not present in the computation path. Values will be initialised at 0.")
							else :
								sim_values = self.readSim()
								Refer_length = sim_values[0]
								Free_surface_location = sim_values[1]
						elif nbr_body > 1:
							print '> There are ' + str(nbr_body) + ' bodies in the project. All the values will be initialized at 0. '
							centerX = 0
							centerY = 0
							centerZ = 0
							Refer_length = 0
							Free_surface_location = 0
						else:
							CFViewWarning( " There are no bodies in the project.")
							end = 1
				except IOError:
					CFViewWarning("The file body_param.dat is missing, impossible to execute the script")
					end = 1

			if end == 0:
				DialogueBox.__init__(self, "Camera Rotation Recording" )

				#definition of the main frames
				Frame1 = self.frame()
				Frame1.pack(side="top",anchor = "w",fill ='x' )
				
				center_frame = self.frame()
				center_frame.pack(side="top",anchor = 'w',fill='x')
				
				advanced_frame = self.frame()
				advanced_frame.pack(side="top",anchor = "w",fill='x')
				
				Frame4 = self.frame()
				Frame4.pack(side="top",anchor = "e",fill='x')
				
				#frame 1 : Refer_length and Free_surface_location
				Refer_lengthFrame = Frame1
				self.Refer_lengthEntry = Refer_lengthFrame.entry(label=" Reference length " , width = 8, value = Refer_length, unit='\[m]', labelwidth = 20).pack(side = "top")
				
				 #CameraHeight
				height_frame = Frame1
				self.heightEntry = height_frame.entry(label=" Camera height " , width = 8, labelwidth = 20,value = Refer_length/10 + Free_surface_location , unit='\[m]').pack(side = "top")
				
				#frame2 : center of gravity
				
				# AdT 160822 > Bug #27382: Beginning
				gravity_center = center_frame.label(text =' Rotation center ').pack(side = 'top', anchor = "w")
				# AdT 160822 > Bug #27382: End
				
				centerX_frame = center_frame
				self.centerXEntry = centerX_frame.entry(label=" X ",width = 8, value = centerX, unit='\[m]').pack(side ='left')
				
				centerY_frame = center_frame
				self.centerYEntry = centerY_frame.entry(label=" Y ",width = 8, value = centerY, unit='\[m]').pack(side ='left')
				
				centerZ_frame = center_frame
				self.centerZEntry = centerZ_frame.entry(label=" Z ",width = 8, value = centerZ, unit='\[m]').pack(side ='left')

				## frame3 Advanced parameters
				self.advanced_activated = False
				#Advanced selection button
				self.advanced_unpack = advanced_frame.button(text=" Advanced >>> ",command = Command(self,MyDialogueCameraRotation.advanced )).pack(side='top',anchor ='w')
				self.advanced_pack = advanced_frame.button(text=" Advanced <<< ",command = Command(self,MyDialogueCameraRotation.advanced ))

				#CameraResolution
				self.resolution_frame = advanced_frame.frame()
				self.resolution_h = self.resolution_frame.entry(label=" Camera resolution  " , value = 1920 , width = 8).pack( side = "left")
				self.resolution_v = self.resolution_frame.entry(label=" x " , value = 1080 , width = 8).pack( side = "left")	
				
				#PicsNumbers
				self.pics_frame = advanced_frame.frame()
				self.picsEntry = self.pics_frame.entry(label=" Number of pictures per rotation " , value = 360 , labelwidth = 29,width = 8).pack( side = "top")

				#frame4
				close  = Frame4.button(text=" Close",command = Command(self,DialogueBox.close) ).pack(side="right",anchor='e')
				apply  = Frame4.button(text=" Rotate ",command = Command(self,MyDialogueCameraRotation.apply ) ).pack(side="right",anchor='e')
				self.showCentered()
	
		# main fonction
		def apply(self):
		  
			try:
				self.Refer_lengthEntry.getFloatValue()
				# AdT #26802 > Begin
				if self.Refer_lengthEntry.getFloatValue() <= 0:
					CFViewWarning('Wrong input value in the entry for reference length. It must be a positive float value.')
					return
				# AdT #26802 > End
				self.heightEntry.getFloatValue()
				self.centerXEntry.getFloatValue()
				self.centerYEntry.getFloatValue()
				self.centerZEntry.getFloatValue()
				self.heightEntry.getFloatValue()
			except ValueError:
				CFViewWarning('Wrong input value in the entry. Must be a float value.')
			Refer_length = self.Refer_lengthEntry.getFloatValue()
			camera_height = self.heightEntry.getFloatValue()
			centerX = self.centerXEntry.getFloatValue()
			centerY = self.centerYEntry.getFloatValue()
			centerZ = self.centerZEntry.getFloatValue()
			
			#check if values are integer
			try:
				self.resolution_h.getIntValue()
				self.resolution_v.getIntValue()
				self.picsEntry.getIntValue()
			except ValueError:
				#Warning('Wrong input value in the entry. Must be an integer value.')
				CFViewWarning('Wrong input value in the entry. Must be an integer value.')
				return
					
			if (self.resolution_h.getIntValue() < 0) or (self.resolution_v.getIntValue() < 0):
				#Warning ('Wrong input value in the entry. Number of pic must be less than 999.')
				CFViewWarning('Wrong input value in the entry. Camera resolution value must be positive')
				return
					
			if (self.picsEntry.getIntValue() > 999) or (self.picsEntry.getIntValue() < 1):
				#Warning ('Wrong input value in the entry. Number of pic must be less than 999.')
				CFViewWarning('Wrong input value in the entry. Number of pic must be in the range of \[1, 999\].')
				return
					  
			resolution_h = self.resolution_h.getIntValue()
			resolution_v = self.resolution_v.getIntValue()
			height = self.heightEntry.getFloatValue()
			nb_theta = self.picsEntry.getIntValue()
					
			#call the function rotation with all the variables
			rotation(Refer_length,camera_height,resolution_h,resolution_v,nb_theta,centerX,centerY,centerZ,self)
				
		# read value in sim_file
		def readSim(self):
			f = open(self.sim_file,'r')
			sim_content=f.readlines()
			f.close()
			line_num = 0
			for line in sim_content:
				line_num += 1
				if line.find('*** REFERENCE LENGTH') >= 0:
					Refer_length = float(sim_content[line_num + 1])
				elif line.find('*** FLUID1-FLUID2 INTERFACE LOCATION') >= 0:
					Free_surface_location = float(sim_content[line_num + 1])
			return Refer_length,Free_surface_location

		#read value in body parameter, center : string list
		def readBodyparameter(self):
			try:
				f = open(self.body_parameter_file,'r')
			except ValueError:
				raise ValueError('The body_param.dat file is missing. This plugin will stop as this file is necessary.')
			body_param_content = f.readlines()
			f.close()
			line_num = 0
			# AdT 160212
			nbr_body = 0
			# AdT #27052 > Begin
			foundCenter = False
			end = 0
			for line in body_param_content:
				if line.find('*** Number of fixed bodies') >= 0:
					nbr_body = int(body_param_content[line_num + 2])
				if line.find('*** Number of moving bodies') >= 0:
					nbr_body = int(body_param_content[line_num + 2]) + nbr_body
				if line.find("Reference point") >= 0:
					center = (body_param_content[line_num + 1]).split()
					foundCenter = True
					break
				line_num +=1
			
			if foundCenter == False:
				CFViewWarning('The body_param.dat file does not contain the reference point. This plugin will stop as this data is necessary.')
				center = []
				end = 1
				#print ' > Coordinates of the reference point: '
				#center = []
				#center.append(raw_input('    Coordinate X: '))
				#center.append(raw_input('    Coordinate Y: '))
				#center.append(raw_input('    Coordinate Z: '))
				#center=[x.strip()for x in center]
			
			return nbr_body,center,end

			# AdT #27052 > End

		def advanced(self):
				#If "advanced" is activated, display the advanced options, display advanced_unpack button instead of advanced_pack button 
				#and set advanced_activated to false
				if self.advanced_activated == True:
					self.advanced_pack.unpack()
					self.advanced_unpack.pack(side='top',anchor ='w')
					self.resolution_frame.unpack()
					self.pics_frame.unpack()
					self.advanced_activated = False
				else:
				#If "advanced" is de-activated, hide the advanced options, display advanced_pack button instead of advanced_unpack button 
				#and set advanced_activated to true
					self.advanced_unpack.unpack()
					self.advanced_pack.pack(side='top',anchor ='w')
					self.resolution_frame.pack(side="top",anchor ='w')
					self.pics_frame.pack(side="top",anchor='w')
					self.advanced_activated = True	

	#rotation
	def rotation(Refer_length,camera_height,resolution_h,resolution_v,nb_theta,centerX,centerY,centerZ,self):
		Xmax = Refer_length         # max coordinate of the boat
		L = Refer_length/4.         # distance behind the boat of the camera
		r = (Refer_length/2.)       # small radius of the ellipse
		R = (r + Refer_length/2 + L)# big radius of the ellipse
		
		view_width = Refer_length*2.
		view_height = Refer_length
		
		#find the picture location and the picture name
		folder = picturefolder(self)
		picture_name = folder[0]
		picture_location = folder[1]
		
		quality = 0 # 0: normal 1: high 2: thin line 3: very thin line

		pic_id = 0

		fps = 12         #ideal is minimum 12 pictures/s for the human eye 
		i = 0
				  
		print ' '
		print ' > Start rotation '
		print ' '
		
		for i in range(nb_theta):
				  
			# Theta is the angle
			theta = i/float(nb_theta)*2.*math.pi 
			#print 'Theta = ' + str(int(theta/math.pi*180))
		  
			# Position of the camera
			x = (Xmax-Refer_length/2.-L/2.+R*math.cos(theta))
			#x = centerX + R*math.cos(theta)
			y = (r*math.sin(theta))
			z = camera_height
			
			# Target point( = gravity center)
			X = centerX 
			Y = centerY
			Z = centerZ

			# define camera
			c.SetCamera(x,y,z,X,Y,Z,0,0,1,view_width,view_height)

			#picture names( < 999)
			if i<10:
					name = picture_name + '00' + str(pic_id) + '.png'
			elif i<100:
					name = picture_name + '0' + str(pic_id) + '.png'
			else:
					name = picture_name + str(pic_id) + '.png'
				  
			# define how to print the picture
			# AdT #26845 > Begin
			c.Print(8,0,1,1,100,resolution_h,resolution_v,0 ,os.path.join(picture_location,name),'',1,0,quality)
			# AdT #26845 > End
			pic_id = pic_id + 1

		print ' > End of the pictures creation '
		# AdT #27053 > Begin
		CFViewWarning('Pictures created in folder ' + str(picture_location))
		print " > Pictures created in folder " + picture_location
		# AdT #27053 > End
		
		print ' '
		print ' > END OF SCRIPT '
		print ' '
			  
	def picturefolder(self):
			  
		#import time and date
		# AdT #26845 > Begin
		time = datetime.datetime.now()
		year = str(time.year)
		month = str(time.month)
		day = str(time.day)
		hour = str(time.hour)
		minute = str(time.minute)
		second = str(time.second)
		# AdT #27053 > Begin
		time = day + '-' + month + '-' + year + '_' + hour + 'h' + '-' + minute + 'm' + '-' +  second + 's'
		# AdT #27053 > End
		
		#create the folder
		# AdT #27053 > Begin
		folder = "Camera_rotation" + "_" + str(time)
		# AdT #27053 > End
		location = os.path.join(self.path,folder)
		# AdT #26845 > End
		
		os.mkdir(location)
		
		picture_name = 'videoFrame_'
		
		return picture_name,location

	z = MyDialogueCameraRotation()