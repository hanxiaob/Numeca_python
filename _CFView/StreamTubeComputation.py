#--------------------------------------------------------------------------------------#
#                          StreamTubeComputation                                       #
#--------------------------------------------------------------------------------------#
#    NUMECA International                                                              #
#       E. Robin                                                            nov 1999   #
#--------------------------------------------------------------------------------------#
# Description : performs the computation of a user provided function on a set of       #
#               flow tubes (to be applied on 2D averaged flow)                         #
#--------------------------------------------------------------------------------------#

from Curve import *
from CFView import *

#--------------------------------------------------------------------------------------#

def AbsTotPressWeight() :
    QntFieldDerived(2,'AbsTotPressWeight','weight*Absolute Total Pressure',
					  'weight*Absolute Total Pressure',
					  'weight*Absolute Total Pressure')
    return 'AbsTotPressRhoV'

#--------------------------------------------------------------------------------------#

def distance(p1, p2) :
    SetProjectEquation(0, 'distance', '1')
    return CurveSegmentIntegral(p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],0,0,1)

#--------------------------------------------------------------------------------------#

def massFlow(p1,p2) :
    SetProjectEquation(2, 'massFlow', 
                       '0.5* y * weight * Wxyz_X / sqrt(Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y)',
                       '0.5* y * weight * Wxyz_Y / sqrt(Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y)',
		       '0')
    return CurveSegmentIntegral(p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],0,0,1)
				   	   
#--------------------------------------------------------------------------------------#

def efficiency(p1, p2):
    SetProjectEquation(0, 'distance', 'weight*Absolute Total Pressure')
    return CurveSegmentIntegral(p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],0,0,1)
				   
#--------------------------------------------------------------------------------------#

def streamTubeCompute(nTubes, inletName, outletName):
    inlet  = Curve(inletName)
    if inlet.type() == 'p' : raise AttributeError, 'Inlet name does not match a boundary curve'
    outlet = Curve(outletName)
    if outlet.type() == 'p' : raise AttributeError, 'Outlet name does not match a boundary curve'

    l = inlet.length()
    dl = l/(nTubes)
    l = dl
    s =[]

    for i in range(0,nTubes-1):
	pi = inlet.pointAtDistance(l)
	ci = Curve(VecLineLocal(pi.x_,pi.y_,0, 0,0,1))
	pcin = ci.point(ci.numOfPoints()-1)
        pcinn = ci.point(ci.numOfPoints()-2)
	dpci = norm(pcin-pcinn)
	d_po = outlet.closestPoint(pcin,Point(0, 0, 1))
	dist = d_po[0]
	if (dist*dist > dpci):   # line ends on outlet if last point is closer 
	    print `i`+'e vector line does not end on the outlet '+outletName
	else:
	    s.append(ci)
	l=l+dl
    return s

#--------------------------------------------------------------------------------------#

def streamTubeRatioAnalysis(nTubes, inletName, outletName, integralFctModule, integralFctName):
    if integralFctModule != 'StreamTubeComputation' :
	eval('from '+integralFctModule+' import *') 
    if nTubes<2 : raise AttributeError, 'number of flow tubes is less than 2'
    
    s=streamTubeCompute(nTubes, inletName, outletName)
	
    nTubes = len(s)-1   # tubes made between 2 streamlines
    v=[]
    pIn=[]
    pOut=[]
    for i in range(0,nTubes):
	p1In  = s[i].point(1)
	p2In  = s[i+1].point(1)
        p1Out = s[i].point(s[i].numOfPoints()-2)
	p2Out = s[i+1].point(s[i+1].numOfPoints()-2)
	pIn.append((p1In+p2In)/2)
	pOut.append((p1Out+p2Out)/2)
	num = eval(integralFctName +'('+`p1Out`+','+`p2Out`+')')
	den = eval(integralFctName +'('+`p1In`+','+`p2In`+')')
	v.append(num/den)
	print v[i]

    return [pIn, pOut, v]

#--------------------------------------------------------------------------------------#

def streamTubeSectionAnalysis(nTubes, inletName, outletName, integralFctModule, integralFctName):
    if integralFctModule != 'StreamTubeComputation' :
	eval('from '+integralFctModule+' import *') 
    if nTubes<2 : raise AttributeError, 'number of flow tubes is less than 2'
    
    s=streamTubeCompute(nTubes, inletName, outletName)
	
    nTubes = len(s)-1   # tubes made between 2 streamlines
    v=[]
    pIn=[]
    pOut=[]
    for i in range(0,nTubes):
	p1In  = s[i].point(1)
	p2In  = s[i+1].point(1)
        p1Out = s[i].point(s[i].numOfPoints()-2)
	p2Out = s[i+1].point(s[i+1].numOfPoints()-2)
	pIn.append((p1In+p2In)/2)
	pOut.append((p1Out+p2Out)/2)
	v.append(eval(integralFctName +'('+`p1Out`+','+`p2Out`+')'))
	print v[i]

    return [pIn, pOut, v]

#--------------------------------------------------------------------------------------#

def streamTubeAlongAnalysis(nTubes, nStations, inletName, outletName, 
			    integralFctModule, integralFctName):
    if integralFctModule != 'StreamTubeComputation' :
	eval('from '+integralFctModule+' import *') 
    if nTubes<2 : raise AttributeError, 'number of flow tubes is less than 2'

    curves=streamTubeCompute(nTubes, inletName, outletName)
    v=[]

    for iTube in range(0,len(curves)-1):
	c1 = curves[iTube]
	c2 = curves[iTube+1]

	p1i = c1.point(1)
	p2i = c2.point(1)
	p1=[]
	p2=[]
	p1.append(p1i)
	p2.append(p2i)

	vi=[]
	vi.append(eval(integralFctName + '('+`p1i`+','+`p2i`+')'))
	if c1.length() > c2.length() :
	    dl = c2.length()/nStations
	else:
	    dl = c1.length()/nStations
	for i in range(1,nStations):
	    l = dl*i
	    p1i = c1.pointAtDistance(l)
	    p2i = c2.pointAtDistance(l)
	    p1.append(p1i)
	    p2.append(p2i)
	    vi.append(eval(integralFctName + '('+`p1i`+','+`p2i`+')'))
	v.append(vi)

    return [p1, p2, v]    
    
#--------------------------------------------------------------------------------------#
#                          StreamTubeAnalysis                                          #
#--------------------------------------------------------------------------------------#
