#                                                                             #
#                     Self Propulsion Dynamic Library                         #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : L. Clous
#	Creation Date : 17/04/2014
#	Last modified : 24/02/2017
#______________________________________________________________________________
#
# Description: Self Propulsion Dynamic Library for FINE/Marine
#______________________________________________________________________________
# Revisions:
#
#  DATE		IMPLEMENTATOR	TYPE OF MODIFICATION
#------------------------------------------------------------------------------
#
# 24/02/17	Anna Mir		#28113, #28114 change identification of SP mode
# 28/11/18  Anna Mir		#22364 add check for 2D cases
#______________________________________________________________________________

#!/bin/python

# for get_numeca_dir_
from IGGSystem import *

# for TCL windows
from Tk import *
import string

# for classic commands
import os,sys,math,fileinput,string,platform,shutil

# for FineMarine
import FM

pad=1
	
class selfPropulsionWizard(DialogueBox):
	OutputFileName = ''
	
	def __init__(self,name=""):
		DialogueBox.__init__(self,name)
		self.show()
		self.pages = []
		self.curPageIndex = -1
		self.curPageFrame = -1
		self.frames = {}
		self.mainFrame = self.frame()
		self.mainFrame.pack(side="top",fill="both")
		
	def addPage(self,page):
		self.pages.append(page)

	def addButtons(self):

		buttonsFrame = self.frame()
		buttonsFrame.pack(side="bottom",anchor = "se" , expand = "yes" )
		
		self.prev = buttonsFrame.button(text="<< Back", command = Command(self, selfPropulsionWizard.gotoPreviousPage))
		self.next = buttonsFrame.button(text="Next >>", command = Command(self, selfPropulsionWizard.gotoNextPage))
		self.closeB = buttonsFrame.button(text="Cancel", command = Command(self, DialogueBox.close))
		self.applyB = buttonsFrame.button(text="Confirm", command = Command(self, selfPropulsionWizard.apply))

		self.next.pack(side="right")
		self.closeB.pack(side="left")

	def startWizard(self):
		if len(self.pages) == 0:
			raise "No page in Wizard"
		self.gotoNextPage()
		self.show()

	def gotoNextPage(self):

		nextPageIndex = self.curPageIndex + 1

		if self.curPageIndex != -1 and nextPageIndex < len(self.pages):
			self.frames[self.curPageIndex].unpack()

		if nextPageIndex < len(self.pages):
			self.curPageIndex = nextPageIndex

		if self.curPageIndex in self.frames:
			curPageFrame = self.frames[self.curPageIndex]
		else:
			curPageFrame = self.pages[self.curPageIndex](self.mainFrame)
			self.frames[self.curPageIndex] = curPageFrame
			curPageFrame.pack(side="top",fill="both")

		if self.curPageIndex == len(self.pages) - 1:
			self.next.unpack()
			self.applyB.pack(side="right")
			self.prev.pack(side="left")
		
		if self.curPageIndex == 1:
			checkValue = self.checkSetup()
			if checkValue == -1:
				self.close()
			else:
				print " > Checking setup correct."
				self.sentence.unpack()
				if self.tmp_comp_choice.getValue() == "1":
					self.sentence = self.content.label("Fixed vessel speed, solved RPM").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				elif self.tmp_comp_choice.getValue() == "2":
					self.sentence = self.content.label("Fixed RPM, solved vessel speed").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				elif self.tmp_comp_choice.getValue() == "3":
					self.sentence = self.content.label("Fixed power (DHP), solved RPM and vessel speed").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				elif self.tmp_comp_choice.getValue() == "4":
					self.sentence = self.content.label("Fixed power (THP), solved vessel speed with actuator disk").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				self.advanced_unpack.pack()
				self.advanced_pack.unpack()
				
				self.motion_type()
				self.wrench_frame.unpack()
				self.power_frame.unpack()
				self.RPM_frame.unpack()
				self.rot_sign_frame.unpack()
				self.diam_ad_frame.unpack()
				self.diam_prop_frame.unpack()
				if self.Fixed:
					self.wrench_frame.pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				if self.tmp_comp_choice.getValue() == "3" or self.tmp_comp_choice.getValue() == "4":
					self.power_frame.pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
					self.RPM_frame.pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				if self.tmp_comp_choice.getValue() != "4":
					self.rot_sign_frame.pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
					self.diam_prop_frame.pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				else:
					self.diam_ad_frame.pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
				
	def gotoPreviousPage(self):

		previousPageIndex = self.curPageIndex - 1

		if self.curPageIndex != -1 and previousPageIndex >= 0:
			self.frames[self.curPageIndex].unpack()

		if previousPageIndex >= 0:
			self.curPageIndex = previousPageIndex
			
		if self.curPageIndex in self.frames:
			curPageFrame = self.frames[self.curPageIndex]
			curPageFrame.pack()
		else:
			curPageFrame = self.pages[self.curPageIndex]( self.mainFrame )
			self.frames[self.curPageIndex] = curPageFrame
			curPageFrame.pack(side="top",fill="both")
			self.applyB.unpack()
			self.next.pack(side="right")
			self.prev.unpack()
			
		if self.curPageIndex != 1:
			self.advanced_unpack.unpack()
			self.advanced_pack.unpack()
			self.thrust_coefFrame.unpack()
			self.advance_coefFrame.unpack()
			self.control_actFrame.unpack()
			self.limit_actFrame.unpack()
			self.max_var_omFrame.unpack()
			self.max_var_vsFrame.unpack()
			self.advanced_activated = False
			
	def checkSetup(self):
		print " > Checking FM setup..."
	
		self.body_def() # Get ship and prop bodies
		try:
			print " > Detected ship body: " + self.shipName
		except:
			Warning("Could not detect a ship, make sure it is set with imposed Tx")
			print " > Could not detect a ship, make sure it is set with imposed Tx"

		setupcheck = 0
		realBodyList = []
		shipMotionType = FM.get_body_motion_type(self.ship)
		shipMotionLaw = get_body_motion_law(self.ship)	
				
		# SP with propeller
		# Check number of bodies is correct
		if self.tmp_comp_choice.getValue() in ["1","2","3"]:
			try:
				print " > Detected propeller body: " + self.propName
			except:
				Warning("Could not detect a propeller, make sure it is set with a pin connection")
				print " > Could not detect a propeller, make sure it is set with a pin connection"
				setupcheck = -1

			for body in FM.get_body_list():
				if 'sliding_patches_' not in body[1].lower():
					realBodyList.append(body)
			if len(realBodyList) == 0 :
				Warning("No body detected.")
				print " > No body detected."
				setupcheck = -1
			elif len(realBodyList) == 1 :
				Warning("One body detected. At least one ship and propeller are needed for this type of self-propulsion")
				print " > One body detected. At least one ship and propeller are needed for this type of self-propulsion"
				setupcheck = -1
			
			# Check body motions are correct						
			if setupcheck == 0:
				propMotionType = FM.get_body_motion_type(self.prop)
				propMotionLaw = get_body_motion_law(self.prop)
				#1) Ship Tx imposed, prop Rx Imposed DL
				if self.tmp_comp_choice.getValue() == "1":
					if shipMotionType[0] != 'Imposed' or propMotionLaw[3] != 'Dynamic library':
						setupcheck = -1
						Warning("Ship Tx motion needs to be Imposed and propeller rotation needs to be Imposed > Dynamic Library")
						print " > Ship Tx motion needs to be Imposed and propeller rotation needs to be Imposed > Dynamic Library"
				
				#2) Ship Tx DL, prop Rx imposed
				elif self.tmp_comp_choice.getValue() == "2":
					if shipMotionLaw[0] != 'Dynamic library' or propMotionType[3] != 'Imposed':
						setupcheck = -1
						Warning("Ship Tx motion needs to be Imposed > Dynamic library and propeller rotation needs to be Imposed")
						print " > Ship Tx motion needs to be Imposed > Dynamic library and propeller rotation needs to be Imposed"

				#3) Both Imposed DL
				elif self.tmp_comp_choice.getValue() == "3":
					if shipMotionLaw[0] != 'Dynamic library' or propMotionLaw[3] != 'Dynamic library':
						Warning("Ship and propeller motions both need to be Imposed > Dynamic library")
						print " > Ship and propeller motions both need to be Imposed > Dynamic library"
						setupcheck = -1
		
		# SSP with Actuator Disk
		if self.tmp_comp_choice.getValue() == "4":
			numAD = int(get_actuator_disk_list()[0])
			typeAD = get_actuator_disk_force_distribution()
			if numAD == 0:
				Warning("Please set up an actuator disk if you want to use the Actuator disk mode")
				print " > Please set up an actuator disk if you want to use the Actuator disk mode."
				setupcheck = -1
			elif numAD > 1:
				Warning(str(numAD) + " actuator disks detected. Only one actuator disk is allowed")
				print " > " + str(numAD) + " actuator disks detected. Only one actuator disk is allowed."
				setupcheck = -1
			if numAD == 1 and typeAD != "PROPELLER CODE":
				Warning("The actuator disk force distribution should be PROPELLER CODE")
				print " > The actuator disk force distribution should be PROPELLER CODE."
				setupcheck = -1
			
			if shipMotionLaw[0] != 'Dynamic library':
				setupcheck = -1
				Warning("Ship Tx motion needs to be Imposed > Dynamic library ")
				print " > Ship Tx motion needs to be Imposed > Dynamic library "

		return setupcheck

	def apply(self):
		
		self.motion_type()
				
		try:
			if self.tmp_comp_choice.getValue() != '4':
				self.diam_prop.getFloatValue()
			else:
				self.diam_ad.getFloatValue()
			if self.tmp_comp_choice.getValue() == '3' or self.tmp_comp_choice.getValue() == "4":
				self.power.getFloatValue()
				self.RPM.getFloatValue()
			if self.tmp_comp_choice.getValue() == '2' or self.tmp_comp_choice.getValue() == '3' or self.tmp_comp_choice.getValue() == "4":
				self.advance_coef.getFloatValue()
			self.thrust_coef.getFloatValue()
			if self.tmp_comp_choice.getValue() == '1' or self.tmp_comp_choice.getValue() == '3':
				self.max_var_om.getFloatValue()
			if self.tmp_comp_choice.getValue() == '2' or self.tmp_comp_choice.getValue() == '3' or self.tmp_comp_choice.getValue() == "4":
				self.max_var_vs.getFloatValue()
			self.control_act.getIntValue()
			self.limit_act.getIntValue()
			if self.Fixed == True :
				self.wrench.getFloatValue()
			
		except ValueError:
			Warning("Wrong input value in at least one entry. Please check that all values are float or integer.")
			return
			
		if self.thrust_coef.getFloatValue() <= 0.0 or self.advance_coef.getFloatValue() <= 0.0 :
			Warning("Wrong input value for thrust or advance coefficient. Must be >0.")
			return
			
		if self.control_act.getIntValue() < 1 :
			Warning("Number of time steps before the controller is activated must be >=1.")
			return
			
		if self.limit_act.getIntValue() < 1 :
			Warning("Check number of time steps before the limiter is activated.")
			return
			
		if self.max_var_om.getFloatValue() <= 0.0 or self.max_var_vs.getFloatValue() <= 0.0 :
			Warning("Maximum variations must be >0.")
			return
			
		if self.tmp_comp_choice.getValue() != '4':
			if self.diam_prop.getFloatValue() <= 0.0 :
				Warning("Propeller diameter must be >0.")
				return
		else:
			if self.diam_ad.getFloatValue() <= 0.0 :
				Warning("Actuator disk outer diameter must be >0.")
				return

		if (self.tmp_comp_choice.getValue() == '3' or self.tmp_comp_choice.getValue() == "4") and self.power.getFloatValue() <= 0.0 :
			Warning("Power must be >0.")
			return
			 
		if (self.tmp_comp_choice.getValue() == '3' or self.tmp_comp_choice.getValue() == "4") and self.RPM.getFloatValue() <= 0.0 :
			Warning("Estimated propeller rotational speed must be >0.")
			return
		
		# find computation directory
		project_path,project_name = FM.get_project_file_name()
		project_name = project_name[:project_name.rfind(".")]
		comp_index = FM.get_active_computation()
		comp_name = FM.get_computation_name(comp_index)
		complete_path = os.path.join(project_path,project_name + "_" + comp_name)
		
		if os.path.isdir(complete_path):
		
			# write SPinputs.dat
			f = open(os.path.join(complete_path,"SPinputs.dat"),"w")
			f.write("*-------------------- S E L F     P R O P U L S I O N ------------------------------\n")
			f.write("*-- Dynamic library\n")
			f.write("*-- this file must be saved in the computation directory with isis_dynamic_library.so or isis_dynamic_library.dll\n")
			f.write("*-- Mandatory input parameters\n")
			f.write("*** Type of self propulsion computation  1:Fixed vessel speed, 2:Fixed propeller rotational velocity, 3:Fixed power, 4:Fixed power with actuator disk\n* \n")
			f.write(self.tmp_comp_choice.getValue()+' \n*')
			f.write("\n*** Name of the vessel\n* \n")
			f.write(self.shipName +' \n*')
			if self.tmp_comp_choice.getValue() != "4":
				f.write("\n*** Name of the propeller\n* \n")
				f.write(self.propName +' \n* ')
			if self.tmp_comp_choice.getValue() == "4":
				f.write("\n*** Outer diameter of the actuator disk [m]\n* \n")
				f.write(str(self.diam_ad.getFloatValue())+' \n*')
			else:
				f.write("\n*** Diameter of the propeller [m]\n* \n")
				f.write(str(self.diam_prop.getFloatValue())+' \n*')
			f.write("\n*** Water density [kg/m**3]\n* \n")
			f.write(str(FM.get_fluid_density(1))+' \n*')
			if self.tmp_comp_choice.getValue() != "4":
				f.write("\n*** Thrust is positive when Omega is positive: 1=true; -1=false \n* \n")
				f.write(self.tmp_rot_sign.getValue()+' \n*')
			f.write("\n*** Additional constant wrench applied along the x axis [N]\n* \n")
			if self.Fixed == True :
				f.write(str(self.wrench.getFloatValue()) +' \n*')
			else :
				f.write(str(FM.get_solved_motion_wrench_parameters(self.ship)[1])+' \n*')
			if self.tmp_comp_choice.getValue() == '1':
				f.write("\n*** Vessel speed [m/s] \n* \n")
				if FM.get_body_motion_law(self.ship) == 'Constant':
					#AdT 26643
					f.write(str(FM.get_body_motion_parameters(self.ship,'Tx')[0])+' \n*')
				else:
					#AdT 26643
					f.write(str(FM.get_body_motion_parameters(self.ship,'Tx')[3])+' \n*')
			elif self.tmp_comp_choice.getValue() == '2':
				f.write("\n*** Propeller rotational velocity [rad/s] \n* \n")
				if FM.get_body_motion_law(self.prop) == 'Constant':
					#AdT 26643
					f.write(str(FM.get_body_motion_parameters(self.prop,'Rn')[0])+' \n*')
				else:
					#AdT 26643
					f.write(str(FM.get_body_motion_parameters(self.prop,'Rn')[3])+' \n*')
			elif self.tmp_comp_choice.getValue() == '3':
				f.write("\n*** Propeller rotational velocity [rad/s] \n* \n")
				f.write(str(self.RPM.getFloatValue())+'\n*')
				f.write("\n*** Power of the propeller (DHP) [W] \n* \n")
				f.write(str(self.power.getFloatValue())+'\n*')
			else:
				f.write("\n*** Estimated propeller rotational velocity [rad/s] \n* \n")
				f.write(str(self.RPM.getFloatValue())+'\n*')
				f.write("\n*** Power of the propeller (THP) [W] \n* \n")
				f.write(str(self.power.getFloatValue())+'\n*')
			f.write("\n*-- Expert input parameters")
			f.write("\n*** Estimated thrust coefficient of the propeller at operating point Kt=Thrust/(rhow*Omega**2*D**4) [-] Thrust in [N] and Omega in [rps] \n* \n")
			f.write(str(self.thrust_coef.getFloatValue())+'\n*')
			if self.tmp_comp_choice.getValue() != '1':
				f.write("\n*** Estimated advance coefficient at operating point J=Vship/(Omega*D) [-] Vship in [m/s] and Omega in [rps] \n* \n")
				f.write(str(self.advance_coef.getFloatValue())+'\n*')
			f.write("\n*** Number of time steps before the controller is activated \n* \n")
			f.write(str(self.control_act.getIntValue())+'\n*')
			f.write("\n*** Number of time steps before the limiter is activated \n* \n")
			f.write(str(self.limit_act.getIntValue())+'\n*')
			if self.tmp_comp_choice.getValue() == '1' or self.tmp_comp_choice.getValue() == '3' :
				f.write("\n*** Maximum variation of Omega between two consecutive time steps n and n+1 when limiter is activated. Expressed in percentage of the value of omega at time step n \n* \n")
				f.write(str(self.max_var_om.getFloatValue())+'\n*')
			if self.tmp_comp_choice.getValue() == '2' or self.tmp_comp_choice.getValue() == '3' or self.tmp_comp_choice.getValue() == '4':
				f.write("\n*** Maximum variation of vessel speed between two consecutive time steps n and n+1 when limiter is activated. Expressed in percentage of the value of omega at time step n \n* \n")
				f.write(str(self.max_var_vs.getFloatValue())+'\n*')
			
			f.close()
			self.close()
			
			print ''
			print ' > SPinputs.dat file has been written in the computation directory. '
			# AdT: Bug correction #27448 both in LINUX and WINDOWS 
			if sys.platform=='win32':
				print ' > Dynamic library isis_dynamic_lib.dll file has been copied into the computation directory. '
			else:
				print ' > Dynamic library isis_dynamic_lib.so file has been copied into the computation directory. '
			print ''
			
			# AdT: Bug correction #27448 both in LINUX and WINDOWS 
			path2DynLib = os.path.join(get_numeca_dir_(),'_data','isis','dynamic_lib')
			if self.tmp_comp_choice.getValue() != '4':
				path2DynLib = os.path.join(path2DynLib,'SP_sliding_grids')
				if sys.platform=='win32':
					path2DynLib = os.path.join(path2DynLib,'win64','isis_dynamic_lib.dll')
				else:
					path2DynLib = os.path.join(path2DynLib,'linux64','isis_dynamic_lib.so')
			else:
				path2DynLib = os.path.join(path2DynLib,'SP_actuator_disk')
				if sys.platform=='win32':
					path2DynLib = os.path.join(path2DynLib,'win64','isis_dynamic_lib.dll')
				else:
					path2DynLib = os.path.join(path2DynLib,'linux64','isis_dynamic_lib.so')
			
			if sys.platform=='win32':
				shutil.copyfile(path2DynLib,os.path.join(complete_path,'isis_dynamic_lib.dll'))
			else:
				shutil.copyfile(path2DynLib,os.path.join(complete_path,'isis_dynamic_lib.so'))
			
		else :
			Warning("Computation directory does not exit. SPinputs.dat can not be written.")
			return


class MyDialogue(selfPropulsionWizard):
	def __init__(self):
		selfPropulsionWizard.__init__(self, "Self-Propulsion Dynamic Library")

		# 22364 close properly if it is a 2d case
		if self.check_2d():
			return

		self.addPage(self.general_page)
		self.addPage(self.mode_page)
		self.addButtons()
		self.startWizard()
		self.showCentered()
		
	def general_page(self,parentFrame):
		self.general_page_frame = parentFrame.frame()
		self.general_page_frame.pack(side="top",fill="both")
		
		### Define type of self-propulsion computation
		self.comp_frame = self.general_page_frame.labelframe(label="Type of self-propulsion")
		self.comp_frame.pack(side="top",fill="x",padx = pad, pady = pad)
		
		#28114 User choice between propeller and AD
		self.spType = Variable(1)
		spTypeProp = self.comp_frame.radiobutton("Propeller", self.spType, value=1, command = Command(self, MyDialogue.updateType)).pack(side="top", anchor = 'w',padx=pad,pady=pad)
		self.comp_frame2 = self.comp_frame.labelframe("Mode")
		self.comp_frame2.pack(side="top", anchor = 'w',padx=pad,pady=pad)
		spTypeAD = self.comp_frame.radiobutton("Actuator Disk", self.spType,value=2,command = Command(self, MyDialogue.updateType)).pack(side="top", anchor = 'w',padx=pad,pady=pad)
		self.comp_frame3 = self.comp_frame.labelframe("Mode")
		self.comp_frame3.pack(side="top", anchor = 'w',padx=pad,pady=pad)

		self.tmp_comp_choice = Variable(1)
		self.tmp_comp_choice_1 = self.comp_frame2.radiobutton("Fixed vessel speed, solved RPM                               ",self.tmp_comp_choice, value=1).pack(side="top", anchor = 'w',padx=pad,pady=pad)
		self.tmp_comp_choice_2 = self.comp_frame2.radiobutton("Fixed RPM, solved vessel speed                               ",self.tmp_comp_choice, value=2).pack(side="top", anchor = 'w',padx=pad,pady=pad)
		self.tmp_comp_choice_3 = self.comp_frame2.radiobutton("Fixed power (DHP), solved RPM and vessel speed             ",self.tmp_comp_choice, value=3).pack(side="top", anchor = 'w',padx=pad,pady=pad)
		self.tmp_comp_choice_4 = self.comp_frame3.radiobutton("Fixed power (THP), solved vessel speed with actuator disk",self.tmp_comp_choice, value=4).pack(side="top", anchor = 'w',padx=pad,pady=pad)
		self.updateType()
		
		return self.general_page_frame
		
	def mode_page(self,parentFrame):
		
		self.motion_type()
		self.mode_page_frame = parentFrame.frame()
		
		self.content = self.mode_page_frame.frame().pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
		if self.tmp_comp_choice.getValue() == "1":
			self.sentence = self.content.label("Fixed vessel speed, solved RPM").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
		elif self.tmp_comp_choice.getValue() == "2":
			self.sentence = self.content.label("Fixed RPM, solved vessel speed").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
		elif self.tmp_comp_choice.getValue() == "3":
			self.sentence = self.content.label("Fixed power (DHP), solved RPM and vessel speed").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
		else:
			self.sentence = self.content.label("Fixed power (THP), solved vessel speed with actuator disk").pack(side="top",fill='x',expand='yes',padx=pad,pady=pad)
		
		# SProtsign
		
		self.rot_sign_frame = self.mode_page_frame.labelframe(label="Is the thrust positive when Omega is positive ?")
		self.tmp_rot_sign = Variable(1)
		
		if self.tmp_comp_choice.getValue() != "4":
			self.rot_sign_frame.pack(side="top", fill="x", padx = pad, pady = pad)
			self.tmp_rot_sign_1 = self.rot_sign_frame.radiobutton("Yes", self.tmp_rot_sign, value=1).pack()
			self.tmp_rot_sign_2 = self.rot_sign_frame.radiobutton("No", self.tmp_rot_sign, value=-1).pack()
		
		# Diameter of the propeller
		self.diam_prop_frame = self.mode_page_frame.labelframe(label="Diameter of the propeller")		
		self.diam_prop = self.diam_prop_frame.entry(value = 0. , width = 8, unit='\[m\]')
		
		if self.tmp_comp_choice.getValue() != "4":
			self.diam_prop_frame.pack(side="top", fill="x", padx = pad, pady = pad)
			self.diam_prop.pack(side = "left" , fill = "x", padx = 1)
		
		self.diam_ad_frame = self.mode_page_frame.labelframe(label="Outer diameter of the actuator disk")
		self.diam_ad = self.diam_ad_frame.entry(value = 0. , width = 8, unit='\[m\]')
		
		if self.tmp_comp_choice.getValue() == "4":
			self.diam_ad_frame.pack(side="top", fill="x", padx = pad, pady = pad)
			self.diam_ad.pack(side = "left" , fill = "x", padx = 1)
		
		# Constant wrench
		self.wrench_frame = self.mode_page_frame.labelframe(label="Additional constant wrench applied along the x axis")
		self.wrench = self.wrench_frame.entry(value = 0. , width = 8, unit='\[N\]')
		
		# All ship motions Imposed/fixed: ask for ext wrench
		if self.Fixed == True:
			self.wrench_frame.pack(side="top", fill="x", padx = pad, pady = pad)
			self.wrench.pack(side = "left" , fill = "x", padx = 1)

		# Power of the propeller
		self.power_frame = self.mode_page_frame.labelframe(label="Power of the propeller")		
		self.power = self.power_frame.entry(value = 0. , width = 8, unit='\[W\]')
		
		if self.tmp_comp_choice.getValue() in ["3","4"]:
			self.power_frame.pack(side="top", fill="x", padx = pad, pady = pad)
			self.power.pack(side = "left" , fill = "x", padx = pad)
		
		# Estimated propeller rotational speed
		self.RPM_frame = self.mode_page_frame.labelframe(label="Estimated propeller rotational speed at operating point")		
		self.RPM = self.RPM_frame.entry(value = 0. , width = 8, unit='\[rad/s\]')
		
		if self.tmp_comp_choice.getValue() in ["3","4"]:
			self.RPM_frame.pack(side="top", fill="x", padx = pad, pady = pad)
			self.RPM.pack(side = "left" , fill = "x", padx = pad)
		
		## Expert parameters
		self.advanced_activated = False
		advanced_frame = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
		self.advanced_unpack = advanced_frame.button(text="Advanced >>>", command = Command(self,MyDialogue.advanced)).pack(side='top',anchor ='w',expand="yes")
		self.advanced_pack = advanced_frame.button(text="Advanced <<<",command = Command(self,MyDialogue.advanced))

		# Thrust coefficient
		self.thrust_coefFrame = advanced_frame.frame()
		self.thrust_coef = self.thrust_coefFrame.entry(label = "Estimated thrust coefficient at operating point                              ",value = 0.2 , width = 8).pack(side='left',expand="yes",padx=pad,pady=pad)
		
		# Advance coefficient
		self.advance_coefFrame = advanced_frame.frame()
		self.advance_coef = self.advance_coefFrame.entry(label = "Estimated advance coefficient at operating point                          " , value = 0.7 , width = 8).pack(side='left',expand="yes",padx=pad,pady=pad)
		
		# Controller activation
		self.control_actFrame = advanced_frame.frame()
		self.control_act = self.control_actFrame.entry(label = "Number of time steps before the controller is activated                " , value = 1 , width = 8).pack(side='left',expand="yes",padx=pad,pady=pad)
		
		# Limiter activation
		self.limit_actFrame = advanced_frame.frame()
		self.limit_act = self.limit_actFrame.entry(label = "Number of time steps before the limiter is activated                     " , value = 150 , width = 8).pack(side='left',expand="yes",padx=pad,pady=pad)
		
		# Max variation of Omega
		self.max_var_omFrame = advanced_frame.frame()
		self.max_var_om = self.max_var_omFrame.entry(label = "Maximum variation of Omega between two consecutive              \ntime steps when the limiter is activated" , value = 1.0 , width = 8 , unit="%").pack(side='left',expand="yes",padx=pad,pady=pad)
		
		# Max variation of vessel speed
		self.max_var_vsFrame = advanced_frame.frame()
		self.max_var_vs = self.max_var_vsFrame.entry(label = "Maximum variation of vessel speed between two consecutive     \ntime steps when the limiter is activated" , value = 1.0 , width = 8 , unit="%").pack(side='left',expand="yes",padx=pad,pady=pad)
		
		return self.mode_page_frame
	
	def advanced(self):
		if self.advanced_activated == True:
			self.advanced_pack.unpack()
			self.advanced_unpack.pack(side='top',anchor ='w',expand="yes")
			self.thrust_coefFrame.unpack()
			self.advance_coefFrame.unpack()
			self.control_actFrame.unpack()
			self.limit_actFrame.unpack()
			self.max_var_omFrame.unpack()
			self.max_var_vsFrame.unpack()
			self.advanced_activated = False
			
		else:
			self.advanced_unpack.unpack()
			self.advanced_pack.pack(side='top',anchor ='w',expand="yes")
			self.thrust_coefFrame.pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)
			if self.tmp_comp_choice.getValue() == "2" or self.tmp_comp_choice.getValue() == "3" or self.tmp_comp_choice.getValue() == "4":
				self.advance_coefFrame.pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)
			self.control_actFrame.pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)
			self.limit_actFrame.pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)
			if self.tmp_comp_choice.getValue() == "2" or self.tmp_comp_choice.getValue() == "3" or self.tmp_comp_choice.getValue() == "4":
				self.max_var_vsFrame.pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)
			if self.tmp_comp_choice.getValue() == "1" or self.tmp_comp_choice.getValue() == "3":
				self.max_var_omFrame.pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)
			self.advanced_activated = True
	
	def body_def(self):
		bodyList = FM.get_body_list()
		for i in range(len(bodyList)):
			body = bodyList[i]
			bodyID = body[0]
			bodyName = body[1]
			if FM.get_body_motion_type(bodyID)[3] == 'Imposed' and 'Sliding_patches' not in bodyName:
				#28113 Check pin axis is aligned with X avoid rudder or other bodies
				pinInfo = get_body_connection(bodyID)
				pinAxis = pinInfo[3]
				if abs(pinAxis[0]) > abs(pinAxis[1]) and abs(pinAxis[0]) > abs(pinAxis[2]):
					self.prop = bodyID
					self.propName = bodyName					
					
			if FM.get_body_motion_type(bodyID)[0] == 'Imposed' and 'Sliding_patches' not in bodyName:
				self.ship = bodyID
				self.shipName = bodyName
				
	def motion_type(self):
		# If all motions are fixed we ask external wrench in this plugin
		# if something is solved the user can enter it in Body motion
		self.body_def()
		self.Fixed = True
		if 'Solved' in FM.get_body_motion_type(self.ship):
			self.Fixed = False
			
	def updateType(self):
		if self.spType.getValue() == "1": #Propeller
			self.tmp_comp_choice_1.enable(True) 
			self.tmp_comp_choice_2.enable(True)
			self.tmp_comp_choice_3.enable(True)
			self.tmp_comp_choice_4.enable(False)
			self.tmp_comp_choice.setValue(1)
		elif self.spType.getValue() == "2": #Actuator Disk
			self.tmp_comp_choice_1.enable(False)
			self.tmp_comp_choice_2.enable(False)
			self.tmp_comp_choice_3.enable(False)
			self.tmp_comp_choice_4.enable(True)
			self.tmp_comp_choice.setValue(4)

	def check_2d(self):
		"""" #22364 Returns true if the project is 2D."""
		project_2d = False
		gravity_vector = FM.get_flow_model_gravity_parameters()
		# In 2D gravity goes in Y direction
		if gravity_vector.index(min(gravity_vector)) == 1:
			project_2d = True
			txt = 'The self-propulsion plugin is not compatible with 2D cases.'
			Warning(txt)
			print ' > ' + txt + '\n'

		return project_2d
	
	

			
				
### Instantiate the dialogue box
print ''
print '-----------------------------------------'
print ' >>> Self-Propulsion Dynamic Library <<< '
print '-----------------------------------------'
print ''

z = MyDialogue()