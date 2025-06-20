#                                                                             #
#                         Compute wetted area                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	  : 2012
#______________________________________________________________________________
#
# Description: Compute body wetted area and display its value
#
# Changes:
#
# DATE        IMPLEMENTER         TYPE OF MODIFICATION
#
#______________________________________________________________________________

from cfv import *

def Compute_wetted_area():
	
	print ' '
	print ' > START OF SCRIPT: COMPUTE_WETTED_AREA'
	print ' '
	
	# check if mono or multi-fluid project and for probes
	qnt_exist_mf = 0
	qnt_exist_mf = QntFieldExist('Mass Fraction')
	if qnt_exist_mf == 0:
		print "Wetted area computation is not possible for mono-fluid projects and probes"
		#Warning("Wetted area computation is not possible for mono-fluid projects and probes")
		CFViewWarning("Wetted area computation is not possible for mono-fluid projects and probes")
		print ' '
		print ' > END OF SCRIPT'
		print ' '
		return
	
	# check 2D/3D
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
	
	if check_2d == 0:
		UnselectFromViewRegExp('')
		SelectTypeFromProject('SOL')

		# 33175 shallow water: remove ground from wetted area calculation
		RemoveFromView('zmin Solid')

		QntFieldScalar('Mass Fraction')
		SclContourSmooth()
		ColormapSmoothOnly()
		RprRangeActiveSurfaces()
		# Compute integral of the mass fraction of the solid patches
		wetted_surf = SclIntegral()
		wetted_surf_value = '%5.6f'%(wetted_surf)
		
		# Display the result in a text frame
		InsertText2('text0',0,0,0 ,'Wetted Surface = '+str(wetted_surf_value)+' m2')
		SetTextFontSize('text0',17)
	
	else:
		print "Wetted area calculation is not available for 2D projects"
		#Warning("Wetted area calculation is not available for 2D projects")
		CFViewWarning("Wetted area calculation is not available for 2D projects")
		print ' '
		print ' > END OF SCRIPT'
		print ' '
		return
	
	print ' '
	print ' > END OF SCRIPT'
	print ' '