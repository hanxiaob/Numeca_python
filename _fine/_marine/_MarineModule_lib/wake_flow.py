#                                                                             #
#                                   Wake flow                                 #
# _____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : Barbara d'Aure, Anna Mir
#	Date: 2014
# ______________________________________________________________________________
#
# Description: launch wake_flow_pp to generate cylindrical cut with va, vr, vt
#
# Changes:
#
# DATE			IMPLEMENTER			TYPE OF MODIFICATION
# 08/08/2017	Julien Roulle		#27199
# 15-12-2017	B. Teissedre		#31636
# 08/01/2018	Baptiste Teissedre	#31636
# 24/10/1018	A. Mir				Code simplification, -local argument for #34117
# ______________________________________________________________________________

from cfv import *
from Tk import *
import os, sys

def Wake_flow_tool():
	# Interface init
	pad = 2

	class MyDialogue(DialogueBox):

		def __init__(self):
			""" Get project path
				Check if project is 3D
				Initialize dialogue"""

			print '\n > START OF SCRIPT: WAKE_FLOW_TOOL\n'

			# Get project path and .sim file name
			# If no project opened or no .sim file existing, end = 1 will be returned to stop the script
			self.end = [0]

			try:
				self.path = GetProjectPath()
				print ' > Path: ' + self.path
			except RuntimeError:
				print ' > Could Not Find Project Path'
				Warning("No project is currently opened. First open FINE/Marine results and launch this plugin again.")
				self.end[0] = 1
				return

			if self.end[0] == 0:
				project_name = GetProjectName()
				self.computation = project_name[:-4]
				self.sim_file = self.computation + '.sim'
				self.sim_file = self.path + os.sep + self.sim_file
				if os.path.exists(self.sim_file) == 0:
					txt = 'SIM file is not present in the computation path. '
					txt += 'Open FINE/Marine results containing an existing SIM file.'
					print ' > ' + txt + '\n'
					CFViewWarning(txt)
					self.end[0] = 1

			# Defect 27199
			# Check 2D/3D first and stop if 2D
			qnt_exist_1 = QntFieldExist('Relative Velocity_Z')
			qnt_exist_2 = QntFieldExist('Velocity_Z')
			if qnt_exist_1 == 1:
				QntFieldRemove('Relative Velocity_Z')
			if qnt_exist_2 == 1:
				QntFieldRemove('Velocity_Z')
			if QntFieldExist('Relative Velocity') == 1:
				QntFieldDerived(0, 'Relative Velocity_Z', 'Relative Velocity_Z', '', '0')
				QntFieldVector('Relative Velocity_Z')
			if QntFieldExist('Velocity') == 1:
				QntFieldDerived(0, 'Velocity_Z', 'Velocity_Z', '', '0')
				QntFieldVector('Velocity_Z')
			SelectFromProjectRegExp('')
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
				return

			# If project opened and .sim file existing, initialise interface
			if self.end == [0]:
				DialogueBox.__init__(self, "Wake flow tool")
				self.show()

				self.mainFrame = self.frame()
				self.mainFrame.pack(side="top", fill="both")

				### Display general_page in main frame
				self.general_page(self.mainFrame)
				self.showCentered()

		def general_page(self, parentFrame):
			""" Interface definition"""

			# If project opened and .sim file existing, interface definition
			if self.end == [0]:
				self.sim_info = self.read_sim()

				# Default values for no actuaor disk in the computation or no actuator disk selected
				ddiameter = 0.0
				dxc = 0.0
				dyc = 0.0
				dzc = 0.0
				dxnv = 0.0
				dynv = 0.0
				dznv = 0.0
				dinner_radius = 0.0
				douter_radius = 0.0
				ddist_prop = 0.0

				# Initialisation control variables
				self.ccwise_activated = False
				self.sixoclock_activated = False
				self.symmetry_activated = False

				# If computation with two or more actuator disks, display actuator disk selection entry
				if self.sim_info[1] >= 2:
					nb_ad_frame = self.frame().pack(side="top", fill="x", padx=pad, pady=pad)
					self.nb_ad = nb_ad_frame.entry(label="ID of the actuator disk to post process: ", value=1,
												   width=16).pack(side="left", fill="y", padx=pad)
					apply_button = nb_ad_frame.button(text="Apply", command=Command(self, MyDialogue.apply_1)).pack(
						side="left", anchor="sw", padx=pad, pady=pad)

				# Interface layout
				# Actuator disk parameters
				adparam = self.labelframe(label="Actuator disk parameters ").pack(side="top", fill="x", padx=pad,
																				  pady=pad)
				settings = adparam.frame().pack(side="top", fill="x", padx=pad, pady=pad)
				# Counterclockwise positive selection
				self.ccwise_activation = settings.checkbutton("Conterclockwise positive ", initValue=0,
															  command=Command(self, MyDialogue.ccwise)).pack(
					side="left", fill="x", padx=pad, pady=pad)
				# Origin at 6 o'clock selection
				self.sixoclock_activation = settings.checkbutton("Origin at 6 o'clock ", initValue=0,
																 command=Command(self, MyDialogue.sixoclock)).pack(
					side="left", fill="x", padx=pad, pady=pad)

				# Diameter
				settings2 = adparam.frame().pack(side="top", fill="x", padx=pad, pady=pad)
				self.ad_diameter = settings2.entry(label="Diameter ", value=ddiameter, width=16, unit='\[m]').pack(
					side="left", fill="y", padx=pad)

				# Center coordinates
				ad_center = adparam.labelframe(label="Center coordinates").pack(side="top", anchor="w", padx=pad,
																				pady=pad)
				self.ad_center_x = ad_center.entry(label="X ", value=dxc, width=16).pack(side="left", fill="y",
																						 padx=pad)
				self.ad_center_y = ad_center.entry(label="Y ", value=dyc, width=16).pack(side="left", fill="y",
																						 padx=pad)
				self.ad_center_z = ad_center.entry(label="Z ", value=dzc, width=16).pack(side="left", fill="y",
																						 padx=pad)

				# Normal vector
				norm_vec = adparam.labelframe(label="Normal vector (pointed towards the wake)").pack(side="top",
																									 anchor="w",
																									 padx=pad, pady=pad)
				self.ad_norm_vec_x = norm_vec.entry(label="X ", value=dxnv, width=16).pack(side="left", fill="y",
																						   padx=pad)
				self.ad_norm_vec_y = norm_vec.entry(label="Y ", value=dynv, width=16).pack(side="left", fill="y",
																						   padx=pad)
				self.ad_norm_vec_z = norm_vec.entry(label="Z ", value=dznv, width=16).pack(side="left", fill="y",
																						   padx=pad)

				## Wake flow plane parameters
				planeparam = self.labelframe(label="Wake flow plane parameters ").pack(side="top", fill="x", padx=pad,
																					   pady=pad)
				# Distance to propeller
				settings3 = planeparam.frame().pack(side="top", fill="x", padx=pad, pady=pad)
				self.p_dist_prop = settings3.entry(label="Distance to the propeller ", value=ddist_prop, width=16,
												   unit='\[m]').pack(side="left", fill="y", padx=pad)

				# Inner and outer radii
				settings4 = planeparam.frame().pack(side="top", fill="x", padx=pad, pady=pad)
				self.p_inner_rad = settings4.entry(label="Inner radius ", value=dinner_radius, width=16,
												   unit='\[m]').pack(side="left", fill="y", padx=pad)
				self.p_outer_rad = settings4.entry(label="Outer radius ", value=douter_radius, width=16,
												   unit='\[m]').pack(side="left", fill="y", padx=pad)

				# Reference values
				compparam = self.labelframe(label="Reference values ").pack(side="top", fill="x", padx=pad, pady=pad)
				# Reference velocity
				self.velocity = compparam.entry(label="Advancing velocity ", value=self.sim_info[0], width=16,
												unit='\[m/s]').pack(side="left", fill="y", padx=pad)

				# Advanced parameters
				self.advanced_activated = False
				advanced_frame = self.frame().pack(side="top", fill="x", padx=pad, pady=pad)

				# Advanced selection button
				self.advanced_unpack = advanced_frame.button(text="Advanced >>>",
															 command=Command(self, MyDialogue.advanced)).pack(
					side='top', anchor='w', expand="yes")
				self.advanced_pack = advanced_frame.button(text="Advanced <<<",
														   command=Command(self, MyDialogue.advanced))

				# Number of points in tangential and radial directions
				self.nb_points_frame = advanced_frame.labelframe(label="Number of points ")

				# Defect 31636
				self.p_nb_pt_rad = self.nb_points_frame.entry(label="Radial direction ", value=self.sim_info[2],
															  width=12).pack(side="left", fill="y", padx=pad)
				self.p_nb_pt_tan = self.nb_points_frame.entry(label="Tangential direction ", value=self.sim_info[3],
															  width=12).pack(side="left", fill="y", padx=pad)
				if self.p_nb_pt_rad.getFloatValue() > 45:
					txt = 'Number of points in radial direction of actuator disk greater than 45'
					txt += '(wave_flow.txt must not be written porperly)'
					Warning(txt)

				# Mesh distribution
				self.distribution_frame = advanced_frame.labelframe(
					label="Mesh concentration: points defined with origin at 12 o'clock with clockwise rotation")
				self.dis_button_frame = self.distribution_frame.frame().pack(side="top", fill="x", padx=pad, pady=pad)
				self.selecConfig = Variable(2)
				self.dis_button_frame.radiobutton("Homogeneous ", self.selecConfig, value=2,
												  command=Command(self, MyDialogue.configurationChange)).pack(
					side="left", fill="x", padx=pad, pady=pad)
				self.dis_button_frame.radiobutton("Around one point", self.selecConfig, value=0,
												  command=Command(self, MyDialogue.configurationChange)).pack(
					side="left", fill="x", padx=pad, pady=pad)
				self.dis_button_frame.radiobutton("Around two points", self.selecConfig, value=1,
												  command=Command(self, MyDialogue.configurationChange)).pack(
					side="left", fill="x", padx=pad, pady=pad)

				self.onep_frame = self.distribution_frame.frame()
				self.orp1 = self.onep_frame.entry(label="P ", value=0.0, width=10, unit='''\[o'clock]''').pack(
					side="left", fill="y", padx=pad)
				self.oh = self.onep_frame.entry(label="Mesh stretching factor ", value=0.2, width=10).pack(side="left",
																										   fill="y",
																										   padx=pad)
				self.sym_button = self.onep_frame.checkbutton("Symmetry", initValue=0,
															  command=Command(self, MyDialogue.f_sym_button)).pack(
					side="left", fill="x", padx=pad, pady=pad)

				self.twop_frame = self.distribution_frame.frame()
				self.trp1 = self.twop_frame.entry(label="P1 ", value=0.0, width=10, unit='''\[o'clock]''').pack(
					side="left", fill="y", padx=pad)
				self.trp2 = self.twop_frame.entry(label="P2 ", value=0.0, width=10, unit='''\[o'clock]''').pack(
					side="left", fill="y", padx=pad)
				self.th = self.twop_frame.entry(label="Mesh stretching factor ", value=0.2, width=12).pack(side="left",
																										   fill="y",
																										   padx=pad)

				# Cancel and Go buttons
				bframe = self.frame().pack(side="top", fill="x", padx=pad, pady=pad)
				go_button = bframe.button(text="Go", command=Command(self.go)).pack(side="right", anchor="sw", padx=pad,
																					pady=pad)
				cancel_button = bframe.button(text="Cancel", command=Command(self.cancel)).pack(side="right",
																								anchor="sw", padx=pad,
																								pady=pad)

				# If computation with one actuator disk, read information for actuator disk one
				if self.sim_info[1] == 1:
					self.read_sim2(1)

		def read_sim(self):
			""" Read information fom sim file:
				- Velocity
				- Number of ADs
				- Number of points in tangential and radial directions"""

			if self.end == [0]:
				with open(self.sim_file, 'r') as f:
					sim_content = f.readlines()

				ref_vel = float(sim_content[sim_content.index('*** REFERENCE VELOCITY\n') + 2])
				ad_number = int(sim_content[sim_content.index('*** ACTUATOR DISK : NUMBER\n') + 2])
				dis_rad = int(
					sim_content[sim_content.index('*** ACTUATOR DISK : INTERNAL MESH DIMENSIONS\n') + 2].split()[1])
				dis_tan = int(
					sim_content[sim_content.index('*** ACTUATOR DISK : INTERNAL MESH DIMENSIONS\n') + 2].split()[2])

				return [ref_vel, ad_number, dis_rad, dis_tan]

		def read_sim2(self, disknum):
			""" Read information related to actuator disk disknum from sim file:
				- Inner and outer radius
				- Diameter
				- Center coordinates
				- Normal vector
				- Distance to propeller"""

			# Initialisation of the target to look for in the .sim file (depending on the actuator disk to post process
			outer_radius_target = '*** ACTUATOR DISK:' + str(disknum) + ':OUTER RADIUS\n'
			center_target = '*** ACTUATOR DISK:' + str(disknum) + ':CENTER COORDINATES\n'
			normal_vector_target = '*** ACTUATOR DISK:' + str(disknum) + ':SHAFT DIRECTION\n'
			dist_prop_target = '*** ACTUATOR DISK:' + str(disknum) + ':DISTANCE TO INFLOW PLANE\n'
			inner_radius_target = '*** ACTUATOR DISK:' + str(disknum) + ':INNER RADIUS\n'
			force_distr_target = '*** ACTUATOR DISK : BODY FORCE DISTRIBUTION\n'

			with open(self.sim_file, 'r') as f:
				sim_content = f.readlines()

			inner_rad = float(sim_content[sim_content.index(inner_radius_target) + 2])
			outer_rad = float(sim_content[sim_content.index(outer_radius_target) + 2])
			ad_diameter = outer_rad * 2

			ad_center_x = float(sim_content[sim_content.index(center_target) + 2].split()[0])
			ad_center_y = float(sim_content[sim_content.index(center_target) + 2].split()[1])
			ad_center_z = float(sim_content[sim_content.index(center_target) + 2].split()[2])

			ad_norm_vec_x = float(sim_content[sim_content.index(normal_vector_target) + 2].split()[0])
			ad_norm_vec_y = float(sim_content[sim_content.index(normal_vector_target) + 2].split()[1])
			ad_norm_vec_z = float(sim_content[sim_content.index(normal_vector_target) + 2].split()[2])

			self.p_inner_rad.setValue(inner_rad)
			self.p_outer_rad.setValue(outer_rad)
			self.ad_diameter.setValue(ad_diameter)
			self.ad_center_x.setValue(ad_center_x)
			self.ad_center_y.setValue(ad_center_y)
			self.ad_center_z.setValue(ad_center_z)
			self.ad_norm_vec_x.setValue(ad_norm_vec_x)
			self.ad_norm_vec_y.setValue(ad_norm_vec_y)
			self.ad_norm_vec_z.setValue(ad_norm_vec_z)

			prop_code = str(sim_content[sim_content.index(force_distr_target) + 2])[:-2]
			if prop_code == 'PROPELLER CODE':
				p_dist_prop = float(sim_content[sim_content.index(dist_prop_target) + 2])
			else:
				p_dist_prop = 0.0
			self.p_dist_prop.setValue(p_dist_prop)

		def apply_1(self):
			""" Apply button: select one actuator disk and read its data"""

			# Check that the actuator disk's ID is an interger. Display warning if not.
			try:
				self.ad_id = self.nb_ad.getIntValue()
			except ValueError:
				CFViewWarning("The actuator disk ID must be an integer value.")
				return

			# Call read_sim() to get the number of actuator disks.
			self.sim_info = self.read_sim()
			id_max = int(self.sim_info[1])

			# Check that the actuator disk's ID is in the existing range. Display warning if not.
			if (self.ad_id > id_max) or (self.ad_id < 1):
				txt = 'There is no actuator disk corresponding to this ID. '
				txt += 'The ID should be between 1 and ' + str(id_max) + '.'
				CFViewWarning(txt)
				return
			print ' > You chose to post process actuator disk number ' + str(self.ad_id)
			# Read the values corresponding to the selected actuator disk and put the corresponding values in the interface.
			self.read_sim2(self.ad_id)

		def ccwise(self):
			"""Conterclockwise positive selection
				- 1: Conterclockwise positive
				- 0: Clockwise positive"""

			if self.ccwise_activation.getState() == 1:
				self.ccwise_activated = True
			else:
				self.ccwise_activated = False

		def sixoclock(self):
			""" Origin at 6 o'clock selection
				- 1: Origin at 6 o'clock
				- 0: Origin at 12 o'clock"""

			if self.sixoclock_activation.getState() == 1:
				self.sixoclock_activated = True
			else:
				self.sixoclock_activated = False

		def configurationChange(self):
			""" Selection of the mesh distribution
				- 0: Concentration around one point
				- 1: Concentration around two points
				- 2: Homogeneous"""

			# Display the frame (and the corresponding entries) for the corresponding option
			if self.selecConfig.getValue() == "0":
				self.onep_frame.pack(side="top", fill="x", padx=pad, pady=pad)
				self.twop_frame.unpack()
			elif self.selecConfig.getValue() == "1":
				self.twop_frame.pack(side="top", fill="x", padx=pad, pady=pad)
				self.onep_frame.unpack()
			elif self.selecConfig.getValue() == "2":
				self.onep_frame.unpack()
				self.twop_frame.unpack()

		def f_sym_button(self):
			""" Activation of the concentration symmetry
				1 - Active
				0 - Not active"""

			if self.sym_button.getState() == 1:
				self.symmetry_activated = True
			else:
				self.symmetry_activated = False

		def advanced(self):
			""" Actions performed by Advanced button """

			# If "advanced" is activated, display the advanced options, display advanced_unpack button instead
			# of advanced_pack button  and set advanced_activated to false
			if self.advanced_activated == True:
				self.advanced_pack.unpack()
				self.advanced_unpack.pack(side='top', anchor='w', expand="yes")
				self.nb_points_frame.unpack()
				self.distribution_frame.unpack()
				self.advanced_activated = False
			# If "advanced" is de-activated, hide the advanced options, display advanced_pack button instead
			# of advanced_unpack button and set advanced_activated to true
			else:
				self.advanced_unpack.unpack()
				self.advanced_pack.pack(side='top', anchor='w', expand="yes")
				self.nb_points_frame.pack(side="top", fill="x", expand="yes", padx=pad, pady=pad)
				self.distribution_frame.pack(side="top", fill="x", expand="yes", padx=pad, pady=pad)
				self.advanced_activated = True

		def cancel(self):
			""" Cancel button action: close the interface."""
			print '\n > END OF SCRIPT\n'
			self.close()

		def checkInputValues(self):
			""" Check values entered by the user are of the type required"""

			# Check if values are floats or integers. Display warning if not.
			try:
				self.ad_diameter.getFloatValue()
				self.ad_center_x.getFloatValue()
				self.ad_center_y.getFloatValue()
				self.ad_center_z.getFloatValue()
				nx = self.ad_norm_vec_x.getFloatValue()
				ny = self.ad_norm_vec_y.getFloatValue()
				nz = self.ad_norm_vec_z.getFloatValue()
				self.p_dist_prop.getFloatValue()
				self.p_inner_rad.getFloatValue()
				self.p_outer_rad.getFloatValue()
				self.velocity.getFloatValue()
				if self.selecConfig.getValue() == '0':
					self.orp1.getFloatValue()
					self.oh.getFloatValue()
				elif self.selecConfig.getValue() == '1':
					self.trp1.getFloatValue()
					self.trp2.getFloatValue()
					self.th.getFloatValue()
			except ValueError:
				Warning('Wrong input value in the entry. Must be a float or an integer value.')
				return

			# Check if values are integers. Display warning if not.
			try:
				self.p_nb_pt_rad.getIntValue()
				self.p_nb_pt_tan.getIntValue()
			except ValueError:
				Warning('Wrong input value in the entry. Must be an integer value.')
				return

			# Check if values are positive (or strictly positive, or smaller than from 12 for P, P1 and P2).
			# Display warning if not.
			if self.ad_diameter.getFloatValue() <= 0:
				Warning('Wrong input value in the entry. Diameter must be a strictly positive value.')
				return
			elif self.p_inner_rad.getFloatValue() <= 0:
				Warning('Wrong input value in the entry. Inner radius must be a strictly positive value.')
				return
			elif self.p_outer_rad.getFloatValue() <= 0:
				Warning('Wrong input value in the entry. Outer radius must be a strictly positive value.')
				return
			elif self.p_nb_pt_tan.getIntValue() <= 0:
				Warning(
					'Wrong input value in the entry. Number of points in tangential direction must be a strictly positive value.')
				return
			elif self.p_nb_pt_rad.getIntValue() <= 0:
				Warning(
					'Wrong input value in the entry. Number of points in radial direction must be a strictly positive value.')
				return
			elif self.selecConfig.getValue() == '0':
				if self.orp1.getFloatValue() < 0 or self.orp1.getFloatValue() > 12:
					Warning('Wrong input value in the entry. P must be in the range of \[0, 12].')
					return
				elif self.oh.getFloatValue() <= 0:
					Warning(
						'Wrong input value in the entry. Mesh stretching factor must be a strictly positive value.')
					return
			elif self.selecConfig.getValue() == '1':
				if self.th.getFloatValue() <= 0:
					Warning(
						'Wrong input value in the entry. Mesh stretching factor must be a strictly positive value.')
					return
				elif self.trp1.getFloatValue() < 0 or self.trp1.getFloatValue() > 12:
					Warning('Wrong input value in the entry. P1 must be in the range of \[0, 12\].')
					return
				elif self.trp2.getFloatValue() < 0 or self.trp2.getFloatValue() > 12:
					Warning('Wrong input value in the entry. P2 must be in the range of \[0, 12].')
					return

			# Check that the normal vector is different from (0, 0, 0)
			if [nx, ny, nz] == [0.0, 0.0, 0.0]:
				Warning('Wrong input value in the entry. Normal vector should be different from (0, 0, 0).')
				return

			# Check if inner radius < outer_radius
			if self.p_outer_rad.getFloatValue() <= self.p_inner_rad.getFloatValue():
				Warning(
					'Wrong input value in the entry. Outer radius should be strictly bigger than inner radius.')
				return

			# Check if P1 is different from P2 (case of mesh concentration around two points)
			if self.selecConfig.getValue() == '1':
				if self.trp1.getFloatValue() == self.trp2.getFloatValue():
					Warning('Wrong input value in the entry. P1 and P2 should be different.')
					return

			# Check if symmetry is activated and P = 0, 6 or 12 o'clock
			if self.selecConfig.getValue() == '0':
				if self.symmetry_activated and self.orp1.getFloatValue() in [0, 6, 12]:
					txt = "You activated the symmetry option but P is 0, 6 or 12 o'clock. "
					txt += "Please deactivate the symmetry option or choose a refinement "
					txt += "location different from 0, 6 or 12 o'clock."
					Warning(txt)
					return

			# Defect 31636: radial direction must be inferior to 45 points
			if self.p_nb_pt_rad.getFloatValue() > 45:
				txt = 'Number of points in radial direction of actuator disk greater than 45. wave_flow.txt'
				txt += 'file will not be written properly.'
				Warning(txt)

			return 'ok'

		def runWakeFlowTool(self):
			""" - Read input values from the interface
				- Launch the wake flow tool executable"""

			# Define variables
			V = str(self.velocity.getFloatValue())
			cc = self.ccwise_activated
			s6 = self.sixoclock_activated
			cpp = str(self.ad_center_x.getFloatValue()) + ',' + str(self.ad_center_y.getFloatValue()) + ',' + str(
				self.ad_center_z.getFloatValue())
			wnv = str(self.ad_norm_vec_x.getFloatValue()) + ',' + str(self.ad_norm_vec_y.getFloatValue()) + ',' + str(
				self.ad_norm_vec_z.getFloatValue())
			rin = str(self.p_inner_rad.getFloatValue())

			D = str(self.ad_diameter.getFloatValue())
			dist = str(self.p_dist_prop.getFloatValue())
			nr = str(self.p_nb_pt_rad.getIntValue())
			nt = str(self.p_nb_pt_tan.getIntValue())

			# Values needed in CFView
			self.rout = str(self.p_outer_rad.getFloatValue())
			rout = self.rout
			self.xc = self.ad_center_x.getFloatValue()
			self.yc = self.ad_center_y.getFloatValue()
			self.zc = self.ad_center_z.getFloatValue()
			self.nx = self.ad_norm_vec_x.getFloatValue()
			self.ny = self.ad_norm_vec_y.getFloatValue()
			self.nz = self.ad_norm_vec_z.getFloatValue()

			# If there is more than one AD
			if (self.sim_info[1] >= 2):
				disk = str(self.ad_id)

			# Mesh concentration definition
			# concentration around 1 point
			if (self.selecConfig.getValue() == '0'):
				# Concentration point values must be between 0 and 11.999
				if self.orp1.getFloatValue() == 12.0:
					rp1 = '0.0'
				else:
					rp1 = str(self.orp1.getFloatValue())
				h = str(self.oh.getFloatValue())
				sym = self.symmetry_activated

			# concentration around 2 points
			elif (self.selecConfig.getValue() == '1'):
				# Concentration point values must be between 0 and 11.999
				if self.trp1.getFloatValue() == 12.0:
					rp1 = '0.0'
				else:
					rp1 = str(self.trp1.getFloatValue())
				if self.trp2.getFloatValue() == 12.0:
					rp2 = '0.0'
				else:
					rp2 = str(self.trp2.getFloatValue())
				h = str(self.th.getFloatValue())

			# System commands to call the wake flow pp executable
			print ' > Running wake flow tool...'

			# Detect the CFView version
			cfviewpath = os.path.dirname(sys.argv[0])
			print 'CFView path =' + str(cfviewpath)
			package_path = cfviewpath.split('/')
			numecapath = os.path.dirname(cfviewpath)
			print 'NUMECA path =' + str(numecapath)

			# Optional arguments when launching the tool
			disk_arg = ''
			if self.sim_info[1] >= 2:
				disk_arg = ' -disk=' + disk

			# Counter clock wise positive
			cc_arg = ''
			if cc == 1:
				cc_arg = ' -cc'

			# Origin at 6 o'clock
			s6_arg = ''
			if s6 == 1:
				s6_arg = ' -s6'

			# Mesh concentration
			mesh_conc_arg = ''
			if self.selecConfig.getValue() in ['0', '1']:
				# Mesh concentration 1 point
				if (self.selecConfig.getValue() == '0'):
					mesh_conc_arg = ' -cc' + ' -h=' + h + ' -rp1=' + rp1
					# Symmetry of mesh concentration
					if sym == 1:
						mesh_conc_arg += ' -sym'
				elif (self.selecConfig.getValue() == '1'):
					mesh_conc_arg = ' -cc' + ' -h=' + h + ' -rp1=' + rp1 + ' -rp2=' + rp2

			basic_discs = ' -auto' + ' -V=' + V + ' -D=' + D + disk_arg + ' -rin=' \
						  + rin + ' -rout=' + rout + ' -wnv=' + wnv + ' -dist=' + dist + ' -cpp=' \
						  + cpp + ' -nr=' + nr + ' -nt=' + nt + cc_arg + s6_arg + mesh_conc_arg + ' -local' + ' -print'

			# WINDOWS
			if sys.platform == 'win32':
				package_path = cfviewpath.split('\\')
				index = package_path.index("bin64")
				version = package_path[index - 1][len("finemarine"):]
				print ' > Package version detected: ' + version
				version_found = 1

				if version_found == 0:
					# Warning("Wake flow tool not available outside FINE/Marine package")
					CFViewWarning("Wake flow tool not available outside FINE/Marine package")

				# Executable absolute path
				wake_flow_exec = numecapath + os.sep + 'bin' + os.sep + 'isis64' + os.sep + 'wake_flow_pp.exe'

				# Execute the command
				os.chdir(self.path)
				os.system(wake_flow_exec + basic_discs)
				print ' > Wake flow tool executed with arguments:'
				print '   ' + wake_flow_exec + basic_discs + '\n'

			# LINUX
			else:
				# Get tool version
				# Defect 24830
				index = package_path.index("LINUX")
				version = package_path[index - 1][len("finemarine"):]
				version = "marine" + version
				print ' > Package version detected: ' + version
				version_found = 1

				if (version_found == 0):
					# Warning("Wake flow tool not available outside FINE/Marine package")
					CFViewWarning("Wake flow tool not available outside FINE/Marine package")

				wake_flow_exec = 'wake_flow_pp' + version
				os.chdir(self.path)
				os.system(wake_flow_exec + basic_discs)
				print ' > Wake flow tool executed with arguments:'
				print '   ' + wake_flow_exec + basic_discs + '\n'

			self.close()

		def openResultsCFV(self):
			""" Open results generated by wake_flow_pp in CFView:
				- wake_flow.g
				- wake_flow.f
				- wake_flow.name"""

			print ' > Wake flow tool calculation finished. Opening results in CFView.'

			# Recover values read by runWakeFlowTool
			xc = self.xc
			yc = self.yc
			zc = self.zc
			nx = self.nx
			ny = self.ny
			nz = self.nz
			rout = self.rout

			# Files saved by the wake flow tool
			gfile = self.path + os.sep + 'wake_flow.g'
			ffile = self.path + os.sep + 'wake_flow.f'
			namefile = self.path + os.sep + 'wake_flow.name'

			# Defect 24919
			if os.path.isfile(gfile) and os.path.isfile(ffile) and os.path.isfile(namefile):

				# num of divisions for the isolines
				ndivisions = 20

				# Va
				OpenPlot3DProject(gfile, ffile, namefile)

				QntFieldScalar('Va')
				SclContourSmooth()
				ColormapSmoothOnly()
				# Unselect all surfaces except for D1.Imin, where we will plot the data
				SelectedSurfacesRemove('D1.Jmin', 'D1.Kmin', 'D1.Kmax', 'D1.Jmax', 'D1.Imax')
				RprRangeActiveSurfaces()
				range_mf = []
				range_mf = QuantityRangeActiveSurfaces()
				SclIsolineMulti(2, 4, range_mf[0], range_mf[1], (range_mf[1] - range_mf[0]) / ndivisions, 1)
				GmtToggleBoundary()
				# GmtToggleGrid()

				# Display the axes
				ViewAxesGlobal()
				# Compute the maximum value of the axis
				xmax = xc + float(rout)
				ymax = yc + float(rout)
				zmax = zc + float(rout)
				# Set axis range
				SetGradAxis1Range(xc, xmax)
				SetGradAxis2Range(yc, ymax)
				SetGradAxis3Range(zc, zmax)

				ViewPlaneX()
				Normal(nx, ny, nz)

				# Vtheta
				OpenPlot3DProject(gfile, ffile, namefile)
				QntFieldScalar('Vtheta')
				SclContourSmooth()
				ColormapSmoothOnly()
				# Unselect all surfaces except for D1.Imin, where we will plot the data
				SelectedSurfacesRemove('D1.Jmin', 'D1.Kmin', 'D1.Kmax', 'D1.Jmax', 'D1.Imax')
				RprRangeActiveSurfaces()
				range_mf = []
				range_mf = QuantityRangeActiveSurfaces()
				SclIsolineMulti(2, 4, range_mf[0], range_mf[1], (range_mf[1] - range_mf[0]) / ndivisions, 1)
				GmtToggleBoundary()
				# GmtToggleGrid()

				# Display the axes
				ViewAxesGlobal()
				# Compute the maximum value of the axis
				xmax = xc + float(rout)
				ymax = yc + float(rout)
				zmax = zc + float(rout)
				# Set axis range
				SetGradAxis1Range(xc, xmax)
				SetGradAxis2Range(yc, ymax)
				SetGradAxis3Range(zc, zmax)

				ViewPlaneX()
				Normal(nx, ny, nz)

				# Vr
				OpenPlot3DProject(gfile, ffile, namefile)
				QntFieldScalar('Vr')
				SclContourSmooth()
				ColormapSmoothOnly()
				# Unselect all surfaces except for D1.Imin, where we will plot the data
				SelectedSurfacesRemove('D1.Jmin', 'D1.Kmin', 'D1.Kmax', 'D1.Jmax', 'D1.Imax')
				RprRangeActiveSurfaces()
				range_mf = []
				range_mf = QuantityRangeActiveSurfaces()
				SclIsolineMulti(2, 4, range_mf[0], range_mf[1], (range_mf[1] - range_mf[0]) / ndivisions, 1)
				GmtToggleBoundary()
				# GmtToggleGrid()

				# Display the axes
				ViewAxesGlobal()
				# Compute the maximum value of the axis
				xmax = xc + float(rout)
				ymax = yc + float(rout)
				zmax = zc + float(rout)
				# Set axis range
				SetGradAxis1Range(xc, xmax)
				SetGradAxis2Range(yc, ymax)
				SetGradAxis3Range(zc, zmax)

				ViewPlaneX()
				Normal(nx, ny, nz)

				ViewTile()

			else:
				txt = 'The wake flow tool did not finish successfully. Check the terminal for errors and make sure the '
				txt += 'following files are present:\n'
				txt += ''.join(['_mesh/', self.computation, '_faces_original.cpr\n'])
				txt += ''.join(
					[self.computation, '_nodes.cpr if there are solved motions, otherwise _mesh/nodes_original.cpr\n'])
				txt += ''.join([self.computation, '_vel.cpr\n'])
				# print '> Could not find wake flow files. Macro interrupted.'
				print ''.join(['\n > ', txt, '\n'])
				Warning(txt)

		def go(self):
			""" Main function launching the plugin workflow"""

			inputCheck = self.checkInputValues()
			if inputCheck != 'ok':
				return

			self.runWakeFlowTool()
			self.openResultsCFV()


			print '\n > END OF SCRIPT\n'


	z = MyDialogue()
