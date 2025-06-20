#                                                                             #
#                         Forces by section                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B.d'Aure
#       Date	  : 2014
#______________________________________________________________________________
#
# Description: Forces by section
#
# Changes:  
#
# DATE			IMPLEMENTER			TYPE OF MODIFICATION
# 02-03-2017	A. Mir				#27158 correction
# 15-12-2017	B. Teissedre		Added moments by section, #32431
#
#______________________________________________________________________________

import os
import sys
import shutil
import time
from Tk import *
from matplotlib import pyplot as plt

	
def Forces_by_section():

	pad = 2
	global flag
	flag = 0

	class MyDialogue(DialogueBox):

		def __init__(self):
			""" Get project path and sim file
				Files needed:
				- *.sim,
				- wall_data.cpr or wall_data.bin (in bxxx folders in case of parallel computation)
				- for parallel computations only: current_part_number.dat and wall_surface_grid.bin
				Returns end = 1 if a file is missing"""
			
			print '\n > START OF SCRIPT: FORCES_BY_SECTION\n'

			self.end = [0, 0]
			
			try:
				self.path = GetProjectPath()
				self.path = os.path.normpath(self.path)
				print ' > Path: ' + str(self.path)
			except RuntimeError:
				print ' > Could Not Find Project Path'
				Warning("No project is currently opened. Press 'Ok', open FINE/Marine results "
						"in CFView and launch this plugin again.")
				self.end[0] = 1
				
			if self.end[0] == 0:
				project_name = GetProjectName()
				# Taking the name minus extension to get only the computation name
				computation = project_name[:-4]
				self.sim_file = computation + '.sim'
				self.sim_file = os.path.normpath(os.path.join(self.path, self.sim_file))
				# If .sim file not existing, plugin stops
				if (os.path.exists(self.sim_file) == 0):
					print " > SIM file is not present in the computation path"
					Warning("SIM file is not present in the computation path. Press 'Ok', open some FINE/Marine results "
							"containing an existing SIM file and launch this plugin again.")
					self.end[0] = 1	
				
				# Check if other necessary files exist
				b001 = os.path.normpath(os.path.join(self.path, 'b001'))
				if os.path.isdir(b001):
					wallDataBin = b001 + '/wall_data.bin'
					wallDataCpr = b001 + '/wall_data.cpr'
					currentPartNumberDat = os.path.normpath(os.path.join(self.path, 'current_part_number.dat'))
					wallSurfaceGridBin = os.path.normpath(os.path.join(self.path,'wall_surface_grid.bin'))
					if not (os.path.isfile(wallDataBin) or os.path.isfile(wallDataCpr)):
						print " > wall_data.bin or wall_data.cpr file is not present in the computation path"
						Warning("wall_data.bin or wall_data.cpr file is not present in the computation path. "
								"Press 'Ok', open some FINE/Marine results containing an existing wall_data.bin or wall_data.cpr file and launch this plugin again.")
						self.end[0] = 1	
					if not (os.path.isfile(currentPartNumberDat)):
						print " > current_part_number.dat file is not present in the computation path"
						Warning("current_part_number.dat file is not present in the computation path. "
								"Press 'Ok', open some FINE/Marine results containing an existing current_part_number.dat"
								" file and launch this plugin again.")
						self.end[0] = 1
					if not (os.path.isfile(wallSurfaceGridBin)):
						print " > wall_surface_grid.bin file is not present in the computation path"
						Warning("wall_surface_grid.bin file is not present in the computation path. "
								"Press 'Ok', open some FINE/Marine results containing an existing wall_surface_grid.bin"
								" file and launch this plugin again.")
						self.end[0] = 1
				else:
					wallDataBin = os.path.normpath(os.path.join(self.path, 'wall_data.bin'))
					wallDataCpr = os.path.normpath(os.path.join(self.path, 'wall_data.cpr'))
					if not (os.path.isfile(wallDataBin) or os.path.isfile(wallDataCpr)):
						print " > wall_data.bin or wall_data.cpr file is not present in the computation path"
						Warning("wall_data.bin or wall_data.cpr file is not present in the computation path. "
								"Press 'Ok', open some FINE/Marine results containing an existing wall_data.bin "
								"or wall_data.cpr file and launch this plugin again.")
						self.end[0] = 1
			
			# Check if there is at least one body in the computation, print warning if not
			self.sim_info = self.readSim()
			if self.sim_info == []:
				Warning ('There is no body on this computation. Forces by section cannot be used.')
				self.end[1] = 1

			# Check if a reference point exists in .sim file
			self.check_ref_pt = ['', '', '']
			with open(self.sim_file,'r') as f:
				sim_content = f.readlines()

			line_num = 0
			# 37652 if the reference point is not found default is 0.0, 0.0, 0.0
			self.check_ref_pt = [0.0, 0.0, 0.0]
			for line in sim_content:
				line_num += 1
				if line.find('*** BODY:SOL:MVT PFD:1:POSITION GC') >= 0:
					try: 
						int(float((sim_content[line_num+1].split(' '))[0]))
						self.check_ref_pt[0] = float((sim_content[line_num + 1].split(' '))[0])
						self.check_ref_pt[1] = float((sim_content[line_num + 1].split(' '))[1])
						self.check_ref_pt[2] = float((sim_content[line_num + 1].split(' '))[2])
					except ValueError:
						# Warning ('The reference point is either inexistant or badly computed in the .sim file. Impossible to compute moments. Press "Ok" to continue to forces calculation.')
						# self.check_ref_pt = ['q']
						print ' > Could not read reference point from SIM file, setting it to (0.0, 0.0, 0.0)\n'
						break

				elif line.find('*** BODY:FIXED:1:REFERENCE POINT') >= 0:
					try: 
						int(float((sim_content[line_num+1].split(' '))[0]))
						self.check_ref_pt[0] = float((sim_content[line_num + 1].split(' '))[0])
						self.check_ref_pt[1] = float((sim_content[line_num + 1].split(' '))[1])
						self.check_ref_pt[2] = float((sim_content[line_num + 1].split(' '))[2])
					except ValueError:
						# Warning ('The reference point is either inexistant or badly computed in the .sim file. '
						#		 'Impossible to compute moments. Press "Ok" to continue to forces calculation.')
						# self.check_ref_pt = ['q']
						print ' > Could not read reference point from SIM file, setting it to (0.0, 0.0, 0.0)\n'
						break

			#if self.check_ref_pt[0] == '':
			#	Warning('The reference point is either inexistant or badly computed in the .sim file. '
			#			 'Impossible to compute moments. Press "Ok" to continue to forces calculation.')

			# If project opened and .sim file existing, initialise interface
			if self.end == [0,0]:
				DialogueBox.__init__(self, "Forces_by_section")
				
				self.mainFrame = self.frame()
				self.mainFrame.pack(side="top",fill="both")
				
				# Display generalPage in main frame
				self.generalPage(self.mainFrame)
		
				# Interface definition
				self.showCentered()

		def generalPage(self,parentFrame):
				
			# If project opened and .sim file existing and at least one body defined, read sim
			if self.end == [0, 0]:
				# Number of bodies
				self.si_nb_bodies = len(self.sim_info)
				
				# Initialize the list of bodies
				self.list_bodies = [0] * self.si_nb_bodies
				# Initialize the maximum number of sub-bodies per body (that will stay at zero if no sub-body is existing)
				self.si_nb_max_subbodies = 0
				# Initialisation of the total number of sub-bodies (for all bodies)
				self.nbTotalSubBodies = 0
				# Filling list of bodies 
				for i in range (0, self.si_nb_bodies):
					self.list_bodies[i] = (self.sim_info[i][0])
				
				# Initialize the list of bodies which have a sub-body 
				self.list_bodies_with_sb = []
				# Filling of the list of bodies which have a sub-body and get the maximum number of sub-bodies
				for i in range(0, self.si_nb_bodies):
					# Si la liste a plus de deux elements, le body possede au moins un sub-body
					if len(self.sim_info[i]) > 2:
						self.list_bodies_with_sb.append(self.sim_info[i][0])
						self.nbTotalSubBodies = self.nbTotalSubBodies + len(self.sim_info[i]) - 2
						nb_max_subbodies = len(self.sim_info[i]) - 2
						if self.si_nb_max_subbodies < nb_max_subbodies:
							self.si_nb_max_subbodies = nb_max_subbodies

				# Initialise sub_body list
				# For case 3
				if (self.si_nb_bodies == 1) and (self.si_nb_max_subbodies > 1):
					self.list_subbodies = self.sim_info[0][2:]
				# For case 6 (empty list, that will be updated when clicking on the self.sb_button button)
				else:
					self.list_subbodies = []

				# Initialisation increment that will be used in the function updateSubBodyList
				self.j = 0
				
				# Initialisation control variables
				plotFxP = True
				plotFxV = False
				plotFx = False
				plotFyP = False
				plotFyV = False
				plotFy = False
				plotFzP = False
				plotFzV = False
				plotFz = False
				
				plotMx = False
				plotMxP = False
				plotMxV = False
				plotMy = False
				plotMyP = False
				plotMyV = False
				plotMz = False
				plotMzP = False
				plotMzV = False

				# Interface layout
				# Parameters
				param = self.labelframe(label="Parameters ").pack(side="top",fill="x",padx=pad,pady=pad)	
				settings = param.frame().pack(side="top",fill="x",padx=pad,pady=pad)
				# for cas 2, 3, 5 et 6
				if ((self.si_nb_bodies == 1) and (self.si_nb_max_subbodies > 0)) or ((self.si_nb_bodies > 1) and (self.si_nb_max_subbodies > 0)):
					# Body/sub-body selection
					bsb_frame = param.labelframe(label="Body/sub-body selection").pack(side="top",anchor="w",padx=pad,pady=pad)
					bsb_button_frame = bsb_frame.frame().pack(side="top",fill="x", padx=pad,pady=pad)
					self.selecConfig = Variable(0)
					# Radiobuttons definition different according to the case

					# case 2
					if (self.si_nb_bodies == 1) and (self.si_nb_max_subbodies == 1):
						# Get the name of the body and sub-body to print them in the radiobuttons label
						b_label = "Display the forces on the body: " + self.sim_info[0][0]
						sb_label = "Display the forces on the sub-body: " + self.sim_info[0][2]
						
						bsb_button_frame.radiobutton(b_label, self.selecConfig, value=0, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)
						bsb_button_frame.radiobutton(sb_label, self.selecConfig, value=1, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)

					# case 3
					elif (self.si_nb_bodies == 1) and (self.si_nb_max_subbodies > 1):
						# Get the name of the body to print it in the radiobuttons labels
						b_label = "Display the forces on the body: " + self.sim_info[0][0]
						bsb_button_frame.radiobutton(b_label, self.selecConfig, value=0, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)
						bsb_button_frame.radiobutton("Display the forces on a sub-body ", self.selecConfig, value=1, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)

					# case 5
					elif (self.si_nb_bodies > 1) and (self.si_nb_max_subbodies == 1) and self.nbTotalSubBodies == 1:
						# Get the name of the sub-body to print it in the radiobuttons labels
						for i in range(0, self.si_nb_bodies):
							if len(self.sim_info[i]) > 2:
								sb_label = "Display the forces on the sub-body: " + self.sim_info[i][2]
						bsb_button_frame.radiobutton("Display the forces on a body ", self.selecConfig, value=0, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)
						bsb_button_frame.radiobutton(sb_label, self.selecConfig, value=1, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)
					# case 6
					elif (self.si_nb_bodies > 1) and ((self.si_nb_max_subbodies > 1) or (self.nbTotalSubBodies > 1)):
						bsb_button_frame.radiobutton("Display the forces on a body ", self.selecConfig, value=0, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)
						bsb_button_frame.radiobutton("Display the forces on a sub-body ", self.selecConfig, value=1, command=Command(self,MyDialogue.bodySubBodySelection)).pack(side="left",fill="x",padx=pad,pady=pad)
					
					# Body list (if display forces on a body selected)
					# for cases 5 et 6
					if (self.si_nb_bodies > 1):
						# If body selected, one entry > body name
						# Initialized as the chose option (packed by default)
						self.b_frame = bsb_frame.label().pack( side = "left" , fill = "y" , padx = pad)
						b_label = self.b_frame.label("Select a body:").pack(side="top",fill="x",padx=pad,pady=pad)
						self.list_bodies1_display=self.b_frame.list(self.list_bodies, multi_select=False, height=4).pack(side = "top",fill="x",expand="yes", padx=pad,pady=pad)
					
					# Body and sub-body lists (if dis-play forces on a sub-body selected)
					self.sb_frame = bsb_frame.frame()
					# Display list of bodies that have sub-bodies + button to update the sub-body list according to the selected body
					# case 6
					if (self.si_nb_bodies > 1) and ((self.si_nb_max_subbodies > 1) or (self.nbTotalSubBodies > 1)):
						self.sb_b_l_frame = self.sb_frame.frame().pack(side="left",fill="x",padx=pad,pady=pad)
						self.sb_b_label=  self.sb_b_l_frame.label("Select a body").pack(side="top",fill="x",padx=pad,pady=pad)
						self.list_bodies2_display=self.sb_b_l_frame.list(self.list_bodies_with_sb, multi_select=False,height=4).pack(side = "top",fill="x",expand="yes", padx=pad,pady=pad)
						self.sb_button_frame = self.sb_frame.frame().pack(side="left",fill="x",padx=pad,pady=pad)
						self.sb_button = self.sb_button_frame.button(text="Update sub-bodies list ->",command = Command(self.updateSubBodyList)).pack(side="top",anchor="sw", padx=pad,pady=pad)
					# Display the sub-body list
					# cases 6 et 3
					if self.si_nb_max_subbodies > 1 or self.nbTotalSubBodies > 1:
						sb_sb_l_frame = self.sb_frame.frame().pack(side="left",fill="x",padx=pad,pady=pad)
						self.sb_sb_label = sb_sb_l_frame.label("Select a sub-body").pack(side="top",fill="x",padx=pad,pady=pad)
						self.list_subbodies_display= sb_sb_l_frame.list(self.list_subbodies, multi_select=False, height=4).pack(side = "top",fill="x",expand="yes", padx=pad,pady=pad)
				# for case 4 
				# Body list
				elif (self.si_nb_bodies > 1) and (self.si_nb_max_subbodies == 0):
					self.b_frame = param.labelframe(label="Select a body").pack( side = "top" , fill = "y" , padx = pad)
					self.list_bodies1_display=self.b_frame.list(self.list_bodies, multi_select=False, height=4).pack(side = "left",fill="x",expand="yes", padx=pad,pady=pad)

				# Number of cuts
				cutparam_frame = param.labelframe(label="Cut ").pack(side="top",anchor="w",padx=pad,pady=pad)
				self.cutdir = cutparam_frame.label("Cut direction").pack(side="left",anchor="w",padx=pad,pady=pad)
				self.selecCutDir = Variable(0)
				cutparam_frame.radiobutton("X ", self.selecCutDir, value=0).pack(side="left",fill="x",padx=pad,pady=pad)
				cutparam_frame.radiobutton("Y ", self.selecCutDir, value=1).pack(side="left",fill="x",padx=pad,pady=pad)
				cutparam_frame.radiobutton("Z ", self.selecCutDir, value=2).pack(side="left",fill="x",padx=pad,pady=pad)
				self.cutnumber = cutparam_frame.entry(label="Number of cuts " , value = 10 , width = 10).pack( side = "left" , fill = "y" , padx = pad)
				
				# Output selection
				outs_lab = self.labelframe(label="Data to plot ").pack(side="top", anchor = "w", padx=pad,pady=pad, fill = 'x')

				self.forces_variables = outs_lab.label("Forces variables").pack(side = "top",anchor="w", padx=pad,pady=pad)
				outs_forces = outs_lab.frame().pack(side = "top",anchor="w", padx=pad,pady=pad)
				self.CFx = outs_forces.checkbutton("Fx ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFxP = outs_forces.checkbutton("FxP ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFxV = outs_forces.checkbutton("FxV ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFy = outs_forces.checkbutton("Fy ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFyP = outs_forces.checkbutton("FyP ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFyV = outs_forces.checkbutton("FyV ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFz = outs_forces.checkbutton("Fz ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFzP = outs_forces.checkbutton("FzP ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CFzV = outs_forces.checkbutton("FzV ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
									
				# Advanced button
				advanced_param = self.labelframe(label="Advanced ").pack(side="top", fill="x", expand="yes", anchor="w",padx=pad,pady=pad)

				# 34327 Set range for the cuts
				range_frame = advanced_param.frame().pack(side="top",anchor="w",padx=pad,pady=pad)
				self.range_button = range_frame.checkbutton("Set range for cuts ", initValue=0, command=Command(self,MyDialogue.range_display)).pack(side="left",padx=pad,pady=pad)
				self.range_min_entry = range_frame.entry(label="Min ", value=0.0, width=10, unit='\[m]')
				self.range_max_entry = range_frame.entry(label="Max ", value=0.0, width=10, unit='\[m]')

				self.dof = advanced_param.label("Travelling shot").pack(side="top",anchor="w",padx=pad,pady=pad)
				ts_set_up = advanced_param.frame().pack(side="top",anchor="w",padx=pad,pady=pad)
				self.selecDof = Variable(0)
				ts_set_up.radiobutton("Ship ", self.selecDof, value=0).pack(side="left",fill="x",padx=pad,pady=pad)
				ts_set_up.radiobutton("Carriage ", self.selecDof, value=1).pack(side="left",fill="x",padx=pad,pady=pad)
				ts_set_up.radiobutton("Earth ", self.selecDof, value=2).pack(side="left",fill="x",padx=pad,pady=pad)
				
				self.frame_ts = advanced_param.label("Frame for travelling shot").pack(side="top",anchor="w",padx=pad,pady=pad)
				frameTs_set_up = advanced_param.frame().pack(side="top",anchor="w",padx=pad,pady=pad)
				self.selecFrame = Variable(0)
				frameTs_set_up.radiobutton("Reference ", self.selecFrame, value=1).pack(side="left",fill="x",padx=pad,pady=pad)
				frameTs_set_up.radiobutton("Primary ", self.selecFrame, value=0).pack(side="left",fill="x",padx=pad,pady=pad)

				# Add Moments output selection only if reference point exists
				# if (self.check_ref_pt[0] != '') and (self.check_ref_pt[0] != 'q'):
				self.moments_variables = outs_lab.label("Moments variables").pack(side="top",anchor="w",padx=pad,pady=pad)
				outs_moments = outs_lab.frame().pack(side = "top",anchor="w", padx=pad,pady=pad)
				self.CMx = outs_moments.checkbutton("Mx ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMxP = outs_moments.checkbutton("MxP ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMxV = outs_moments.checkbutton("MxV ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMy = outs_moments.checkbutton("My ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMyP = outs_moments.checkbutton("MyP ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMyV = outs_moments.checkbutton("MyV ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMz = outs_moments.checkbutton("Mz ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMzP = outs_moments.checkbutton("MzP ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)
				self.CMzV = outs_moments.checkbutton("MzV ", initValue = 0, command=Command(self,MyDialogue.funcNbPlots)).pack(side="left",padx=pad,pady=pad)

				self.ref_pt = advanced_param.label("Reference point for moments").pack(side="top",anchor="w",padx=pad,pady=pad)
				ref_pt_set_up =  advanced_param.frame().pack(side = "top",anchor="w", padx=pad,pady=pad)
				self.ref_pt_x = ref_pt_set_up.entry(label="X " , value = self.check_ref_pt[0] , width = 10).pack( side = "left",padx=pad,pady=pad)
				self.ref_pt_y = ref_pt_set_up.entry(label="Y " , value = self.check_ref_pt[1] , width = 10).pack( side = "left",padx=pad,pady=pad)
				self.ref_pt_z = ref_pt_set_up.entry(label="Z " , value = self.check_ref_pt[2] , width = 10).pack( side = "left",padx=pad,pady=pad)

				# One or several plots selection
				one_several_plots = outs_lab.frame().pack(side="top",fill="x",padx=pad,pady=pad)
				self.selecNbPlots = Variable(0)
				self.one_plot_button = one_several_plots.radiobutton("One plot per force ", self.selecNbPlots, value=0)
				self.several_plots_button = one_several_plots.radiobutton("One plot for all forces ", self.selecNbPlots, value=1)

				# Go and Close buttons
				buttonframe = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
				close_button = buttonframe.button(text="Close",command = Command(self.closeButton)).pack(side="right",anchor="sw",padx=pad,pady=pad)
				go_button = buttonframe.button(text="Go",command = Command(self.go)).pack(side="right",anchor="sw",padx=pad,pady=pad)

		def bodySubBodySelection(self):
			""" self.selecConfig
				- 0: body
				- 1: sub-body"""

			# Display the frame (and the corresponding entries) for the corresponding option
			if self.selecConfig.getValue() == "0":
				if (self.si_nb_max_subbodies > 1) or (self.si_nb_bodies >1):
					self.sb_frame.unpack()
				if self.si_nb_bodies >1:
					self.b_frame.pack(side="top",fill="x",padx=pad,pady=pad)
			elif self.selecConfig.getValue() == "1":
				if self.si_nb_bodies > 1:
					self.b_frame.unpack()
				if (self.si_nb_bodies > 1) or (self.si_nb_max_subbodies > 1):
					self.sb_frame.pack(side="top",fill="x",padx=pad,pady=pad)

		def updateSubBodyList(self):
			"""Update the sub-body list according to the selected body"""

			while self.list_subbodies_display.getItems() != []:
				self.list_subbodies_display.removeItem(self.j)
				self.j = self.j + 1

			try:
				selected_body = self.list_bodies[(self.list_bodies2_display.getSelection())[0]]
			except IndexError:
				Warning("Please select a body first.")
			# get .sim file
			for i in range(0, self.si_nb_bodies):
				if selected_body in self.sim_info[i]:
					body_list_position = i
			self.list_subbodies = self.sim_info[body_list_position][2:]
			if self.list_subbodies == []:
				self.list_subbodies_display.appenplotMx = False
				plotMy = False
				plotMz = FalsedItem('None')
			else:
				for name_to_add in self.list_subbodies:
					self.list_subbodies_display.appendItem(name_to_add)

		def funcNbPlots(self):
			""" Change interface depending on the number of plots"""

			plotFxP = self.CFxP.getState()
			plotFxV = self.CFxV.getState()
			plotFx = self.CFx.getState()

			plotFyP = self.CFyP.getState()
			plotFyV = self.CFyV.getState()
			plotFy = self.CFy.getState()

			plotFzP = self.CFzP.getState()
			plotFzV = self.CFzV.getState()
			plotFz = self.CFz.getState()
			vartoplot = [plotFxP, plotFxV, plotFx, plotFyP, plotFyV, plotFy, plotFzP, plotFzV, plotFz]

			if (self.check_ref_pt[0] != '') and (self.check_ref_pt[0] != 'q'):
				plotMx = self.CMx.getState()
				plotMxP = self.CMxP.getState()
				plotMxV = self.CMxV.getState()
				plotMy = self.CMy.getState()
				plotMyP = self.CMyP.getState()
				plotMyV = self.CMyV.getState()
				plotMz = self.CMz.getState()
				plotMzP = self.CMzP.getState()
				plotMzV = self.CMzV.getState()
				vartoplotMoments = [plotMx, plotMxP, plotMxV, plotMy, plotMyP, plotMyV, plotMz, plotMzP, plotMzV]

			l = 0
			for i in range(9):
				if (self.check_ref_pt[0] != '') and (self.check_ref_pt[0] != 'q'):
					if (vartoplot[i] == 1) or (vartoplotMoments[i] ==1):
						l = l+1
				else:
					if vartoplot[i] == 1:
						l = l+1

			if l > 1:
				self.one_plot_button.pack(side="left",padx=pad,pady=pad)
				self.several_plots_button.pack(side="left",padx=pad,pady=pad)
			else:
				self.one_plot_button.unpack()
				self.several_plots_button.unpack()

		def closeButton(self):
			""" Close the interface"""

			print '\n END OF SCRIPT\n'
			self.close()

		def go(self):
			everything_ok = True
			
			# Check if a body/sub-body is selected, print a warning if not
			# case 4 or (case 5 and body selected) or (case 6 and body selected)
			if ((self.si_nb_bodies > 1) and (self.si_nb_max_subbodies == 0)) or (((self.si_nb_bodies > 1) and (self.si_nb_max_subbodies == 1) and (self.nbTotalSubBodies == 1)) and self.selecConfig.getValue() == '0') or (((self.si_nb_bodies > 1) and ((self.si_nb_max_subbodies > 1) or (self.nbTotalSubBodies > 1))) and self.selecConfig.getValue() == '0'):
				if self.list_bodies1_display.getSelection() == []:
					Warning ('Please select a body to be able to continue.')
					everything_ok = False
			# case 6 and sub-body selected
			elif ((self.si_nb_bodies > 1) and ((self.si_nb_max_subbodies > 1) or (self.nbTotalSubBodies > 1))) and self.selecConfig.getValue() == '1':
				if self.list_bodies2_display.getSelection() == []:
					Warning ('Please select a body to be able to continue.')
					everything_ok = False
			# (case 6 and sub-body selected) or (case 3 and sub-body selected)
			if (((self.si_nb_bodies > 1) and ((self.si_nb_max_subbodies > 1) or (self.nbTotalSubBodies > 1))) or ((self.si_nb_bodies == 1) and (self.si_nb_max_subbodies > 1))) and self.selecConfig.getValue() == '1':
				if self.list_subbodies_display.getSelection() == []:
					Warning ('Please select a sub-body to be able to continue.')
					everything_ok = False
					
			if (self.si_nb_bodies > 1) and (self.si_nb_max_subbodies > 1):
				if self.selecConfig.getValue() == '1':
					selected_body = self.list_bodies[(self.list_bodies2_display.getSelection())[0]]
					a = self.list_subbodies
					for i in range (0, len(self.list_bodies)):
						if selected_body == self.sim_info[i][0]:
							body_list_position = i
							break
					list_subbodies_belonging_to_selected_body = []
					for k in range (2, len(self.sim_info[i])):
						if not list_subbodies_belonging_to_selected_body:
							list_subbodies_belonging_to_selected_body = [self.sim_info[i][k]]
						else:
							list_subbodies_belonging_to_selected_body.append(self.sim_info[i][k])
					if list_subbodies_belonging_to_selected_body != self.list_subbodies:
						Warning("The body and sub-body you selected don't match. Please update the sub-body list" 
						"before selecting the sub-body.")
						everything_ok = False

			# 34327 Set range for cuts
			self.set_range = self.range_button.getState()
			if self.set_range == 1:
				self.range_min = self.range_min_entry.getFloatValue()
				self.range_max = self.range_max_entry.getFloatValue()

				if self.range_max <= self.range_min:
					Warning("Invalid range for cuts")
					everything_ok = False
					
			if everything_ok:
				print '\n > Start of forces_by_section tool\n'

				# Variables used as arguments for the executable:
				surf = 'wall_data.cpr'
				sim = self.sim_file
				
				self.body_subbody_list = self.getBodySubBodyIndex()
				body = self.body_subbody_list[0]
				if ((self.si_nb_bodies == 1) and (self.si_nb_max_subbodies > 0)) or ((self.si_nb_bodies > 1) and (self.si_nb_max_subbodies > 0)):
					self.there_is_sb = int(self.selecConfig.getValue())
				else:
					self.there_is_sb = 0
				sb = self.body_subbody_list[1]
				
				self.cutdir = int(self.selecCutDir.getValue())
				body_ts = body
				self.ncuts = self.cutnumber.getIntValue() 	# Available from marine31_3a6

				# Traveling shot
				dof_ts = self.getDofTS()
				frame_ts = self.getFrameTS()
				dof_ts = str(dof_ts[0]) + ',' + str(dof_ts[1]) + ',' + str(dof_ts[2]) + ',' + str(dof_ts[3]) + ',' + str(dof_ts[4]) + ',' + str(dof_ts[5])

				if (self.check_ref_pt[0] == '') or (self.check_ref_pt[0] == 'q'):
					m_ref_pt = ['']					
				else:
					m_ref_pt = self.getMrefPt()
					m_ref_pt = str(m_ref_pt[0]) + ',' + str(m_ref_pt[1]) + ',' + str(m_ref_pt[2]) 

				# 34327 Range
				if self.set_range == 1:
					range_arg = ' -range={},{}'.format(self.range_min, self.range_max)

				# Shell commands to call forces_by_section executable
				# Detect the CFView version
				cfviewpath = os.path.dirname(sys.argv[0])
				cfviewpath = os.path.normpath(cfviewpath)

				# Get all arguments needed to launch the tool
				# Basic arguments
				args = ' -surf=' + surf + ' -sim=' + sim + ' -body=' + str(body) + ' -body_ts=' \
					   + str(body_ts) + ' -ncut=' + str(self.ncuts) + ' -dof_ts=' + dof_ts + ' -frame_ts=' \
					   + frame_ts + ' -print'
				# Sub-body
				if self.there_is_sb == 1:
					args += ' -sb=' + str(sb)
				# Moments
				if m_ref_pt[0] != '':
					args += ' -m_ref_pt=' + m_ref_pt

				# Range
				if self.set_range == 1:
					args += range_arg

				# cut in y direction
				if self.cutdir == 1:
					args += ' -cut=y'
					self.CutsDirName = 'Y'
				# cut in z direction
				elif self.cutdir == 2:
					args += ' -cut=z'
					self.CutsDirName = 'Z'
				# cut in x direction
				else:
					self.CutsDirName = 'X'
				
				# Windows
				if sys.platform == 'win32':
					
					# Get tool version
					# cfviewpath is something like C:\NUMECA_SOFTWARE\finemarine61rc\bin64
					numecapath, rest = os.path.split(cfviewpath) #remove bin64
					installpath, version = os.path.split(numecapath) #get version = finemarineXXX
					print ' > Package path: ' + str(numecapath)					

					try:
						version = version.lower().split("fine").pop()
						version_found = 1
					except:
						version_found = 0
					print ' > Version: ' + str(version)	
					
					if version_found == 0:
							#Warning("Wake flow tool not available outside FINE/Marine package")
							CFViewWarning("Forces_by_section tool not available outside FINE/Marine package")
					else:
						# Executable absolute path
						forces_by_section_exec = os.path.normpath(os.path.join(numecapath, 'bin/isis64/forces_by_section.exe'))
						
						# Fix of bug 25396
						# For 2D cases without AGR, wall_surface_grid.bin is needed so we need to launch extract_wall_surface_grid
						pathToSurf = os.path.normpath(os.path.join(self.path, surf))
						pathToWallSurface = os.path.normpath(os.path.join(self.path, 'wall_surface_grid.bin'))
						if os.path.isfile(pathToSurf) == False and os.path.isfile(pathToWallSurface) == False:
							os.chdir(self.path)
							with open('extract_wall_surface_grid.input', 'w') as f:
								f.write('\n \n \n')

							print ' > Launch extract_wall_surface_grid tool'
							os.system(os.path.normpath(os.path.join(numecapath, 'bin/isis64/extract_wall_surface_grid.exe < extract_wall_surface_grid.input')))
							os.system('DEL extract_wall_surface_grid.input')

						# Launch
						os.chdir(self.path)
						os.system(forces_by_section_exec + args)

				# LINUX
				else:
					# Get tool version
					# cfviewpath is something like /common/numeca/finemarine61rc/LINUX/cfview
					linuxpath, rest = os.path.split(cfviewpath) #remove cfview
					numecapath, rest = os.path.split(linuxpath) #remove LINUX
					installpath, version = os.path.split(numecapath) #get version = finemarineXXX
					print ' > Package path: ' + str(numecapath)					

					try:
						version = version.lower().split("fine").pop()
						version_found = 1
					except:
						version_found = 0

					if version_found == 0:
						# Warning("Wake flow tool not available outside FINE/Marine package")
						CFViewWarning("Forces_by_section tool not available outside FINE/Marine package")
					else:
						# Fix of bug 25396
						# For 2D cases without AGR, wall_surface_grid.bin is needed so we need to launch extract_wall_surface_grid
						pathToSurf = os.path.normpath(os.path.join(self.path, surf))
						pathToWallSurface = os.path.normpath(os.path.join(self.path, 'wall_surface_grid.bin'))
						if os.path.isfile(pathToSurf) == False and os.path.isfile(pathToWallSurface) == False:
							os.chdir(self.path)
							f = open('extract_wall_surface_grid.input', 'w')
							f.write('\n \n \n')
							f.close()
							print ' > Launch extract_wall_surface_grid tool'
							os.system('extract_wall_surface_grid' + version + ' < extract_wall_surface_grid.input')
							os.system('rm -f extract_wall_surface_grid.input')

						os.chdir(self.path)
						os.system('forces_by_section' + version + args)

				# 37621 Make results folder for both OS with date
				tmp = time.localtime()
				time_string = time.strftime('%m-%d-%Y_%Hh-%Mm-%Ss', tmp)
				output_folder = 'Forces_by_section_output_' + time_string

				self.pathFbs = os.path.normpath(os.path.join(self.path, output_folder))
				print ' > Output path: ' + str(self.pathFbs)
				if not os.path.isdir(self.pathFbs):
					os.mkdir(self.pathFbs)

				self.make_plots()

		def getDofTS(self):
			""" Get travelling shot"""
			if int(self.selecDof.getValue()) == 2:   # Earth frame
				return 1,1,1,0,0,0
			elif int(self.selecDof.getValue()) == 1:  # Carriage frame
				return 1,1,1,0,0,1 
			else:                                    # Ship frame
				return 1,1,1,1,1,1

		def getFrameTS(self):
			""" Get settings for frame of travelling shot (TS)"""
			if int(self.selecFrame.getValue()) == 1:  # Reference
				return "reference"
			else:                                    # Primary
				return "primary"

		def getMrefPt(self):
			""" Get point of reference for moments"""
			x_ref = self.ref_pt_x.getFloatValue()
			y_ref = self.ref_pt_y.getFloatValue()
			z_ref = self.ref_pt_z.getFloatValue()
			return x_ref,y_ref,z_ref      

		def getBodySubBodyIndex(self):
			""" Returns a list of the selected body's and sub-body's index (sub-body's index = 0 if no sub-body)"""

			# Default values
			sub_body_id = 0
			body_id = self.sim_info[0][1] 
			# case 2
			if ((self.si_nb_bodies == 1) and (self.si_nb_max_subbodies == 1)):
				if self.selecConfig.getValue() == '1':
					sub_body_id = 1 
			# case 3
			elif ((self.si_nb_bodies == 1) and (self.si_nb_max_subbodies > 1)):
				if self.selecConfig.getValue() == '1':
					#Sub-body's index = position in the list + 1
					for i in self.list_subbodies_display.getSelection():
						sub_body_name = self.list_subbodies_display.getItemFromId(i)
					for k in range (0, len(self.sim_info[0])):
						if  self.sim_info[0][k] ==  sub_body_name:
							sub_body_id = k-1   
							break
					
			# case 4
			elif ((self.si_nb_bodies > 1) and (self.si_nb_max_subbodies == 0)):
				#Get body's name (selection gives position in the displayed list as a list,the position as an interger is extracted and the name of the body is found)
				selected_body = self.list_bodies[(self.list_bodies1_display.getSelection())[0]]
				#In the list of bodies
				for i in range (0, self.si_nb_bodies):
					#If the name of the selected body is found, deduce the position in the list and then the body's index
					if selected_body in self.sim_info[i]:
						body_list_position = i
						body_id = self.sim_info[i][1]
			# case 5
			elif ((self.si_nb_bodies > 1) and (self.si_nb_max_subbodies == 1) and self.nbTotalSubBodies == 1):
				if self.selecConfig.getValue() == '0':
					for i in range(0, len(self.sim_info)):
						if len(self.sim_info[i]) > 2:
							body_id = self.sim_info[i][1]
				elif self.selecConfig.getValue() == '1':
					selected_body = self.list_bodies_with_sb[0]
					for i in range (0, len(self.list_bodies)):
						if selected_body in self.sim_info[i]:
							body_list_position = i
							body_id = self.sim_info[i][1]
					sub_body_id = 1
			# case 6
			elif (self.si_nb_bodies > 1) and ((self.si_nb_max_subbodies > 1) or (self.nbTotalSubBodies > 1)):
				if (self.selecConfig.getValue() == '0'):
					selected_body = self.list_bodies[(self.list_bodies1_display.getSelection())[0]]
					for i in range (0, self.si_nb_bodies):
						if selected_body in self.sim_info[i]:
							body_list_position = i
							body_id = self.sim_info[i][1]
				if (self.selecConfig.getValue() == '1'):
					selected_body = self.list_bodies[(self.list_bodies2_display.getSelection())[0]]
					for i in range (0, len(self.list_bodies)):
						if selected_body in self.sim_info[i]:
							body_list_position = i
							body_id = self.sim_info[i][1]
					for i in self.list_subbodies_display.getSelection():
						sub_body_name = self.list_subbodies_display.getItemFromId(i)
					for k in range (0, len(self.sim_info[body_list_position])):
						if self.sim_info[body_list_position][k] ==  sub_body_name:
							sub_body_id = k-1    
							break

			return [body_id, sub_body_id]

		def readSim(self):
			""" Returns list of bodies: this list is composed of several lists (one per body) containing
				[body name, body index, [sub-body name 1, sub-body name 2]
				Example for two bodies (ship1, ship2), the first body having two sub-bodies (rudder, hull):
				[['ship1', 1, 'rudder', 'keel'], ['ship2', 2]]"""

			if self.end == [0, 0]:
				with open(self.sim_file,'r') as f:
					sim_content = f.readlines()

				# fb, imb, smb are booleans that returns true if there are fixed/imposed/solved bodies in the computation
				fb = False
				imb = False
				smb = False
				# nb_f_b, nb_im_b, nb_sm_b are the number of fixed/imposed motion/solved motion bodies
				nb_f_b = 0
				nb_im_b = 0
				nb_sm_b = 0
				
				# Find the total number of bodies (total_nb_bodies),
				# the existance and number of fixed/imposed motion/solved motion bodies
				for line in sim_content:
					if line.find('*-------------------- F I X E D     B O D I E S ------------------------------') >= 0:
						fb = True
						nb_f_b = int(sim_content[2 + sim_content.index('*** BODY:FIXED:NUMBER\n')])
						print " number of fixed bodies: " + str(nb_f_b)
					if line.find('*--- B O D I E S     W I T H     I M P O S E D     M O T I O N ---------------') >= 0:
						imb = True
						nb_im_b = int(sim_content[2 + sim_content.index('*** BODY:SOL:MVT IMP:NUMBER\n')])
					if line.find('*--- B O D I E S     W I T H     S O L V E D     M O T I O N -----------------') >= 0:
						smb = True
						nb_sm_b = int(sim_content[2 + sim_content.index('*** BODY:SOL:MVT PFD:NUMBER\n')])
				total_nb_bodies = nb_f_b + nb_im_b + nb_sm_b
							
				# body_list structure:
				# [body name, body index, [sub-body name 1, sub-body name 2]
				body_list = [0] * total_nb_bodies

				if fb:
					# k is the position of the body in the body class
					k = 0
					# i is the position of the body list in body_list
					for i in range(0, nb_f_b):
						k = k + 1
						# get body index
						body_index = int(sim_content[2 + sim_content.index('*** BODY:FIXED:' + str(k) + ':INDEX\n')])
						# get body name and add it in first position in the body list
						# (splitlines used here to remove the "return to line" (/n) at after the body name)
						name_of_bd = str(sim_content[2 + sim_content.index('*** BODY:FIXED:' + str(k) + ':NAME\n')]).splitlines()
						if (name_of_bd[0][0:-2] != "Virtual_body") and (name_of_bd[0][0:-2] != "Sliding_patches"):
							body_list[i] = name_of_bd
							# append body index in second position in the body list
							body_list[i].append(body_index)
							# find out if there are existing sub-bodies for each body of this class
							for line2 in sim_content:
								if line2.find (str(body_index) + ':SUB BODY NAME') >= 0:
									# get a preliminary list of sub-bodies: this list still contains some "parasites" due to the splitting
									# ex: ['', 'rudder2', ' ', 'rudder1', ' \n']
									preliminary_subbody_list = sim_content[2 + sim_content.index('*** BODY:FIXED:' + str(body_index) + ':SUB BODY NAME\n')].split('\'')
									# remove "parasites" of the sub-bodies list, that are all in the odd positions of the list. 
									# we keep only the strings in the even positions of the list
									# ex: ['rudder2', 'rudder1']
									subbody_list = preliminary_subbody_list[1::2]
									# get the length of the sub-bodies list
									subbody_list_length = len(subbody_list)
									# for each sub-body in subbody_list, we append the sub-body's name to the body list
									for j in range(subbody_list_length):
										body_list[i].append(str(subbody_list[j]))
									
				if imb:
					k = 0
					# to know the position if the body list in body_list
					# if there are fixed bodies, start iterating from the number of fixed bodies and stop at the
					# number of fixed + imposed motion bodies
					if fb:
						start_list = nb_f_b
						end_list = nb_f_b + nb_im_b
					# if there are no fixed bodies, start to iterate at 0 and stop at the number of imposed motion bodies
					else:
						start_list = 0
						end_list = nb_im_b
						
					for i in range(start_list, end_list):
						k = k + 1
						body_index = int(sim_content[2 + sim_content.index('*** BODY:SOL:MVT IMP:' + str(k) + ':INDEX\n')])
						name_of_bd = str(sim_content[2 + sim_content.index('*** BODY:SOL:MVT IMP:' + str(k) + ':NAME\n')]).splitlines()
						if  (name_of_bd[0][0:-2] != "Virtual_body") and (name_of_bd[0][0:-2] != "Sliding_patches"):
							body_list[i] = name_of_bd
							body_list[i].append(body_index)
							for line2 in sim_content:
								if line2.find (str(body_index) + ':SUB BODY NAME') >= 0:
									preliminary_subbody_list = sim_content[2 + sim_content.index('*** BODY:SOL:MVT IMP:' + str(body_index) + ':SUB BODY NAME\n')].split('\'')
									subbody_list = preliminary_subbody_list[1::2]
									subbody_list_length = len(subbody_list)
									for j in range(subbody_list_length):
										body_list[i].append(str(subbody_list[j]))
								
				if smb:
					k = 0
					if (fb == True and imb == True):
						start_list = nb_f_b + nb_im_b
						end_list = nb_f_b + nb_im_b + nb_sm_b
					elif (fb == True and imb == False):
						start_list = nb_f_b 
						end_list = nb_f_b + nb_sm_b
					elif (fb == False and imb == True):
						start_list = nb_im_b 
						end_list = nb_im_b + nb_sm_b
					else:
						start_list = 0
						end_list = nb_sm_b
					
					for i in range(start_list, end_list):
						k = k + 1
						body_index = int(sim_content[2 + sim_content.index('*** BODY:SOL:MVT PFD:' + str(k) + ':INDEX\n')])
						name_of_bd = str(sim_content[2 + sim_content.index('*** BODY:SOL:MVT PFD:' + str(k) + ':NAME\n')]).splitlines()
						if  (name_of_bd[0][0:-2] != "Virtual_body") and (name_of_bd[0][0:-2]!= "Sliding_patches"):
							body_list[i] = name_of_bd
							body_list[i].append(body_index)
							for line2 in sim_content:
								if line2.find (str(body_index) + ':SUB BODY NAME') >= 0:
									preliminary_subbody_list = sim_content[2 + sim_content.index('*** BODY:SOL:MVT PFD:' + str(body_index) + ':SUB BODY NAME\n')].split('\'')
									subbody_list = preliminary_subbody_list[1::2]
									subbody_list_length = len(subbody_list)
									for j in range(subbody_list_length):
										body_list[i].append(str(subbody_list[j]))		#

				for bd in body_list:
					if bd == 0:
						body_list.remove(bd)

				# print body_list
				return body_list

		def range_display(self):
			""" Show range entries if the checkbox is activated"""
			if self.range_button.getState() == 1:
				self.range_min_entry.pack(side="left", padx=pad, pady=pad)
				self.range_max_entry.pack(side="left", padx=pad, pady=pad)
			else:
				self.range_min_entry.unpack()
				self.range_max_entry.unpack()

		def make_plots(self):
			""" Create and save the plots of the selected quantities"""

			# Initialization
			for i in range(0, len(self.sim_info)):
				if self.body_subbody_list[0] == self.sim_info[i][1]:
					body_name = self.sim_info[i][0]
					if self.there_is_sb == 1:
						sub_body_name = self.sim_info[i][self.body_subbody_list[1] + 1]
					break
			if self.there_is_sb == 1:
				forces_file = 'forces_by_section_' + str(
					self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '_' + sub_body_name + '.dat'

			else:
				forces_file = 'forces_by_section_' + str(self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '.dat'

			if not (os.path.isfile(os.path.normpath(os.path.join(self.path, 'forces_by_section.dat')))):
				print ' '
				CFViewWarning(
					"forces_by_section tool failed. Please have a look at the shell to find the cause of the error.")
				raise Exception(
					' > forces_by_section tool failed. Please have a look above to find the cause of the error.')

			shutil.move(os.path.normpath(os.path.join(self.path, 'forces_by_section.dat')),
							os.path.normpath(os.path.join(self.pathFbs, forces_file)))

			forces_file = os.path.normpath(os.path.join(self.pathFbs, forces_file))
			# data = np.zeros((self.ncuts, 10))
			# titles = []

			# Data is stored in a dictionary with the following keys:
			# - name: string FxP
			# - title: string FxP(N/m)
			# - active (int, 0 or 1)
			# data: float list of values

			# Read data and store it
			with open(forces_file, 'r') as f:
				f_lines = f.readlines()[3:]

			# Store values from file
			vartoplot = []
			for j in range(1, 10):  # Variables (columns)
				var = {}
				data = []
				for i in range(self.ncuts + 1):  # Number of cuts (lines)
					if i == 0:
						var['title'] = f_lines[i].split()[j]
					else:
						data.append(f_lines[i].split()[j])
				var['data'] = data
				vartoplot.append(var)

			# Store X/Y/Z coordinates
			Xdata = []
			for i in range(1, self.ncuts + 1):
				Xdata.append(f_lines[i].split()[0])

			# Variable names without units
			for var in vartoplot:
					var['name'] = var['title'].strip("(N/m)")

			# Read active status from checkbuttons
			aux_var_func = [{'name': 'FxP', 'active': self.CFxP.getState()},
						 {'name': 'FxV', 'active': self.CFxV.getState()},
						 {'name': 'Fx', 'active': self.CFx.getState()},

						 {'name': 'FyP', 'active': self.CFyP.getState()},
						 {'name': 'FyV', 'active': self.CFyV.getState()},
						 {'name': 'Fy', 'active': self.CFy.getState()},

						 {'name': 'FzP', 'active': self.CFzP.getState()},
						 {'name': 'FzV', 'active': self.CFzV.getState()},
						 {'name': 'Fz', 'active': self.CFz.getState()}, ]
			
			# Store if the variable is active for plotting
			for var in vartoplot:
				for var1 in aux_var_func:
					if var['name'] == var1['name']:
						var['active'] = var1['active']

			# TEMP
			# for var in vartoplot:
			# 	print var

			# Plotting
			vartoplotactive = [var['active'] for var in vartoplot]
			NbVarToPlot = sum(vartoplotactive)
			if NbVarToPlot == 1:
				OnePlotOnly = 1
			else:
				OnePlotOnly = int(self.selecNbPlots.getValue())

			# self.figure_number = 0
			art = []

			if (OnePlotOnly == 1) and any(nb != 0 for nb in vartoplotactive):
				figure_name = 'forces_by_section_'
				plt.clf()
				for var in vartoplot:
					if var['active'] == 1:
						figure_name += var['name']
						plt.plot(Xdata, var['data'], linestyle='-', marker='o', markersize=5, label=var['title'])

				if self.there_is_sb == 0:
					plt.title('Force distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', ' + str(
						self.ncuts) + ' cuts', fontsize=12)
				else:
					plt.title(
						'Force distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', Sub-body: ' + sub_body_name + ', ' + str(
							self.ncuts) + ' cuts', fontsize=12)
				lgd = plt.legend(prop={'size': 7}, loc='center left', bbox_to_anchor=(1, 0.5))
				art.append(lgd)
				plt.grid()
				plt.xlabel(self.CutsDirName + ' [m]')
				plt.ylabel('Force per section [N/m]')
				if self.there_is_sb == 1:
					figure_name = figure_name + str(
						self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '_' + sub_body_name
				else:
					figure_name = figure_name + str(self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name
				plt.savefig(os.path.normpath(os.path.join(self.pathFbs, figure_name + '.png')), additional_artists=art,
							bbox_inches="tight")
				# 25657 correction
				plt.close()

			elif (OnePlotOnly == 0) and any(nb != 0 for nb in vartoplotactive):
				for i in range(9):
					figure_name = 'forces_by_section_'
					plt.clf()
					for var in vartoplot:
						if var['active'] == 1:
							figure_name += var['name']
							plt.plot(Xdata, var['data'], linestyle='-', marker='o', markersize=5, label=var['title'])

							if self.there_is_sb == 0:
								plt.title(
									'Force distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', ' + str(
										self.ncuts) + ' cuts', fontsize=12)

							else:
								plt.title(
									'Force distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', Sub-body: ' + sub_body_name + ', ' + str(
										self.ncuts) + ' cuts', fontsize=12)
							lgd = plt.legend(prop={'size': 7}, loc='center left', bbox_to_anchor=(1, 0.5))
							art.append(lgd)
							plt.grid()
							plt.xlabel(self.CutsDirName + ' [m]')
							plt.ylabel('Force per section [N/m]')
							if self.there_is_sb == 1:
								figure_name = figure_name + str(
									self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '_' + sub_body_name
							else:
								figure_name = figure_name + str(self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name
							plt.savefig(os.path.normpath(os.path.join(self.pathFbs, figure_name + '.png')),
										additional_artists=art, bbox_inches="tight")
						# 25657 correction
						plt.close()

			# 36851 check if moments file exists (Moment output data is not available with old data wall_data.bin)
			if os.path.isfile(os.path.join(self.path, 'moments_by_section.dat')):
				if (self.check_ref_pt[0] != '') and (self.check_ref_pt[0] != 'q'):

					if self.there_is_sb == 1:
						moments_file = 'moments_by_section_' + str(
							self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '_' + sub_body_name + '.dat'
					else:
						moments_file = 'moments_by_section_' + str(
							self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '.dat'

					# 36851 Moment output data is not available with old data wall_data.bin
					# if not (os.path.isfile(os.path.normpath(os.path.join(self.path, 'moments_by_section.dat')))):
					# print ' '
					# CFViewWarning("forces_by_section tool failed. Please have a look at the shell to find the cause of the error.")
					# raise Exception(' > forces_by_section tool failed. Please have a look above to find the cause of the error.')

					shutil.move(os.path.normpath(os.path.join(self.path, 'moments_by_section.dat')),
									os.path.normpath(os.path.join(self.pathFbs, moments_file)))
					moments_file = os.path.normpath(os.path.join(self.pathFbs, moments_file))

					with open(moments_file, 'r') as m:
						m_lines = m.readlines()[3:]

					# Store values from file
					vartoplotMoments = []
					for j in range(1, 10):  # Variables (columns)
						var = {}
						data = []
						for i in range(self.ncuts + 1):  # Number of cuts (lines)
							if i == 0:
								var['title'] = m_lines[i].split()[j]
							else:
								data.append(m_lines[i].split()[j])
						var['data'] = data
						vartoplotMoments.append(var)

					# Store X/Y/Z coordinates
					Xdata = []
					for i in range(1, self.ncuts + 1):
						Xdata.append(m_lines[i].split()[0])

					# Variable names without units
					for var in vartoplotMoments:
						var['name'] = var['title'].strip("(Nm/m)")

					aux_var_func_m = [{'name': 'Mx', 'active': self.CMx.getState()},
								 		{'name': 'MxP', 'active': self.CMxP.getState()},
								 		{'name': 'MxV', 'active': self.CMxV.getState()},

								 		{'name': 'My', 'active': self.CMy.getState()},
								 		{'name': 'MyP', 'active': self.CMyP.getState()},
								 		{'name': 'MyV', 'active': self.CMyV.getState()},

								 		{'name': 'Mz', 'active': self.CMz.getState()},
								 		{'name': 'MzP', 'active': self.CMzP.getState()},
								 		{'name': 'MzV', 'active': self.CMzV.getState()} ]

					# Store if the variable is active for plotting
					for var in vartoplotMoments:
						for var1 in aux_var_func_m:
							if var['name'] == var1['name']:
								var['active'] = var1['active']

					#print 'var to plot moments'
					#for var in vartoplotMoments:
					#print var

					vartoplotactiveM = [var['active'] for var in vartoplotMoments]
					NbVarToPlotMoments = sum(vartoplotactiveM)

					if NbVarToPlotMoments == 1:
						OnePlotOnlyMoments = 1
					else:
						OnePlotOnlyMoments = int(self.selecNbPlots.getValue())

					# print titlesMoments
					# self.figure_number = 0
					art = []

					if (OnePlotOnlyMoments == 1) and any(nb != 0 for nb in vartoplotactiveM):
						figure_name = 'moments_by_section_'
						plt.clf()
						for var in vartoplotMoments:
							if var['active'] == 1:
								figure_name += var['name']
								plt.plot(Xdata, var['data'], linestyle='-', marker='o',
										 markersize=5, label=var['title'])

						if self.there_is_sb == 0:
							plt.title(
								'Moment distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', ' + str(
									self.ncuts) + ' cuts', fontsize=12)
						else:
							plt.title(
								'Moment distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', Sub-body: ' + sub_body_name + ', ' + str(
									self.ncuts) + ' cuts', fontsize=12)
						lgd = plt.legend(prop={'size': 7}, loc='center left', bbox_to_anchor=(1, 0.5))
						art.append(lgd)
						plt.grid()
						plt.xlabel(self.CutsDirName + ' [m]')
						plt.ylabel('Moment per section [Nm/m]')
						if self.there_is_sb == 1:
							figure_name = figure_name + str(
								self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '_' + sub_body_name
						else:
							figure_name = figure_name + str(self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name
						plt.savefig(os.path.normpath(os.path.join(self.pathFbs, figure_name + '.png')),
									additional_artists=art, bbox_inches="tight")
						# 25657 correction
						plt.close()

					elif (OnePlotOnlyMoments == 0) and any(nb != 0 for nb in vartoplotactiveM):
						for var in vartoplotMoments:
							figure_name = 'moments_by_section_'
							plt.clf()
							if var['active'] == 1:
								figure_name += var['name']
								plt.plot(Xdata, var['data'], linestyle='-', marker='o',
										 markersize=5, label=var['title'])

								if self.there_is_sb == 0:
									plt.title(
										'Moment distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', ' + str(
											self.ncuts) + ' cuts', fontsize=12)

								else:
									plt.title(
										'Moment distribution in ' + self.CutsDirName + ' direction, Body: ' + body_name + ', Sub-body: ' + sub_body_name + ', ' + str(
											self.ncuts) + ' cuts', fontsize=12)
								lgd = plt.legend(prop={'size': 7}, loc='center left', bbox_to_anchor=(1, 0.5))
								art.append(lgd)
								plt.grid()
								plt.xlabel(self.CutsDirName + ' [m]')
								plt.ylabel('Moment per section [Nm/m]')
								if self.there_is_sb == 1:
									figure_name = figure_name + str(
										self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name + '_' + sub_body_name
								else:
									figure_name = figure_name + str(self.ncuts) + 'cuts' + self.CutsDirName + '_' + body_name
								plt.savefig(os.path.normpath(os.path.join(self.pathFbs, figure_name + '.png')),
											additional_artists=art, bbox_inches="tight")
							# 25657 correction
							plt.close()

			if sys.platform == 'win32':
				pathFbsForDisplay_temp = self.pathFbs.split(os.sep)
				pathFbsForDisplay = pathFbsForDisplay_temp[0]
				for i in range(1, len(pathFbsForDisplay_temp)):
					pathFbsForDisplay = os.path.normpath(os.path.join(pathFbsForDisplay, pathFbsForDisplay_temp[i]))

			else:
				pathFbsForDisplay = self.pathFbs

			CFViewWarning("forces_by_section tool ran successfully. Outputs generated in " + (str(pathFbsForDisplay)))
			print '\n > forces_by_section tool ran successfully'
			print ' > Outputs generated in {}\n'.format(self.pathFbs)
	z = MyDialogue()