#--------------------------------------------------------------------------------------------#
#                       Curve.py                                                             #
#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         Etienne Robin                                                           oct 1999   #
#--------------------------------------------------------------------------------------------#
# Description : curve as a list of points                                                    #
#               can be shared with C++ code                                                  #
#--------------------------------------------------------------------------------------------#

from CFView_Curve import *

from math         import *
from types        import *
from Point        import *

#--------------------------------------------------------------------------------------------#

class Curve:

    # constructor and destructor
    def __init__(self, name=None):
        self.name_ = name
        if name == None :
            self.type_ = 'p'
            self.points_ = []
        else:
            self.impl_ = Curve_getPointer(name)
            if self.impl_ != 0 :
                print 'Curve '+name+' found in CFView'
                self.type_ = 'c'
            else:
                print 'Curve '+name+' is a new curve'
                self.type_ = 'p'
                self.points_ = []

    def __del__(self):
        if self.type_ == 'c' :
            Curve_releasePointer(self.impl_)

    # interface members
    def type(self): return self.type_


    def numOfPoints(self):
        if self.type_=='c' :
            return Curve_numOfPoints(self.impl_)
        else:
            return len(self.points_)


    def length(self):
        if self.type_=='c' :
            l=Curve_length(self.impl_)
        else:
            npoints = len(self.points_)
            l=0
            if npoints > 1 :
                p1=self.points_[0]
                for i in range(1,npoints):
                    p2=self.points_[i]
                    l=l+norm(p2-p1)
                    p1=p2
        return l

    def point(self, i):
        if self.type_ == 'c' :
            p= Curve_point(self.impl_,i)
            return Point(p[0], p[1], p[2])
        else:
            if i>=self.numOfPoints() :
                raise AttributeError, 'Curve.point : index >= number of points'
            else:
                return self.points_[i]


    def addPoint(self, p):
        if self.type_ == 'c' :
            raise TypeError, 'Internal CFView curves cannot be modified'
        else:
            if p.__class__.__name__=='Point' :
                self.points_.append(p)
            else:
                raise TypeError, 'Curve.addPoint : unexpected argument type '+type(p)

    def pointAtDistance(self, d):
        if d<0 : raise AttributeError, 'Curve.pointAtDistance : negative distance'
        if self.type_ == 'c' :
            pt = Curve_pointAtDistance(self.impl_,d)
            return Point(pt[0], pt[1], pt[2])
        else:
            npoints=self.numOfPoints()
            if npoints < 2 : raise AttributeError, 'Curve.pointAtDistance : curve with less than 2 points'
            p1=self.points_[0]
            l=0
            for i in range(1,npoints):
                p2=self.points_[i]
                il=norm(p2-p1)
                if (l+il)< d : l=l+il
                else: break
                p1=p2
            if l+il<d : raise AttributeError, 'Curve.pointAtDistance : distance > curve length'
            p = p1+(p2-p1)*(d-l)/il
            return p

    def closestPoint(self, p, n):
        if self.type_ == 'c' :
            res = Curve_closestPoint(self.impl_,p.x_,p.y_,p.z_,n.x_,n.y_,n.z_)
            pr = res[1]
            return [res[0],Point(pr[0], pr[1], pr[2])]
        else:
            raise TypeError, 'Curve.closestPoint not implemented for python based curves'

    def showInPlot(self, qttyName, qttyValues):
        if (self.numOfPoints()==len(qttyValues)):
            if self.type_=='p':
                l = len(self.points_)
                points = []
                for i in range(0,l): points.append(self.points_[i].asTuple())
                Curve_showInPlot(0,
                                 self.name_,
                                 qttyName,
                                 points,
                                 qttyValues)
                del points
            else:
                #bug 3071
                l = Curve_numOfPoints(self.impl_)
                points = []
                for i in range(0,l):
                    points.append(Curve_point(self.impl_,i))
                    #print Curve_point(self.impl_,i)
                    

                Curve_showInPlot(0,
                                 #3071
                #Curve_showInPlot(1,
                                 
                                 self.name_,
                                 qttyName,
                                 #3071
                                 points,
                                 
                                 qttyValues)
        else:
            raise AttributeError, 'Curve.showInPlot : num of values not equal num of curve points'

                                 
    def computeIntegral(self, type, eqX, eqY='', eqZ=''):
        if self.type_=='c' :
            return Curve_computeIntegral(self.name_,type,'tempQnt',eqX, eqY, eqZ)
        else:
            raise TypeError, 'Curve.computeIntegral not implemented for python based curves'



#--------------------------------------------------------------------------------------------#
#                       Curve.py                                                             #
#--------------------------------------------------------------------------------------------#
