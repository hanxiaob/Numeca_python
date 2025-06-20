import string
from turnkey import *
#	from CFView import *
#
projectname_3d = ProjectFile ()
l=len(projectname_3d)
#
viewname_3d = ThreeDim_StaticPressure () 
filename = projectname_3d[0:l] + '.6.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
viewname = Blade_StaticPressureDistribution () 
filename = projectname_3d[0:l] + '.3.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
viewname_tmp = MeridionalSpanwiseDistribution_AbsoluteTotalPressure ()
filename = projectname_3d[0:l] + '.1.jpeg'
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
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
Meridional_AbsoluteTotalTemperature ()
filename = projectname_3d[0:l] + '.2.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
Meridional_AbsoluteTotalPressure ()
filename = projectname_3d[0:l] + '.4.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
Meridional_StaticPressure ()
filename = projectname_3d[0:l] + '.5.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
Meridional_Vectors ()
filename = projectname_3d[0:l] + '.7.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
MeridionalStreamwiseDistribution_AbsoluteTotalPressure ()
filename = projectname_3d[0:l] + '.8.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#	ViewClose ()
#
Meridional_Vm () 
filename = projectname_3d[0:l] + '.9.jpeg'
print filename
Update ()
Print(7, 1, 0, 0, 100, 640, 480, 0, filename, '')
Update ()
#
Quit ()
#

