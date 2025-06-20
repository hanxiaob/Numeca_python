#                                                                             #
#                         Plot wave elevation                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	  : 
#______________________________________________________________________________
#
# Description: Plot wave elevation
# Changes:
#
# DATE        IMPLEMENTER          TYPE OF MODIFICATION
#15-12-2017	  B. Teissedre		    Defect 32044 - Adapt for catamaran cases
# 12-01-2018  Baptiste Teissedre	#32044
#29-04-2019   Anna Mir             #37498
#______________________________________________________________________________

from cfv import *
from Curve import *
import os, sys

def Plot_wave_elevation_along_X():
	
	print '\n > START OF SCRIPT: PLOT_WAVE_ELEVATION_ALONG_X\n'

	# check if mono or multi-fluid project
	qnt_exist_mf = 0
	qnt_exist_mf2 = 0
	qnt_exist_mf = QntFieldExist('Mass Fraction')
	if qnt_exist_mf == 0 and qnt_exist_mf2 == 0:
		print "Wave elevation plot is not possible for mono-fluid projects and probes"
		#Warning("Wave elevation plot is not possible for mono-fluid projects and probes")
		CFViewWarning("Wave elevation plot is not possible for mono-fluid projects and probes")
		print '\n > END OF SCRIPT\n'
		return
		
	# check multi-domain
	nDom = NumberOfDomains()
	if nDom != 1:
		print "Wave elevation plot is not possible for multi-domain projects"
		#Warning("Wave elevation plot is not possible for multi-domain projects")
		CFViewWarning("Wave elevation plot is not possible for multi-domain projects")
		print '\n > END OF SCRIPT\n'
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
	
	if check_2d == 0:
		# Clean fields, surfaces, files
		qnt_exist = QntFieldExist('Wave Elevation')
		if qnt_exist == 1:
			QntFieldRemove('Wave Elevation')
		DeleteFromProjectRegExp('ISO Mass Fraction=0.5*')
		
		path = os.path.join(os.path.expanduser("~"), '.numeca', 'tmp')
		file1 = os.path.join(path, 'elevation_tmp.dat')
		file2 = os.path.join(path, 'wave_elevation_curve_board1.dat')
		file3 = os.path.join(path, 'wave_elevation_curve_board2.dat')
		files = [file1, file2, file3]
		for f in files:
			if os.path.isfile(f):
				os.remove(f)

		# Plot wave elevation on boundaries
		QntFieldScalar('Mass Fraction')
		SclIsoSurfaceValue(0.5)
		SclIsoSurfaceSave()
		SelectFromProject('ISO Mass Fraction=0.5 .D1')
		GmtToggleGrid()
		QntFieldDerived(0, 'Wave Elevation', 'z', '', '0')
		SclPlotBoundary(0)
		PlotViewActivate('Wave Elevation')
		PlotPlaneX()
		ViewZoomAll()
	
		# Extract plot(s)
		CurvesNamesList = GetViewCurveList()
		if len(CurvesNamesList) == 1:
			SelectPlotCurves('Boundary  on ISO Mass Fraction=0.5 .D1')
			ActivePlotCurveOutput(file1,'Boundary  on ISO Mass Fraction=0.5 .D1')  # Save plot to .numeca folder
		else:
			length_list = [Curve(curve).numOfPoints() for curve in CurvesNamesList]
			good_index = length_list.index(max(length_list))
			goodCurve = CurvesNamesList[good_index]
			ActivePlotCurveOutput(file1, goodCurve)
		
		# Read the file from Cartesian plot of CFView
		with open(file1, 'r') as g:
			file_content = g.readlines()

		# Extract longest list if holes are present in free surface
		file_lists = []
		for i, line in enumerate(file_content):
			if 'Wave Elevation' in line:
				number_lines = int((line.split())[2])
				list_tmp = file_content[i+1: i+number_lines+1]
				file_lists.append(list_tmp)

		nbr_of_parts = len(file_lists)
		list_max = []
		max_lines = 0
		for l in file_lists:
			if len(l) > max_lines:
				max_lines = len(l)
				list_max = l

		# Extract vectors from content
		x1 = [float(x.split()[0]) for x in list_max]
		y1 = [float(x.split()[1]) for x in list_max]
		scalar1 = [float(x.rstrip().split()[3]) for x in list_max]

		# Find extremities along X
		xmin = x1[0]
		m = 0
		xmax = x1[0]
		M = 0
		for i in range(0, len(x1)):
			if x1[i] < xmin:
				xmin = x1[i]
				m = i
			elif x1[i] > xmax:
				xmax = x1[i]
				M = i

		# Find extremities along Y
		y2 = []
		for i in range(0, len(y1)):
			y2.append(y1[i])
		y2.sort()
		ymin = y2[0]
		ymax = y2[len(y1)-1]
		
		print '\nDomain extremities: Xmin={}, Xmax={}, Ymin={}, Ymax={}\n'.format(xmin, xmax, ymin, ymax)
		
		# Reverse Y extremities in case of negative Ymax
		ymin_tmp = ymin
		ymax_tmp = ymax
		if abs(ymax) < abs(ymin) and ymax > ymin:
			ymax = ymin_tmp
			ymin = ymax_tmp
		
		# separate list into the two board plots
		if x1[0] < x1[1]:    # list goes clockwise
			# 37498 if the indexes are not increasing list is empty
			if m+1 > M:
				xboard_one = x1[M:m+1]
			else:
				xboard_one = x1[m+1:M]

			xboard_one.reverse()
			xboard_two = x1[m:-1] + x1[0:M+1]

			if m + 1 > M:
				scalar_board_one = scalar1[M:m+1]
			else:
				scalar_board_one = scalar1[m+1:M]

			scalar_board_one.reverse()
			scalar_board_two = scalar1[m:-1] + scalar1[0:M+1]
		else:
			# 37498 if the indexes are not increasing list is empty
			if M+1 > m:
				xboard_one = x1[m:M+1]
			else:
				xboard_one = x1[M + 1:m]

			xboard_two_begin = x1[0:m+1]
			xboard_two_begin.reverse()
			xboard_two_end = x1[M:]
			xboard_two_end.reverse()
			xboard_two = xboard_two_begin + xboard_two_end

			if M + 1 > m:
				scalar_board_one = scalar1[m:M+1]
			else:
				scalar_board_one = scalar1[M+1:m]

			scalar_board_two_begin = scalar1[0:m+1]
			scalar_board_two_begin.reverse()
			scalar_board_two_end = scalar1[M:]
			scalar_board_two_end.reverse()
			scalar_board_two = scalar_board_two_begin + scalar_board_two_end

		board_list = []
		# Write vectors into a new file to be loaded into CFView
		if scalar_board_one:  # 37498 Save only if there are elements in the list
			with open(file2, 'w') as f:
				i = 0
				f.write('1 1 '+str(len(xboard_one))+' |Wave Elevation|\n')
				while i < len(xboard_one):
					f.write(str(xboard_one[i])+' '+str(scalar_board_one[i])+'\n')
					i = i+1
			board = {
				"name": "board1",
				"file": file2,
				"curve_type": [0,1,1,0,0,0,1,2,0,0,0,0,0.4,4,0,0]}
			board_list.append(board)

		if scalar_board_two:
			with open(file3, 'w') as f:
				i = 0
				f.write('1 1 '+str(len(xboard_two))+' |Wave Elevation|\n')
				while i < len(xboard_two):
					f.write(str(xboard_two[i])+' '+str(scalar_board_two[i])+'\n')
					i = i+1
			board = {
				"name": "board2",
				"file": file3,
				"curve_type": [240,1,1,0,0,0,1,2,0,0,0,0,0.3,4,0,0]}
			board_list.append(board)

		# Represent Cartesian plot
		for t in range(0, nbr_of_parts):
			for curveName in CurvesNamesList:
				SelectPlotCurves(curveName)
				DeletePlotCurves(curveName)

		for board in board_list:
			QntValidLoad(board["file"])
			QntValid('Wave Elevation|wave_elevation_curve_' + board["name"], '', 0)
			PlotViewActivate('Wave Elevation')
			PlotPlaneX()
			ViewZoomAll()
			SelectPlotCurves('wave_elevation_curve_' + board["name"])
			ctype_list = board["curve_type"]
			UpdateCurveType(*ctype_list)
			ShowHorizontalGridLines()
			ShowVerticalGridLines()
			LimitsFull()
			ToggleTicksOrientation()
			ViewTile()
			FitAbscissa()
	else:
		print "Wave elevation plot is not available for 2D projects"
		CFViewWarning("Wave elevation plot is not available for 2D projects")
		print '\n > END OF SCRIPT\n'
		return

	print '\n > END OF SCRIPT\n'
