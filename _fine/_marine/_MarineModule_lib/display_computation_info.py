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
#______________________________________________________________________________

import os

from Tk import *

import CFView as cfv

from display_values import *

def Display_computation_info():
  
	print ' '
	print ' > START OF SCRIPT: DISPLAY_COMPUTATION_INFO '
	print ' '

	end = 0
	
	try :
		path = GetProjectPath()
	except Exception:
		CFViewWarning("No project is currently opened. Please press 'OK', open FINE/Marine results in CFView and launch this plugin again.")
		end = 1
	
	if end == 0:	
		print os.path.abspath(__file__)
		project_file = os.listdir(path)
	
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
		end = 1	

	#sim and mvt_file
	if end == 0:
		for i in range(len(project_file)):
			if project_file[i].find(".sim")>=0:
				sim_file = os.path.join(path,project_file[i])
				print " > sim file : " +str(sim_file)
				f = open(sim_file,'r')
				sim_contents = f.readlines()
				f.close()
				line_num = 0
				bodyNameFound = False
				for line in sim_contents:
					if line.find("*** BODY:SOL:MVT IMP:1:NAME")>=0 or line.find("*** BODY:SOL:MVT PFD:1:NAME")>=0:
						bodyNameFound = True
						body_name = (sim_contents[line_num + 2])[:-1]
						mvt_file = os.path.join(path,"Mvt_" + body_name + ".dat")
						print " > Mvt_file : " +str(mvt_file)
						break
					line_num += 1
				if bodyNameFound == False:
					CFViewWarning(" .sim file does not contain the name of the body, impossible to proceed. ")
					end = 1
	
	if end == 0:
		if (os.path.exists(sim_file) == 0):
			CFViewWarning(" .sim file is not present, impossible to read values. ")
			end = 1
		if (os.path.exists(mvt_file) == 0):
			CFViewWarning(" Mvt_ file is not present, impossible to read values. ")
			end = 1
		
	#create Display_Position.txt and write in it
	def writeDisplay(position,Efforts,Motions, number_of_cells, actuator_disk):
		
		Display_Input = {'Position': str(position)}
		Display_Input = dict(Display_Input.items() + {'Fx': str(Efforts[0]), 'Fy': str(Efforts[1]), 'Fz': str(Efforts[2])}.items())
		Display_Input = dict(Display_Input.items() + {'Mx': str(Efforts[3]), 'My': str(Efforts[4]), 'Mz': str(Efforts[5])}.items())
		Display_Input = dict(Display_Input.items() + {'FxP': str(Efforts[6]), 'FyP': str(Efforts[7]), 'FzP': str(Efforts[8])}.items())
		Display_Input = dict(Display_Input.items() + {'MxP': str(Efforts[9]), 'MyP': str(Efforts[10]), 'MzP': str(Efforts[11])}.items())
		Display_Input = dict(Display_Input.items() + {'FxV': str(Efforts[12]), 'FyV': str(Efforts[13]), 'FzV': str(Efforts[14])}.items())
		Display_Input = dict(Display_Input.items() + {'MxV': str(Efforts[15]), 'MyV': str(Efforts[16]), 'MzV': str(Efforts[17])}.items())
		Display_Input = dict(Display_Input.items() + {'Tx0': str(Motions[0]), 'Ty0': str(Motions[1]), 'Tz0': str(Motions[2])}.items())
		Display_Input = dict(Display_Input.items() + {'Rx2': str(Motions[3]), 'Ry1': str(Motions[4]), 'Rz0': str(Motions[5])}.items())
		Display_Input = dict(Display_Input.items() + {'Vx': str(Motions[6]), 'Vy': str(Motions[7]), 'Vz': str(Motions[8])}.items())
		Display_Input = dict(Display_Input.items() + {'Ax': str(Motions[9]), 'Ay': str(Motions[10]), 'Az': str(Motions[11])}.items())
		Display_Input = dict(Display_Input.items() + {'Number of cells': str(number_of_cells)}.items())
		Display_Input = dict(Display_Input.items() + {'Thrust': str(actuator_disk[0]), 'Torque': str(actuator_disk[1])}.items())
		
		return Display_Input

	if end == 0:
		class MyDialogue(DialogueBox):
			def __init__(self):
				
				DialogueBox.__init__(self, "Display" )

				#definition of the main frames
				
				# Frame1 : display position
				Frame1 = self.labelframe('Display position').pack(side = "top", anchor = "w", fill ='x')
					
				A1_frame = Frame1.frame().pack(side="left",anchor = "w")
				B1_frame = Frame1.frame().pack(side="left",anchor = "w")
				C1_frame = Frame1.frame().pack(side="left",anchor = "w")
					
				#Frame2 efforts
				# AdT 160211 Bug #26118: Effort changed to Efforts
				Frame2 = self.labelframe(" Efforts ").pack(side ="top",anchor="w", fill ='x')
				
				FrameA2 = Frame2.frame().pack(side="left",anchor="w")
				FrameB2 = Frame2.frame().pack(side="left",anchor="w")
				FrameC2 = Frame2.frame().pack(side="left",anchor="w")
				FrameD2 = Frame2.frame().pack(side="left",anchor="w")
				FrameE2 = Frame2.frame().pack(side="left",anchor="w")
				FrameF2 = Frame2.frame().pack(side="left",anchor="w")
					
				#frame3 motions
				Frame3 = self.labelframe(" Motions ").pack(side='top',anchor='w', fill = 'x')
					
				FrameA3 = Frame3.frame().pack(side="left",anchor="w")
				FrameB3 = Frame3.frame().pack(side="left",anchor="w")
				FrameC3 = Frame3.frame().pack(side="left",anchor="w")
				FrameD3 = Frame3.frame().pack(side="left",anchor="w")
				FrameE3 = Frame3.frame().pack(side="left",anchor="w")
				FrameF3 = Frame3.frame().pack(side="left",anchor="w")
				FrameG3 = Frame3.frame().pack(side='top',anchor='w')
					
				#Frame4 others
				thrust_activated = 0
				torque_activated = 0
				
				try :
					f = open(sim_file[:-3] + 'std','r')
					std_contents = f.readlines()
					f.close()
					for i in std_contents:
						line = i.split()
						if 'Imposed' in line and 'thrust' in line:
							thrust_activated = 1
						if 'Imposed' in line and 'torque' in line:
							torque_activated = 1
				except IOError:
					  CFViewWarning('The file ' +str(sim_file[:-3]) + ".std isn't present, it will be impossible to read actuator disk values.")
				
				if os.path.exists(os.path.join(path,'nb_cell.dat')) == 1 or thrust_activated == 1:
					Frame4 = self.labelframe('Others').pack(side="top",anchor="w",fill='x')
				#Frame5 button
				Frame5 = self.frame().pack(side="top",anchor="e",fill='x')
						
				#frame 1 : text localisation
				self.selecConfig = Variable(0)
				A1_frame.radiobutton(" Up-Left ", self.selecConfig, value=0).pack(side="top",anchor="w")
				B1_frame.radiobutton(" Up-Center ", self.selecConfig, value=1).pack(side="top",anchor="w")
				C1_frame.radiobutton(" Up-Right ", self.selecConfig, value=2).pack(side="top",anchor="w")
				A1_frame.radiobutton(" Down-Left ", self.selecConfig, value=3).pack(side="top",anchor="w")
				B1_frame.radiobutton(" Down-Center ", self.selecConfig, value=4).pack(side="top",anchor="w")
				C1_frame.radiobutton(" Down-Right ", self.selecConfig, value=5).pack(side="top",anchor="w")
					
				#frame2 efforts
				self.Fx_button = FrameA2.checkbutton(" Fx ",initValue = 0).pack(side = "top",anchor = "w")
				self.Fy_button = FrameB2.checkbutton(" Fy ",initValue = 0).pack(side = "top",anchor = "w")
				self.Fz_button = FrameC2.checkbutton(" Fz ", initValue = 0).pack(side = "top",anchor = "w")
				self.Mx_button = FrameD2.checkbutton(" Mx ",initValue = 0).pack(side = "top",anchor = "w")
				self.My_button = FrameE2.checkbutton(" My ",initValue = 0).pack(side = "top",anchor = "w")
				self.Mz_button = FrameF2.checkbutton(" Mz ", initValue = 0).pack(side = "top",anchor = "w")
				self.FxP_button = FrameA2.checkbutton(" FxP",initValue = 0).pack(side = "top",anchor = "w")
				self.FyP_button = FrameB2.checkbutton(" FyP",initValue = 0).pack(side = "top",anchor = "w")
				self.FzP_button = FrameC2.checkbutton(" FzP", initValue = 0).pack(side = "top",anchor = "w")
				self.MxP_button = FrameD2.checkbutton(" MxP",initValue = 0).pack(side = "top",anchor = "w")
				self.MyP_button = FrameE2.checkbutton(" MyP",initValue = 0).pack(side = "top",anchor = "w")
				self.MzP_button = FrameF2.checkbutton(" MzP", initValue = 0).pack(side = "top",anchor = "w")
				self.FxV_button = FrameA2.checkbutton(" FxV",initValue = 0).pack(side = "top",anchor = "w")
				self.FyV_button = FrameB2.checkbutton(" FyV",initValue = 0).pack(side = "top",anchor = "w")
				self.FzV_button = FrameC2.checkbutton(" FzV", initValue = 0).pack(side = "top",anchor = "w")
				self.MxV_button = FrameD2.checkbutton(" MxV",initValue = 0).pack(side = "top",anchor = "w")
				self.MyV_button = FrameE2.checkbutton(" MyV",initValue = 0).pack(side = "top",anchor = "w")
				self.MzV_button = FrameF2.checkbutton(" MzV", initValue = 0).pack(side = "top",anchor = "w")
					
				#frame3 motions
				#all the motions are desactivated to avoid multiple frames
				Tx0_activated = 0
				Ty0_activated = 0
				Tz0_activated = 0
				Rx2_activated = 0
				Ry1_activated = 0
				Rz0_activated = 0
				Vx_activated = 0
				Vy_activated = 0
				Vz_activated = 0
				Ax_activated = 0
				Ay_activated = 0
				Az_activated = 0
				
				try:
					f = open(mvt_file,"r")
					mvt_contents = f.readlines()
					f.close()
				except IOError:
					CFViewWarning(' Mvt_ file is not present, impossible to read values. ')
				
				for i in mvt_contents:
					#active the motions if they can be select
					if i.find("Tx0") > 0 and Tx0_activated == 0:
						self.Tx0_button = FrameA3.checkbutton(" Tx0 ",initValue = 0).pack(side = "top",anchor = "w")
						Tx0_activated = 1
							
					if i.find("Ty0") > 0 and Ty0_activated ==0:
						self.Ty0_button = FrameB3.checkbutton(" Ty0 ",initValue = 0).pack(side = "top",anchor = "w")
						Ty0_activated = 1
						
					if i.find("Tz0") > 0 and Tz0_activated == 0:
						self.Tz0_button = FrameC3.checkbutton(" Tz0 ", initValue = 0).pack(side = "top",anchor = "w")
						Tz0_activated = 1
						
					if i.find("Rx2") > 0 and Rx2_activated == 0:
						self.Rx2_button = FrameD3.checkbutton(" Rx2 ",initValue = 0).pack(side = "top",anchor = "w")
						Rx2_activated = 1
							
					if i.find("Ry1") > 0 and Ry1_activated ==0:
						self.Ry1_button = FrameE3.checkbutton(" Ry1 ",initValue = 0).pack(side = "top",anchor = "w")
						Ry1_activated = 1
							
					if i.find("Rz0") > 0 and Rz0_activated ==0:
						self.Rz0_button = FrameF3.checkbutton(" Rz0 ", initValue = 0).pack(side = "top",anchor = "w")
						Rz0_activated = 1
						
					if i.find("Vx") > 0 and Vx_activated ==0:
						self.Vx_button = FrameA3.checkbutton(" Vx ",initValue = 0).pack(side = "top",anchor = "w")
						Vx_activated = 1
						
					if i.find("Vy") > 0 and Vy_activated ==0:
						self.Vy_button = FrameB3.checkbutton(" Vy ",initValue = 0).pack(side = "top",anchor = "w")
						Vy_activated = 1
						
					if i.find("Vz") > 0 and Vz_activated ==0:	
						self.Vz_button = FrameC3.checkbutton(" Vz ", initValue = 0).pack(side = "top",anchor = "w")
						Vz_activated = 1
						
					if i.find("Ax") > 0 and Ax_activated ==0:
						self.Ax_button = FrameD3.checkbutton(" Ax ",initValue = 0).pack(side = "top",anchor = "w")
						Ax_activated = 1
							
					if i.find("Ay") > 0 and Ay_activated ==0:	
						self.Ay_button = FrameE3.checkbutton(" Ay ",initValue = 0).pack(side = "top",anchor = "w")
						Ay_activated = 1
						
					if i.find("Az") > 0 and Az_activated ==0:	
						self.Az_button = FrameF3.checkbutton(" Az ", initValue = 0).pack(side = "top",anchor = "w")
						Az_activated = 1
					
				#frame4: Others
				if os.path.exists(os.path.join(path,'nb_cell.dat')) == 1:
					# AdT 160211 Bug #26118: Cells changed to cells
					self.Number_of_cells_button = Frame4.checkbutton(" Number of cells ",initValue = 0).pack(side = "top",anchor = "w")
					
				if thrust_activated == 1:
					# AdT 160211 Bug #26118: Actuator Disk changed to Actuator disk
					self.actuator_disk =  Frame4.label(text =' Actuator disk ').pack(side = 'top', anchor = "w")
					self.thrust_button = Frame4.checkbutton(" Thrust ",initValue = 0).pack(side = "left",anchor = "w")
				if torque_activated == 1:
					self.torque_button = Frame4.checkbutton(" Torque ",initValue = 0).pack(side = "left",anchor = "w")
					
				#frame5
				close  = Frame5.button(text=" Close",command = Command(self,DialogueBox.close))
				apply  = Frame5.button(text=" Display ",command = Command(self,MyDialogue.apply))
				delete = Frame5.button(text=" Delete text",command = Command(self,MyDialogue.deleteText))
				close.pack(side="right")
				apply.pack(side="right")
				delete.pack(side="right")

				self.showCentered()
			
			#delete text
			def deleteText(self):
				cfv.DeleteText('display')
			
			# main fonction
			def apply(self):
				position = self.selecConfig.getValue()
				Efforts = (self.Fx_button.getState(),self.Fy_button.getState(),self.Fz_button.getState(),self.Mx_button.getState(),self.My_button.getState(),self.Mz_button.getState(),self.FxP_button.getState(),self.FyP_button.getState(),self.FzP_button.getState(),self.MxP_button.getState(),self.MyP_button.getState(),self.MzP_button.getState(),self.FxV_button.getState(),self.FyV_button.getState(),self.FzV_button.getState(),self.MxV_button.getState(),self.MyV_button.getState(),self.MzV_button.getState())
					
				#check if the motions exist
				try :
					self.Tx0 = self.Tx0_button.getState()
				except Exception:
					self.Tx0 = 0
				try :
					self.Ty0 = self.Ty0_button.getState()
				except Exception:
					self.Ty0 = 0
				try :
					self.Tz0 = self.Tz0_button.getState()
				except Exception:
					self.Tz0 = 0
				try :
					self.Rx2 = self.Rx2_button.getState()
				except Exception:
					self.Rx2 = 0
				try :
					self.Ry1 = self.Ry1_button.getState()
				except Exception:
					self.Ry1 = 0
				try :
					self.Rz0 = self.Rz0_button.getState()
				except Exception:
					self.Rz0 = 0
				try :
					self.Vx = self.Vx_button.getState()
				except Exception:
					self.Vx = 0
				try :
					self.Vy = self.Vy_button.getState()
				except Exception:
					self.Vy = 0
				try :
					self.Vz = self.Vz_button.getState()
				except Exception:
					self.Vz = 0
				try :
					self.Ax = self.Ax_button.getState()
				except Exception:
					self.Ax = 0
				try :
					self.Ay = self.Ay_button.getState()
				except Exception:
					self.Ay = 0
				try :
					self.Az = self.Az_button.getState()
				except Exception:
					self.Az = 0
						
				Motions = (self.Tx0,self.Ty0,self.Tz0,self.Rx2,self.Ry1,self.Rz0,self.Vx,self.Vy,self.Vz,self.Ax,self.Ay,self.Az)
					
				try :
					number_of_cells = self.Number_of_cells_button.getState()
				except Exception:
					number_of_cells = 0
				
				try :
					self.thrust = self.thrust_button.getState()
				except Exception:
					self.thrust = 0
				try:
					self.torque = self.torque_button.getState()
				except Exception:
					self.torque = 0
					
				actuator_disk = (self.thrust,self.torque)
					
				#write the position, efforts, motions, number of cells and actuator disk
				Display_Input = writeDisplay(position,Efforts,Motions,number_of_cells,actuator_disk)
				#self.close()
				
				path = GetProjectPath()
				project_name = GetProjectName()
				project_file = os.listdir(path)

				end = nbBody(project_name)

				#sim and mvt_file
				if end == 0:
					file_exist = 0
					for i in range(len(project_file)):
						if project_file[i].find(".sim")>=0:
							sim_file = os.path.join(path,project_file[i])
							f = open(sim_file,'r')
							sim_contents = f.readlines()
							f.close
							line_num = 0
							for line in sim_contents:
								if line.find("*** BODY:SOL:MVT IMP:1:NAME")>=0 or line.find("*** BODY:SOL:MVT PFD:1:NAME")>=0:
									body_name = (sim_contents[line_num + 2])[:-1]
									file_exist = 1
									mvt_file = os.path.join(path,"Mvt_" + body_name + ".dat")
									break
								line_num += 1

					if file_exist == 0:
						CFViewWarning('Files are missing, impossible to read values. ')
						end = 1
	
					position = readPosition(Display_Input)
					main(position,path,project_name,Display_Input,mvt_file,sim_file)

		z = MyDialogue()