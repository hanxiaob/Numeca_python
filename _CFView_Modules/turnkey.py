def ThreeDim_StaticPressure():
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
	ViewActivate (viewName_3d)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
# suction and pressure sides
	SelectFromViewRegExp('*I*')
	GmtRepetitionToggle()
	GmtRepetitionNumber(3)
	GmtToggleBoundary()
	QntFieldScalar('Static Pressure')
	SclContourSmooth()
	RprColormap(1)
# hub
	SelectFromViewRegExp('*J 1 *')
#	GmtRepetitionToggle()
#	GmtRepetitionNumber(3)
#	QntFieldScalar('Static Pressure')
	GmtToggleGrid()
	SclContourSmooth()
	RprColormap(1)
	ViewPlaneZ()
	ViewZoomAll ()
#        InsertText(0.0,0.8, 0 ,'Contour plot of the wall static pressure')
	return viewName_3d


#
# Plot the meridional velocity
#
def Meridional_Vm () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
        QntFieldScalar('Vm')
        SclContourSmooth()
	RprColormap(1)
#    	InsertText(0.0,0.9, 0 ,'Contour plot of the circumferentially averaged meridional velocity')



#
# Plot the absolute total temperature 
#
def Meridional_AbsoluteTotalTemperature () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
        QntFieldScalar('Absolute Total Temperature')
        SclContourSmooth()
	RprColormap(1)
#	InsertText(0.0,0.9, 0 ,'Contour plot of the circumferentially averaged absolute total temperature')


#
# Plot the absolute total pressure
#
def Meridional_AbsoluteTotalPressure () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
        QntFieldScalar('Absolute Total Pressure')
        SclContourSmooth()
	RprColormap(1)
#	InsertText(0.0,0.9, 0 ,'Contour plot of the circumferentially averaged meridional absolute total pressure')


#
# Plot the static pressure
#
def Meridional_StaticPressure () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
        QntFieldScalar('Static Pressure')
        SclContourSmooth()
	RprColormap(1)
#	InsertText(0.0,0.9, 0 ,'Contour plot of the circumferentially averaged meridional static pressure')



#
# Plot the vectors in the meridional plane
#
def Meridional_Vectors () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
        QntFieldVector('Wxyz')	
#
	b1 = StructuredDomainSize (1)
	imax = int(b1[0])
	jmax = int(b1[1])
	kmax = int(b1[2])
        VectorAll(1,imax,1,1,jmax,1)
	RprColormap(1)
#	InsertText(0.0,0.9, 0 ,'Vectors of the circumferentially averaged solution')


#
# Plot the static pressure along the blade walls
#
def Blade_StaticPressureDistribution () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
	ViewActivate (viewName_3d)
	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
	SelectFromViewRegExp('*I*')
        QntFieldScalar('Static Pressure')
	RprColormap(1)
#
	b1 = StructuredDomainSize (1)
	imax = int(b1[0])
	jmax = int(b1[1])
	kmax = int(b1[2])
	j1 = int(1)
	j2 = int((jmax-1)/3.+1)
	j3 = int((jmax-1)/2.)
	j4 = int( jmax-1-j2)
	j5 = int( jmax-2)
#
        viewname1 = SclPlotGridLine(2,4,0,j2,0,512) 
	PlotCurveType(0,0,0, 0,0,0,1,2,0,0,0,0,0.4,4,0,0)
#	              color = black                    visibility
#
#       PlotCurveType arguments
#       =======================
#       Line type   : colour, pattern, endcap, linejoin, visibility, width
#       Marker type : colour, light,   size,   symbol,   filled,     visibility
#
        SclPlotGridLine(2,4,0,j3,0,512)	
	PlotCurveType(0,1,1, 0,0,0,1,2,0,0,0,0,0.4,5,1,0)
#	              color = red 
        SclPlotGridLine(2,4,0,j4,0,512)	
	PlotCurveType(120,1,1, 0,0,0,1,2,0,0,0,0,0.4,6,0,0)
#	              color = green 
	ViewActivate(viewname1)
#	InsertText(0.0, 0.86,0 ,'Pressure distribution along the blade walls')
#	InsertText(0.0, 0.80,0 ,'box       : near hub distribution')
#	InsertText(0.0, 0.74,0 ,'circle   : mid-span distribution')
#	InsertText(0.0, 0.68,0 ,'diamond : near tip distribution')
	return viewname1

#
# Plot the Absolute Total Pressure distributions in the meridional plane
#
def MeridionalStreamwiseDistribution_AbsoluteTotalPressure () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
    	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
	SelectFromViewRegExp('Domain 1')
        QntFieldScalar('Absolute Total Pressure')
	RprColormap(1)
#
	b1 = StructuredDomainSize (1)
	imax = int(b1[0])
	jmax = int(b1[1])
	kmax = int(b1[2])
	print imax, jmax, kmax
	j1 = int(1)
	j2 = int((jmax-1)/3.+1)
	j3 = int((jmax-1)/2.)
	j4 = int( jmax-1-j2)
	j5 = int( jmax-2)
#
        viewname1=SclPlotGridLine(2,4,1,j2,0,imax)	
	PlotCurveType(0,0,0, 0,0,0,1,2,0,0,0,0,0.4,4,0,0)
#	              color = black 
#
#       PlotCurveType arguments
#       =======================
#       Line type   : colour, pattern, endcap, linejoin, visibility, width
#       Marker type : colour, light,   size,   symbol,   filled,     visibility
#
        SclPlotGridLine(2,4,1,j3,0,imax)	
	PlotCurveType(0,1,1, 0,0,0,1,2,0,0,0,0,0.4,5,1,0)
#	              color = red 
        SclPlotGridLine(2,4,1,j4,0,imax)	
	PlotCurveType(120,1,1, 0,0,0,1,2,0,0,0,0,0.4,6,0,0)
#	              color = green 
	ViewActivate(viewname1)
#	InsertText(0.0, 0.86,0 ,'Streamwise distribution of the absolute total pressure')
#	InsertText(0.0, 0.80,0 ,'box        : near hub distribution')
#	InsertText(0.0, 0.74,0 ,'circle    : mid-span distribution')
#	InsertText(0.0, 0.68,0 ,'diamond  : near tip distribution')


#
# Plot the Absolute Total Pressure distributions in the meridional plane
#
def MeridionalSpanwiseDistribution_AbsoluteTotalPressure () :
	from CFView import *
	global viewName_3d
	global viewName_me
#
# Initialize ViewName_3d
#
	try :
		if (viewName_3d != '') :
			print viewName_3d			
			
	except NameError, AttributeError :
		viewName_3d = ViewName ()
#
# Initialize ViewName_me & read the meridional project
#

	try :
		if (viewName_me != '') :
			print viewName_me			
			
	except NameError, AttributeError :
		import string
		projectname_3d = ProjectFile ()
		l=len(projectname_3d)
		projectname_me = projectname_3d[0:l-3]
		projectname_me = projectname_me + 'me.cfv'
		print projectname_me
		viewName_me = FileOpenProject(projectname_me)
#
	ViewActivate (viewName_me)
    	LimitsFull()
     	DeleteTextAll()
     	DeleteAll()
	SelectFromViewRegExp('Domain 1')
        QntFieldScalar('Absolute Total Pressure')
	RprColormap(1)
#
	b1 = StructuredDomainSize (1)
	imax = int(b1[0])
	jmax = int(b1[1])
	kmax = int(b1[2])
	print imax, jmax, kmax
	i1 = int(1)
	i2 = int((imax-1)/3.+1)
	i3 = int((imax-1)/2.)
	i4 = int( imax-1-i2)
	i5 = int( imax-2)
#
        viewname1=SclPlotGridLine(2,4,0,i1,0,jmax)	
	PlotCurveType(300,1,1,0,0,0,1,2,0,0,0,0,0.4,2,0,0)
#	              color = magenta 
#
#       PlotCurveType arguments
#       =======================
#       Line type   : colour, pattern, endcap, linejoin, visibility, width
#       Marker type : colour, light,   size,   symbol,   filled,     visibility
#
        SclPlotGridLine(2,4,0,i2,0,jmax)	
	PlotCurveType(0,1,1, 0,0,0,1,2,0,0,0,0,0.4,4,0,0)
#	              color = red 
        SclPlotGridLine(2,4,0,i3,0,jmax)	
	PlotCurveType(0,0,0, 0,0,0,1,2,0,0,0,0,0.4,5,0,0)
#	              color = black 
        SclPlotGridLine(2,4,0,i4,0,jmax)	
	PlotCurveType(120,1,1, 0,0,0,1,2,0,0,0,0,0.4,6,0,0)
#	              color = green 
        SclPlotGridLine(2,4,0,i5,0,jmax)	
	PlotCurveType(240,1,1, 0,0,0,1,2,0,0,0,0,0.4,7,0,0)
#	              color = blue 
	ViewActivate(viewname1)
	PlotType(1,0,4,0,7,50000,200000,0,1)
	PlotHAxisLabel(0.15,4,1,10,0,1,1,0,0,1,0,0,0,0 ,'Absolute Total Pressure')
	PlotVAxisLabel(0.15,4,1,10,2,0,0,1,0,1,0,0,0,0 ,'Normalized Arc Length')
	PlotHGridLines(0,0,0,1,0,0,0,1,0,0,0,2,0,0,0,1)
	PlotVGridLines(0,0,0,1,0,0,0,1,0,0,0,2,0,0,0,1)
	PlotHAxisTicks(0,0,0,2,0.1,10,50000,200000)
	PlotHAxisTicksLabels(0.04,1,10,0,1,1,0,0,1,0,0,0,0,0,0,6)
	PlotVAxisTicks(0,0,0,2,0.1,10,0,1)
	PlotVAxisTicksLabels(0.04,1,10,2,0,1,0,0,1,0,0,0,0,0,0,6)
        ViewZoomAll ()
#	InsertText(0.0, 0.86,0 ,'Spanwise distribution of absolute total pressure')
#	InsertText(0.0, 0.80,0 ,'plus       : near inlet distribution           ')
#	InsertText(0.0, 0.74,0 ,'box        : near leading edge distribution ')
#	InsertText(0.0, 0.68,0 ,'circle    : intermediate distribution        ')
#	InsertText(0.0, 0.62,0 ,'diamond  : near trailing edge distribution')
#	InsertText(0.0, 0.56,0 ,'triangle : near outlet distribution          ')
	return viewname1


#
# Generate the postscript files
#
def EncapsulatedPostscript_files () :
#
	from CFView import *
	import string
#
	projectname_3d = ProjectFile ()
	l=len(projectname_3d)
#
	MeridionalSpanwiseDistribution_AbsoluteTotalPressure ()
	filename = projectname_3d[0:l] + '.1.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_AbsoluteTotalTemperature ()
	filename = projectname_3d[0:l] + '.2.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Blade_StaticPressureDistribution () 
	filename = projectname_3d[0:l] + '.3.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_AbsoluteTotalPressure ()
	filename = projectname_3d[0:l] + '.4.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_StaticPressure ()
	filename = projectname_3d[0:l] + '.5.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	ThreeDim_StaticPressure () 
	filename = projectname_3d[0:l] + '.6.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_Vectors ()
	filename = projectname_3d[0:l] + '.7.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	MeridionalStreamwiseDistribution_AbsoluteTotalPressure ()
	filename = projectname_3d[0:l] + '.8.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#	ViewClose ()
#
	Meridional_Vm () 
	filename = projectname_3d[0:l] + '.9.eps'
	print filename
	Update ()
	Print(1, 0, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()



def EncapsulatedPostscript_files1 () :
#
	from CFView import *
	import string
	from turnkey import *
#	from CFView import *
#
	projectname_3d = ProjectFile ()
	l=len(projectname_3d)
#
	viewname_3d = ThreeDim_StaticPressure () 
	filename = projectname_3d[0:l] + '.6.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	viewname = Blade_StaticPressureDistribution () 
	filename = projectname_3d[0:l] + '.3.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	viewname_tmp = MeridionalSpanwiseDistribution_AbsoluteTotalPressure ()
	filename = projectname_3d[0:l] + '.1.eps'
	print filename
#
# Close all three-dimensional views
#
	ViewActivate (viewname)
	ViewClose (viewname) 
	ViewActivate (viewname_3d)
	ViewClose (viewname_3d)
	print viewname
	print viewname_3d
#
	ViewActivate (viewname_tmp)
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_AbsoluteTotalTemperature ()
	filename = projectname_3d[0:l] + '.2.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_AbsoluteTotalPressure ()
	filename = projectname_3d[0:l] + '.4.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_StaticPressure ()
	filename = projectname_3d[0:l] + '.5.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	Meridional_Vectors ()
	filename = projectname_3d[0:l] + '.7.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#
	MeridionalStreamwiseDistribution_AbsoluteTotalPressure ()
	filename = projectname_3d[0:l] + '.8.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#	ViewClose ()
#
	Meridional_Vm () 
	filename = projectname_3d[0:l] + '.9.eps'
	print filename
	Update ()
	Print(1, 1, 0, 0, 100, 640, 480, 0, filename, '')
	Update ()
#

