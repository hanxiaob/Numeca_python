#                                                                             #
#                         Represent free surface                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	  : 2012
#______________________________________________________________________________
#
# Description: Represent free surface
# Changes:
#
# DATE        IMPLEMENTER         TYPE OF MODIFICATION
#
#______________________________________________________________________________


from cfv import *

def Represent_free_surface():
	
	print ' '
	print ' > START OF SCRIPT: REPRESENT_FREE_SURFACE'
	print ' '
	
	# check if mono or multi-fluid project and probes
	qnt_exist_mf = 0
	qnt_exist_mf = QntFieldExist('Mass Fraction')
	if qnt_exist_mf == 0:
		print "Free surface representation is not possible for mono-fluid projects and probes"
		#Warning("Free surface representation is not possible for mono-fluid projects and probes")
		CFViewWarning("Free surface representation is not possible for mono-fluid projects and probes")
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
		# Clean fields and surfaces
		qnt_exist = 0
		qnt_exist = QntFieldExist('Wave Elevation')
		if qnt_exist == 1:
			QntFieldRemove('Wave Elevation')
		DeleteFromProjectRegExp('ISO Mass Fraction=0.5*')

		# Compute iso-surface and represent wave elevation with isolines
		QntFieldScalar('Mass Fraction')
		SclIsoSurfaceValue(0.5)
		SclIsoSurfaceSave()
		UnselectFromViewRegExp('')
		SelectFromProjectRegExp('ISO Mass Fraction=0.5*')
		GmtToggleGrid()
		QntFieldDerived(0 ,'Wave Elevation' ,'z' ,'' ,'0')
		SclContourStrip()
		ColormapStripesOnly()
		RprRangeActiveSurfaces()
		UpdateColormapJet()
		range_mf = []
		range_mf = QuantityRangeActiveSurfaces()
		SclIsolineMulti(2,4,range_mf[0],range_mf[1],(range_mf[1]-range_mf[0])/30,1)
	else:
		print "Free surface representation is not available for 2D projects"
		#Warning("Free surface representation is not available for 2D projects")
		CFViewWarning("Free surface representation is not available for 2D projects")
		print ' '
		print ' > END OF SCRIPT'
		print ' '
		return
	
	print ' '
	print ' > END OF SCRIPT'
	print ' '