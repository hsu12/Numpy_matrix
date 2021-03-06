# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 10:35:11 2016

@author: kaputj
"""
#ratedRPM  Rated Torque
import numpy as np


p=5             # number of pole pairs
ratedRPM=1050.0 # RPM for rated torque

Npointsi=16     # LUT points
Npointst=512    # numpoints to search over

Ld_Saturation_pct=0.85
Lq_Saturation_pct=0.7

def find_gt(T, Tmax):
    Q = []
    for i in range(len(T)):
        if (T[i] >= Tmax):
            Q.append(i)
    return Q

def user_inputs():
    #LD = float(raw_input('LD(H, saturated): '))
    #LQ = float(raw_input('LQ(H, saturated): '))
    LD = float(raw_input('LD(H, measured): ')) * Ld_Saturation_pct
    LQ = float(raw_input('LQ(H, measured): ')) * Lq_Saturation_pct
    Vrms = float(raw_input('Vrms: '))
    LM = Vrms/(np.pi*5000/60)*np.sqrt(3)/np.sqrt(2)
    LM = round(LM, 4)
    TM = float(raw_input('Rated Torque(oz-ft): '))
    return LD, LQ, LM, TM/11.801

def test_inputs():
    return 0.040, 0.045, 0.1465, 46.0/11.801

def main():
    Ld, Lq, LambdaM, reqTorque = user_inputs()
    #Ld, Lq, LambdaM, reqTorque = test_inputs()
    MaxTorque = 0.0
    #reqTorque_plus15percent = reqTorque*1.15
    reqTorque_plus25percent = reqTorque*1.25
    Imax = 1.0
    reqImax = 0.0
    #while(MaxTorque < reqTorque_plus15percent):
    while(MaxTorque < reqTorque_plus25percent):

        Imax = Imax + 0.1
        Is = np.linspace(start=0,stop=Imax,num=Npointsi)
        theta = np.linspace(start=0,stop=np.pi,num=Npointst)

        Id = np.zeros((Npointsi,Npointst))#create three vector table
        Iq = np.zeros((Npointsi,Npointst))
        Te = np.zeros((Npointsi,Npointst))
    
        TeMax = np.zeros((Npointsi))
        
        index = np.zeros((Npointsi), dtype=np.int)
        idMTPA = np.zeros((Npointsi))
        iqMTPA = np.zeros((Npointsi))
        LambdaDMTPA = np.zeros((Npointsi))
        LambdaQMTPA = np.zeros((Npointsi))
        LambdaMTPA = np.zeros((Npointsi))
        
        for i in range(Npointsi):
            for j in range(Npointst):
                Id[i,j] = Is[i]*np.cos(theta[j])
                Iq[i,j] = Is[i]*np.sin(theta[j])

                Te[i,j] = 1.5 * p * ( (LambdaM * Iq[i,j]) + ((Ld - Lq) * Id[i,j] * Iq[i,j]) )
                
                TeMax[i]=max(Te[i,:])
                k = find_gt(Te[i,:], TeMax[i])
                index[i] = min(k)
                idMTPA[i] = Id[i,index[i]]
                iqMTPA[i] = Iq[i,index[i]]
                
                LambdaDMTPA[i] = LambdaM+Ld*idMTPA[i]
                LambdaQMTPA[i] = Lq*iqMTPA[i]
                LambdaMTPA[i] = np.sqrt(LambdaDMTPA[i]**2 + LambdaQMTPA[i]**2)
        
        #Temax[] is an arry of max torque for a given value in Is[i]
        MaxTorque = max(TeMax)
        if(reqImax == 0) and (MaxTorque >= reqTorque):
            reqImax = Imax
        TeRef = np.linspace(start=0,stop=MaxTorque,num=Npointsi)
        TeRefStep = TeRef[1] - TeRef[0]
                
        polyFluxRefMTPA = np.polyfit(TeMax,LambdaMTPA,deg=7)#export MTPA curv
        FluxRefMTPA = np.polyval(polyFluxRefMTPA, TeRef)#flux reference generated by MTPA CURV
        FluxRefMax = FluxRefMTPA[-1]

        #print MaxTorque*11.801, Imax
    
    #print TeRef
    #print FluxRefMTPA
    #print TeRefStep
    
    p2FluxRefMTPA = np.polyfit(TeMax, LambdaMTPA, deg=2)

    """
    Print Format:

    // Ld=0.045-15%, Lq=0.064-30%, LambdaM=0.1465, Tmax=40+15%
    //    0.040         0.045              0.1465       46
    FluxRefMTPA = 0.0032057*TeAbs*TeAbs + 0.0026468*TeAbs + 0.1457233;// IsMax=3.6
    FluxRefMTPA_Tmax = 0.0032057*Tmax*Tmax + 0.0026468*Tmax + 0.1457233;// MaxTorque=47.025 oz-ft

    0x0400,// Tmax, 40oz.ft,1/2HP, 2 (Abs Max 47)
    0x0310,// IsMax, 0x0298
    0x0373,// Pmax
    0x0335,// Rs3.4
    0x0040,// Ld0.045 -15%
    0x0045,// Lq0.064 -30%
    0x1465,// LambdaM0.1465

    """
    # // Ld=0.048-15%, Lq=0.064-30%, LambdaM=0.1465, Tmax=40
    #print '// Ld='+'{0:.3f}'.format(Ld),  
    print '// Ld='+'{0:.3f}'.format(Ld/Ld_Saturation_pct),
    print 'Lq='+'{0:.3f}'.format(Lq/Lq_Saturation_pct),
    print 'LambdaM='+str(LambdaM)+',',
    print 'Tmax='+'{0:.1f}'.format(reqTorque*11.801)
    # //    0.040         0.045              0.1465       40
    #print '//   ','{0:.3f}'.format(Ld),
    #print '       ','{0:.3f}'.format(Lq),
    #print '             ''{0:.4f}'.format(LambdaM),
    #print '      '+'{0:.1f}'.format(reqTorque*11.801)
    # FluxRefMTPA = 0.0032057*TeAbs*TeAbs + 0.0026468*TeAbs + 0.1457233;// IsMax=3.6
    print 'FluxRefMTPA =',
    print str(round(p2FluxRefMTPA[0],7))+'*TeAbs*TeAbs +',
    print str(round(p2FluxRefMTPA[1],7))+'*TeAbs +',
    print str(round(p2FluxRefMTPA[2],7))+';',
    print ' // IsMax='+str(Imax)
    # *FluxRefMTPA = 0.0032057*TeAbs*TeAbs + 0.0026468*TeAbs + 0.1457233;// IsMax=3.6
    """
    print '*FluxRefMTPA =',
    print str(round(p2FluxRefMTPA[0],7))+'*TeAbs*TeAbs +',
    print str(round(p2FluxRefMTPA[1],7))+'*TeAbs +',
    print str(round(p2FluxRefMTPA[2],7))+';',
    print '  // IsMax='+str(Imax)
    """
    # FluxRefMTPA_Tmax = 0.0032057*Tmax*Tmax + 0.0026468*Tmax + 0.1457233;// MaxTorque=47.025 oz-ft
    print 'FluxRefMTPA_Tmax =',
    print str(round(p2FluxRefMTPA[0],7))+'*Tmax*Tmax +',
    print str(round(p2FluxRefMTPA[1],7))+'*Tmax +',
    print str(round(p2FluxRefMTPA[2],7))+';',
    print '// MaxTorque='+str(round(MaxTorque*11.801,3)), 'oz-ft\n'
    # *FluxRefMTPA_Tmax = 0.0032057*(*Tmax)*(*Tmax) + 0.0026468*(*Tmax) + 0.1457233;// MaxTorque=47.025 oz-ft
    """
    print '*FluxRefMTPA_Tmax =',
    print str(round(p2FluxRefMTPA[0],7))+'*(*Tmax)*(*Tmax) +',
    print str(round(p2FluxRefMTPA[1],7))+'*(*Tmax) +',
    print str(round(p2FluxRefMTPA[2],7))+';',
    print '// MaxTorque='+str(round(MaxTorque*11.801,3)), 'oz-ft\n'
    """

    # 0x0400, // Tmax, 40.0oz-ft, 1/2HP, 2 (Abs Max 47)
    TM = reqTorque*11.801
    TM4 = '{0:.1f}'.format(TM)
    if(TM < 100.0):
        print '0x0'+TM4[0:2]+TM4[3]+',',
    else:
        print '0x'+TM4[0:3]+TM4[4]+',',
    print '//', 'Tmax', TM4, 'oz-ft', 'HP', '#', '(Abs Max', '{0:.1f}'.format(MaxTorque*11.801), 'oz-ft)'

    # 0x0310, // IsMax, 3.10 A
    if(reqImax < 10.0):
        print '0x0'+str(reqImax)[0]+str(reqImax)[2]+'0,',
    else:
        print '0x'+str(reqImax)[0:2]+str(reqImax)[3]+'0,',
    print '//', 'IsMax', '{0:.2f}'.format(reqImax), 'A', '(AbsMax', Imax, 'A)'
    # 0x0373, // Pmax
    # Don't have access to Pmax
    print '0x0000, // Pmax'

    # 0x0335, // Rs 3.35
    # Don't have access to Rs
    print '0x0000, // Rs'

    # 0x0040, // Ld 0.045 -15%
    Ld4 = '{0:.3f}'.format(Ld)
    #print Ld4[0], Ld4[1], Ld4[2], Ld4[3], Ld4[4]
    print '0x'+Ld4[0]+Ld4[2:5]+',',
    print '//', 'Ld', '{0:.3f}'.format(Ld/Ld_Saturation_pct), '-15%'

    # 0x0045, // Lq 0.064 -30%
    Lq4 = '{0:.3f}'.format(Lq)
    print '0x'+Lq4[0]+Lq4[2:5]+',',
    print '//', 'Lq', '{0:.3f}'.format(Lq/Lq_Saturation_pct), '-30%'

    # 0x1465, // LambdaM 0.1465
    Lm4 = '{0:.4f}'.format(LambdaM)
    print '0x'+Lm4[2:6]+',',
    print '//', 'LambdaM', Lm4

    """
    print str(round(p2FluxRefMTPA[0],7))+'*TeAbs*TeAbs +',
    print str(round(p2FluxRefMTPA[1],7))+'*TeAbs +',
    print str(round(p2FluxRefMTPA[2],7))
    print 'Max Achievable Torque:', round(MaxTorque*11.801,3), 'oz-ft'
    print 'IMax:', Imax
    """
    
main()
    
    
    
