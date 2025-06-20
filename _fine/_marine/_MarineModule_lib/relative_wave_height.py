#                                                                             #
#                         Represent free surface                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Teissedre
#       Date	  : 15-12-2017
#______________________________________________________________________________
#
# Description: Represent free surface
# Changes:
#
# DATE        IMPLEMENTER         TYPE OF MODIFICATION
#
#______________________________________________________________________________


from cfv import *
import os, sys, platform, shutil
from Tk import *


def displayRWH2(z_init):
	""" Display relative wave height"""
	# Compute data for Mass Fraction Iso-surface
	QntFieldScalar('Mass Fraction')
	SclIsoSurfaceValue(0.5)
	SclIsoSurfaceSave()
	UnselectFromViewRegExp('')
	SelectFromProjectRegExp('ISO Mass Fraction=0.5*')
	GmtToggleGrid()

	QntFieldDerived(0, 'Wave Elevation', 'z-{}'.format(z_init), '', '0')
	SclContourStrip()
	ColormapStripesOnly()
	UpdateColormapJet()
	RprRangeActiveSurfaces()
	range_mf = QuantityRangeActiveSurfaces()
	SclIsolineMulti(2, 4, range_mf[0], range_mf[1], (range_mf[1] - range_mf[0]) / 30, 1)

	print '\n > END OF SCRIPT\n'


### S
# Create dialogue box in case of non-existence of .sim file
class MyDialogue(DialogueBox):

	def __init__(self):
		DialogueBox.__init__(self, "Initial free-surface location")
		self.z_init = 0.0
		Frame1 = self.frame()
		Frame1.pack(side="top", fill="x")
		self.fs_location = Frame1.entry(label="Enter location", width=12, value=0, unit='\[m]', labelwidth=20).pack(
			side="top")
		Frame1.button(text=" Apply ", command=Command(self, MyDialogue.apply)).pack(side="right", anchor='e')
		self.showCentered()

	def apply(self):
		z_init = self.fs_location.getFloatValue()
		displayRWH(z_init)
		# 33850
		self.close()
### E

def Relative_wave_height():
	""" Main"""

	print ' '
	print ' > START OF SCRIPT: RELATIVE_WAVE_HEIGHT'
	print ' '
	
	# check if mono or multi-fluid project and probes
	qnt_exist_mf = QntFieldExist('Mass Fraction')
	if qnt_exist_mf == 0:
		print "Relative wave height representation is not possible for mono-fluid projects and probes"
		#Warning("Wave height representation is not possible for mono-fluid projects and probes")
		CFViewWarning("Relative wave height representation is not possible for mono-fluid projects and probes")
		print '\n > END OF SCRIPT\n'' '
		return

	# check 2D/3D
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
		
	if check_2d == 1:
		print "Relative wave height representation is not available for 2D projects"
		# Warning("Free surface representation is not available for 2D projects")
		CFViewWarning("Relative wave height representation is not available for 2D projects")
		print '\n > END OF SCRIPT\n'
		return

	else:
		# Clean fields and surfaces
		qnt_exist = 0
		qnt_exist = QntFieldExist('Wave Elevation')
		if qnt_exist == 1:
			QntFieldRemove('Wave Elevation')
		DeleteFromProjectRegExp('ISO Mass Fraction=0.5*')

		path = GetProjectPath()
		cfv_file = GetProjectName()
		computation = cfv_file[:-4]
		sim_file = computation + '.sim'
		sim_file = path + os.sep + sim_file

### S
		# Check if .sim file exists
		if (os.path.exists(sim_file) == 0):
			print " > SIM file is not present in the computation path"
			Warning("SIM file is not present in the computation path. "
					"Press 'OK' and compute your chosen value for the initial free-surface location.")
			MyDialogue()

		else:
			# Look for the initial free-surface location in the .sim file
			with open(sim_file,'r') as f:
				sim_content = f.readlines()
			try:
				z_init = float(sim_content[2 + sim_content.index('*** FLUID1-FLUID2 INTERFACE LOCATION\n')])
				displayRWH2(z_init)
			except ValueError:
				Warning("Free surface position could not be read from SIM file. "
						"Press 'OK' and compute your chosen value for the initial free-surface location.")
				MyDialogue()
