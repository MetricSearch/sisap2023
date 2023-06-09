# Jensen Shannon Distance
import math
import numpy as np

# from sisap2023.msed import msed
# from sisap2023.similarity import euclid

def jsd_dist(A,B):
    """first param is an row - an array, second is matrix of rows (values)
       returns a row vector"""
    ha = h(A)
    hb = h(B)
    hc = h(A+B)
    hacc = ( hb - hc ) + ha
    # he = - np.divide( np.nansum( hacc,1,keepdims=True ), math.log(4) ) + 1
    he = - np.divide( np.nansum( hacc,1 ), math.log(4) ) + 1
    rtn = np.sqrt( np.where(he<0,0,he) )   
    return rtn

def h(x):
    return np.multiply( -x,np.log(x) )

# test code
# p1 = np.array([ 0, 0.1, 0.9 ])
# p2 = np.array([ 0.9, 0, 0.1 ])
# p3 = np.array([[ 0.9, 0, 0.1 ], [0, 0.5, 0.5]])
# print(jsd(p1,p3))
# sed = msed( np.vstack( (p1,p2) ) ) 
# eu = euclid(p1,p3)
# print(eu)
# print(sed)

