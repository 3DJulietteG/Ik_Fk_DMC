import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import sys
import math
import pymel.core as pm
import maya.mel as mel


"""
________________________________________________________________________________________________________________________________________


Create a Fk/Ik/Dynamic rigg

by Juliette GUEYDAN


____________________________________________________________________________________________________________________________________
"""

if cmds.window("dynaRigg", exists=True):
    cmds.deleteUI("dynaRigg",window=True) 


#_____________________________________________________________ 

#Auto-rigg IK/FK/Dynamic

def rigg(*args):
    
    name = cmds.textField(textFieldEntry, editable = True, q = True, text=True, w = 249)

#_____________________________________________________________ 
    
#Create Joint Chain

    #Bind
    frst=cmds.ls(sl=True)
    sc=cmds.listRelatives(frst, allDescendents=True)
    sc.reverse()
    jnt = frst + sc
    print(jnt)
    y=len(jnt)
    cmds.select(jnt)
    for x in range (0,y):
        i=x+1
        cmds.rename(jnt[x],'Bind_'+name+'_0%d'%i)

    #FK
    cmds.select("Bind_"+name+'_01')
    base=cmds.ls(sl=True)
    cmds.duplicate(base, n="FK_"+name+'_01', renameChildren=True)
    FKchain=cmds.listRelatives("FK_"+name+'_01', allDescendents=True)
    FKchain.append("FK_"+name+'_01')
    FKchain.reverse()
    y=len(FKchain)
    for x in range (1,y):
        i=x+1
        cmds.rename(FKchain[x],'FK_'+name+'_0%d'%i)
    
    #IK
    cmds.duplicate(base, n="IK_"+name+'_01', renameChildren=True)
    IKchain=cmds.listRelatives("IK_"+name+'_01', allDescendents=True)
    IKchain.append("IK_"+name+'_01')
    IKchain.reverse()
    y=len(IKchain)
    for x in range (1,y):
        i=x+1
        cmds.rename(IKchain[x],'IK_'+name+'_0%d'%i)
 
    #IK_FK to BindChain
    
    cmds.select('IK_'+name+'_0*')
    IKchain = cmds.ls(sl=True, sn=True)
    cmds.select('FK_'+name+'_0*')
    FKchain = cmds.ls(sl=True, sn=True)
    cmds.select('Bind_'+name+'_0*')
    BNDchain = cmds.ls(sl=True, sn=True)
    
    mid= BNDchain[int(len(BNDchain)/2)]
    cmds.circle(r=2, n="Switch_IK_FK_"+name)
    cmds.matchTransform("Switch_IK_FK_"+name,mid)
    cmds.select("Switch_IK_FK_"+name)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    
    cmds.addAttr("Switch_IK_FK_"+name, longName='IK_FK', nn='Switch IK to FK', attributeType='float', minValue=0, maxValue=1 )
    cmds.setAttr("Switch_IK_FK_"+name+'.IK_FK', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'.IK_FK', keyable=True )
    cmds.addAttr("Switch_IK_FK_"+name, longName='_______', attributeType='enum', enumName='DYNAMIC')
    cmds.setAttr("Switch_IK_FK_"+name+'._______', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'._______', keyable=True )
    

    
    for x in range(0,len(BNDchain)):
        BlendTr = cmds.shadingNode('blendColors', asUtility=True, n='BlendCl_'+BNDchain[x]+'_Tr')
        BlendRt = cmds.shadingNode('blendColors', asUtility=True, n='BlendCl_'+BNDchain[x]+'_Rt')
        cmds.connectAttr(IKchain[x]+'.translate', BlendTr+'.color2')
        cmds.connectAttr(FKchain[x]+'.translate', BlendTr+'.color1')        
        cmds.connectAttr(IKchain[x]+'.rotate', BlendRt+'.color2')
        cmds.connectAttr(FKchain[x]+'.rotate', BlendRt+'.color1')
        cmds.connectAttr("Switch_IK_FK_"+name+'.IK_FK', BlendRt+'.blender')
        cmds.connectAttr("Switch_IK_FK_"+name+'.IK_FK', BlendTr+'.blender')
        cmds.connectAttr(BlendRt+'.output', BNDchain[x]+'.rotate')
        cmds.connectAttr(BlendTr+'.output', BNDchain[x]+'.translate')



#_____________________________________________________________        
        
#Rigg Joint Chain
    
#FK
    
    FKchain=cmds.listRelatives("FK_"+name+'_01', allDescendents=True)
    FKchain.append("FK_"+name+'_01')
    cmds.select(FKchain)
    x=0
    y=len(FKchain)
    cmds.select(clear=True)
    for x in range (0, y):
        ctrl=cmds.circle(r=1.5, n="CTRL_"+FKchain[x])
        cmds.matchTransform(ctrl,FKchain[x])
        
    #CTRL
        
    cmds.select("CTRL_FK*")
    shapeList = cmds.ls(sl=True)
    FKctrl = cmds.listRelatives(shapeList, parent=True, fullPath=True)
    x=0
    y=len(FKctrl)
    cmds.select(clear=True)
    for x in range (0, y):
        cmds.createNode('transform',n ='Offset1')
        grp1 = ['Offset1']
        offset1 = cmds.ls(sl=True)
        cmds.matchTransform(offset1, FKctrl[x])
        cmds.parent(FKctrl[x], grp1)
        cmds.rename('Offset1', FKctrl[x]+'_Offset')
   
    #Offset
    
    cmds.select("CTRL_FK*_Offset")
    FKoffset = cmds.ls(sl=True)
    cmds.delete(FKoffset[-1])
    cmds.select("CTRL_FK*_Offset")
    FKoffset = cmds.ls(sl=True)
    cmds.select("CTRL_FK*")
    lst = cmds.ls(sl=True)
    shapeList= [s for s in lst if "_Offset" not in s]
    lst = cmds.listRelatives(shapeList, parent=True, fullPath=False)
    FKctrl=[s for s in lst if "_Offset" not in s]
    cmds.select(FKctrl)
    y=len(FKoffset)
    for x in range (1, y):
        a=x-1
        cmds.parent(FKoffset[x], FKctrl[a])
    cmds.createNode('transform',n ='CTRL_FK_'+name)
    cmds.parent(FKoffset[0],'CTRL_FK_'+name)
    FKchain.reverse()
    FKchain.pop()
    
    #ParentFK#
    for x in range (0, len(FKchain)):
        cmds.parentConstraint(FKctrl[x], FKchain[x], mo=True, st=["x","y","z"])



#________________________________________________________________________
    
#IK

    #Create IK Spline
    
    cmds.select("IK_"+name+"*")
    IKchain= cmds.ls(sl=True)
    print(IKchain)
    ikh, effector, curve = cmds.ikHandle(n="Ik_"+name, sj=IKchain[0], ee=IKchain[-1], sol='ikSplineSolver', ccv=True, roc=False, simplifyCurve=False, pcv=False)
    effector = cmds.rename(effector, 'eff_Ik_'+name)
    curve = cmds.rename(curve, 'crv_Ik_'+name)
    cmds.duplicate(curve, n='crv_base_DMC_'+name)
    startjnt= IKchain[0]
    endjnt= IKchain[-1]
    midjnt= IKchain[int(len(IKchain)/2)]

    startjnt = cmds.duplicate(startjnt, n="Jnt_"+name+"_Root", po=True)

    endjnt = cmds.duplicate(endjnt, n="Jnt_"+name+"_Tip", po=True)

    midjnt = cmds.duplicate(midjnt, n="Jnt_"+name+"_Mid", po=True)


    Jnt= startjnt+endjnt+midjnt

    for i in Jnt:
        parent = cmds.listRelatives(i, p=True)

        if parent :
            cmds.parent(i, world=True)
        else :
            print (i+"is already parented to world")

    cmds.skinCluster(startjnt, midjnt, endjnt, 'crv_Ik_'+name)

    cmds.select(endjnt, startjnt, midjnt)
    Jnt=cmds.ls(sl=True)

    for x in range(0,3):
        cmds.circle(r=1.5, n="CTRL_"+Jnt[x])
        cmds.matchTransform("CTRL_"+Jnt[x],Jnt[x])
        cmds.createNode('transform',n ="CTRL_"+Jnt[x]+"_Offset")
        cmds.matchTransform("CTRL_"+Jnt[x]+"_Offset","CTRL_"+Jnt[x])
        cmds.parent("CTRL_"+Jnt[x],"CTRL_"+Jnt[x]+"_Offset")
        cmds.parentConstraint("CTRL_"+Jnt[x], Jnt[x], mo=True)
            
    cmds.connectAttr("CTRL_"+Jnt[0]+'.rotateX', "Ik_"+name+'.twist')

    #Stretch_Squash

    cmds.select('crv_Ik_'+name)
    Crv='crv_Ik_'+name

    # Creation Nodes#

    cmds.addAttr("CTRL_"+Jnt[0], longName='_______', attributeType='enum', enumName='____')
    cmds.setAttr("CTRL_"+Jnt[0]+'._______', channelBox=True )
    cmds.setAttr("CTRL_"+Jnt[0]+'._______', keyable=True )
    cmds.addAttr("CTRL_"+Jnt[0], longName='Stretch_Squash', attributeType='bool')
    cmds.setAttr("CTRL_"+Jnt[0]+'.Stretch_Squash', channelBox=True )
    cmds.setAttr("CTRL_"+Jnt[0]+'.Stretch_Squash', keyable=True)

    CrvInfo = cmds.shadingNode('curveInfo', asUtility=True, n='curveInfo_'+Crv)
    PourcentDiv = cmds.shadingNode('multiplyDivide', asUtility=True, n=name+'_Stretch_Pourcent_Div')

    CondStretchy = cmds.shadingNode('condition', asUtility=True, n='Cond_Stretch_'+name+'_IK')
    
    BlendBND=cmds.shadingNode('blendColors', asUtility=True, n='BlendCl_Stretch_BND_'+name)


    # Connections Nodes#
    cmds.connectAttr(Crv+'.worldSpace[0]', CrvInfo+'.inputCurve')
    cmds.connectAttr(CrvInfo+'.arcLength', PourcentDiv+'.input1X')
    x= cmds.getAttr(CrvInfo+'.arcLength')
    cmds.setAttr(PourcentDiv+'.input2X',x)
    cmds.setAttr(PourcentDiv+'.operation',2)
    cmds.connectAttr(PourcentDiv+'.outputX', CondStretchy+'.colorIfTrueR')
    cmds.setAttr(CondStretchy+'.secondTerm',1)
    cmds.connectAttr("CTRL_"+Jnt[0]+'.Stretch_Squash', CondStretchy+'.firstTerm')


    #Out Connections
    cmds.select('IK_'+name+'_0*')
    IKchain = cmds.ls(sl=True, sn=True)
    cmds.connectAttr(CondStretchy+'.outColorR', BlendBND+'.color2R')
    cmds.connectAttr("Switch_IK_FK_"+name+'.IK_FK', BlendBND+'.blender')
    cmds.setAttr(BlendBND+'.color1R',1)
    for x in range(0,len(IKchain)):
        cmds.connectAttr(CondStretchy+'.outColorR', IKchain[x]+'.scaleX')
        cmds.connectAttr(BlendBND+'.outputR', BNDchain[x]+'.scaleX')


#________________________________________________________________________
    
#DMC
    cmds.select('crv_base_DMC_'+name)
    mel.eval('makeCurvesDynamicHairs 0 0 1')
    cmds.rename("hairSystem1OutputCurves|curve1", 'crv_DMC_'+name)
    cmds.rename("hairSystem1Follicles|follicle1", 'fol_DMC_'+name)
    cmds.rename("hairSystem1", 'hairSys_'+name)
    cmds.rename("nucleus1", 'nucleus_'+name)
    cmds.parent('crv_DMC_'+name, world=True)
    cmds.parent('fol_DMC_'+name, world=True)
    cmds.parent('crv_base_DMC_'+name, world=True)
    cmds.delete("hairSystem1OutputCurves","hairSystem1Follicles")
    
    cmds.setAttr('fol_DMC_'+name+'.pointLock',1)
    cmds.blendShape('crv_DMC_'+name, 'crv_Ik_'+name, n='BShp_DMC_Crv_'+name)
    
    #Create DMC Attribute


    #cmds.parentConstraint("Bind_"+name+"_01", "Switch_IK_FK_"+name, mo=True, sr=["x","y","z"])

    cmds.addAttr("Switch_IK_FK_"+name, longName='Enabled', attributeType='bool')
    cmds.setAttr("Switch_IK_FK_"+name+'.Enabled', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'.Enabled', keyable=True)

    cmds.addAttr("Switch_IK_FK_"+name, longName='Simulation', attributeType='float', minValue=0, maxValue=1)
    cmds.setAttr("Switch_IK_FK_"+name+'.Simulation', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'.Simulation', keyable=True)

    cmds.addAttr("Switch_IK_FK_"+name, longName='Follow_Pose', attributeType='float', minValue=0, maxValue=1)
    cmds.setAttr("Switch_IK_FK_"+name+'.Follow_Pose', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'.Follow_Pose', keyable=True)

    cmds.addAttr("Switch_IK_FK_"+name, longName='Drag', attributeType='float', minValue=0, maxValue=1)
    cmds.setAttr("Switch_IK_FK_"+name+'.Drag', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'.Drag', keyable=True)

    cmds.addAttr("Switch_IK_FK_"+name, longName='Turbulence', attributeType='float', minValue=0, maxValue=1)
    cmds.setAttr("Switch_IK_FK_"+name+'.Turbulence', channelBox=True )
    cmds.setAttr("Switch_IK_FK_"+name+'.Turbulence', keyable=True)

    #Connect_Attribute

    cmds.connectAttr("Switch_IK_FK_"+name+'.Simulation', 'BShp_DMC_Crv_'+name+'.crv_DMC_'+name)
    cmds.connectAttr("Switch_IK_FK_"+name+'.Follow_Pose', 'hairSys_'+name+'.startCurveAttract')
    cmds.connectAttr("Switch_IK_FK_"+name+'.Enabled', 'nucleus_'+name+'.enable')
    cmds.connectAttr("Switch_IK_FK_"+name+'.Drag', 'hairSys_'+name+'.drag')
    cmds.connectAttr("Switch_IK_FK_"+name+'.Turbulence', 'hairSys_'+name+'.turbulenceStrength')


    #Create Cluster handles
    
    degree=cmds.getAttr("crv_base_DMC_"+name+".degree")
    spans=cmds.getAttr("crv_base_DMC_"+name+".spans")
    cvs=degree+spans
    y=cvs-3
    cmds.select(clear=True)
    cmds.select("crv_base_DMC_"+name+"" + '.cv[2:'+str(y)+']', add=True)
    curveCVs=cmds.ls(sl=True, fl=True)
    for x in range(0,len(curveCVs)):
        cmds.cluster(curveCVs[x])

    cmds.select(clear=True)
    cmds.select("crv_base_DMC_"+name + '.cv['+str(y+1)+':'+str(cvs)+']', add=True)
    cmds.cluster()

    cmds.select(clear=True)
    cmds.select("crv_base_DMC_"+name + '.cv[0:1]', add=True)
    cmds.cluster()

   
    cmds.select("cluster*Handle")  
    clst=cmds.ls(sl=True, fl=True)
    cmds.select(clst[-1])
    last=cmds.ls(sl=True, fl=True)
    clst.pop(-1)
    clst.insert(0,last)
    print(clst)

    for x in range (0,len(clst)):
        i=x+1
        cmds.rename(clst[x],'Cl_base_DMC_'+name+'_0%d'%i)

    #Create DMC Ctrl

    cmds.duplicate("CTRL_FK_"+name, n="CTRL_DMC_"+name, renameChildren=True)
    ctrlDMC=cmds.listRelatives("CTRL_DMC_"+name, allDescendents=True)
    ctrlDMC.append("CTRL_DMC_"+name)
    shapelist=[s for s in ctrlDMC if "Shape" not in s]
    shapelist.reverse()
    ctrl=[s for s in shapelist if "Offset" not in s]
    ctrl.remove("CTRL_DMC_"+name)
    print(ctrl)
    y=len(ctrl)
    for x in range (0,y):
        i=x+1
        cmds.rename(ctrl[x],'CTRL_DMC_'+name+'_0%d'%i)

    off=[s for s in shapelist if "Offset" in s]
    y=len(off)
    for x in range (0,y):
        i=x+1
        cmds.rename(off[x],'CTRL_DMC_'+name+'_0%d'%i+"_Offset1")    

    cmds.select('Cl_base*')
    t=cmds.ls(sl=True, fl=True)
    b=[s for s in t if "Cluster" not in s]
    clst=[s for s in b if "Shape" not in s]

    cmds.select("CTRL_DMC_"+name+"_0*")
    l=cmds.ls(sl=True, fl=True)  
    a=[s for s in l if "Offset" not in s]
    ctrl=[s for s in a if "Shape" not in s]
    print(ctrl)
    print(clst)

    for x in range(0,len(ctrl)):
        cmds.parent(clst[x],ctrl[x])
    cmds.parent(clst[-1],ctrl[-1])

    #First Dynamic Configuration

    cmds.setAttr('hairSys_'+name+'.stiffnessScale[0].stiffnessScale_Position',1)   
    cmds.setAttr('hairSys_'+name+'.stiffnessScale[1].stiffnessScale_FloatValue', 0.5)
    cmds.setAttr('hairSys_'+name+'.attractionScale[1].attractionScale_Interp',3)
    cmds.setAttr('hairSys_'+name+'.attractionScale[2].attractionScale_Position',0.5)
    cmds.setAttr('hairSys_'+name+'.attractionScale[2].attractionScale_FloatValue',0.35)
    cmds.setAttr('hairSys_'+name+'.attractionScale[1].attractionScale_FloatValue',0.1)
    cmds.setAttr('hairSys_'+name+'.attractionScale[2].attractionScale_Interp' ,3)


#____________________________________________________________

#Hierarchie

    cmds.createNode('transform',n ='GRP_FK_Joint_'+name)
    cmds.createNode('transform',n ='GRP_IK_Joint_'+name)
    cmds.createNode('transform',n ='GRP_foll_'+name)
    cmds.createNode('transform',n ='GRP_ControleJoint_'+name)
    cmds.createNode('transform',n ='GRP_curves_'+name)
    cmds.createNode('transform',n ='GRP_'+name)
    cmds.createNode('transform',n ='GRP_CTRL_'+name)
    cmds.createNode('transform',n ='GRP_DynamicNodes_'+name)

    cmds.parent("FK_"+name+"_01",'GRP_FK_Joint_'+name)
    cmds.parent("IK_"+name+"_01",'GRP_IK_Joint_'+name)
    cmds.parent("fol_DMC_"+name,'GRP_foll_'+name)
    cmds.parent("crv_DMC_"+name,'GRP_curves_'+name)
    cmds.parent("crv_base_DMC_"+name,'GRP_curves_'+name)
    cmds.parent("crv_Ik_"+name,'GRP_curves_'+name)
    cmds.parent("nucleus_"+name,'GRP_DynamicNodes_'+name)
    cmds.parent("hairSys_"+name,'GRP_DynamicNodes_'+name)
    cmds.parent("Switch_IK_FK_"+name,'GRP_CTRL_'+name)
    cmds.parent("CTRL_DMC_"+name,'GRP_CTRL_'+name)
    cmds.parent("CTRL_FK_"+name,'GRP_CTRL_'+name)

    cmds.select("CTRL_Jnt_"+name+"*_Offset")
    cmds.group(n="CTRL_Ik_"+name)
    cmds.parent("CTRL_Ik_"+name,'GRP_CTRL_'+name)

    cmds.select("Jnt_"+name+"_Tip", "Jnt_"+name+"_Mid", "Jnt_"+name+"_Root")
    sel=cmds.ls(sl=True, fl=True) 
    cmds.parent(sel,'GRP_ControleJoint_'+name)

    cmds.parent("Bind_"+name+"_01",'GRP_'+name)
    cmds.parent("Ik_"+name,'GRP_'+name)
    cmds.parent('GRP_FK_Joint_'+name,'GRP_'+name)
    cmds.parent('GRP_IK_Joint_'+name,'GRP_'+name)


#____________________________________________________________

#Last Connection

    CondVisIKFK = cmds.shadingNode('condition', asUtility=True, n='Cond_Vis_'+name+'_IK_FK')

    CondVisDMC = cmds.shadingNode('condition', asUtility=True, n='Cond_Vis_'+name+'_DMC')
    BlendVisIK = cmds.shadingNode('blendColors', asUtility=True, n='BlendCl_Vis_IK_'+name)
    SetRBlend = cmds.shadingNode('condition', asUtility=True, n='SetR_Vis_IK_'+name)

    cmds.setAttr(CondVisIKFK+'.operation',2)
    cmds.setAttr(CondVisIKFK+'.secondTerm',0.5)
    cmds.connectAttr("Switch_IK_FK_"+name+".IK_FK", CondVisIKFK+'.firstTerm')
    cmds.setAttr(CondVisIKFK+'.colorIfFalseG',0)
    cmds.setAttr(CondVisIKFK+'.colorIfTrueG',1)
    cmds.connectAttr(CondVisIKFK+'.outColorG', 'GRP_FK_Joint_'+name+'.visibility')
    cmds.connectAttr(CondVisIKFK+'.outColorG', 'CTRL_FK_'+name+'.visibility')

    cmds.setAttr(CondVisDMC+'.operation',0)
    cmds.connectAttr("Switch_IK_FK_"+name+".Simulation", CondVisDMC+'.firstTerm')
    cmds.connectAttr(CondVisDMC+'.outColorR', 'CTRL_DMC_'+name+'.visibility')
    cmds.connectAttr(CondVisDMC+'.outColorR', 'crv_DMC_'+name+'.visibility')
    cmds.connectAttr(CondVisDMC+'.outColorR', 'crv_base_DMC_'+name+'.visibility')

    cmds.connectAttr(CondVisDMC+'.outColorR', SetRBlend+'.firstTerm')
    cmds.connectAttr(SetRBlend+'.outColorR', BlendVisIK+'.blender' )
    cmds.setAttr(SetRBlend+'.operation',0)

    cmds.connectAttr(BlendVisIK+'.outputR', 'GRP_IK_Joint_'+name+'.visibility')
    cmds.connectAttr(BlendVisIK+'.outputR', 'CTRL_Ik_'+name+'.visibility')
    cmds.connectAttr(CondVisIKFK+'.outColorR', BlendVisIK+'.color2R')
    cmds.setAttr(BlendVisIK+'.color1R',0)
    
    cmds.setAttr('GRP_ControleJoint_'+name+'.visibility',0)
    cmds.setAttr('GRP_DynamicNodes_'+name+'.visibility',0)
    cmds.setAttr('GRP_foll_'+name+'.visibility',0)



#Help

def help_def (*args):
	cmds.window(title="Help", w = 300, h = 50, minimizeButton=False, maximizeButton=False)
	cmds.frameLayout(l="What to do", marginHeight=10, marginWidth=10)
	cmds.setParent()
	cmds.text(("""-Creer une chaine de joint (qui correspond à ce que tu veux pour ton objet, pas besoin de rename)
-L'orienter (ceux qui n'orientent pas leurs joints vont en enfer)
-Selectionne le premier joint de la chaine et appuie sur le bouton : "Create Rigg"."""), align="left", ww=True)
	cmds.showWindow()

def call (*args):
	cmds.window(title="Help", w = 200, h = 50, minimizeButton=False, maximizeButton=False)
	cmds.frameLayout(l="Contact", marginHeight=10, marginWidth=10)
	cmds.setParent()
	cmds.text(("""GUEYDAN Juliette
gueydanjuliette@orange.fr"""), align="left", ww=True)
	cmds.showWindow()


#window___________________________________________________________________________________________________________
    
	
window= cmds.window("dynaRigg", t="Auto-rigg IK/FK/Dynamic",mnb=False,mxb= False,s=False, menuBar=True ,widthHeight=(250, 200) )
mainw = cmds.formLayout()
nm = cmds.frameLayout( label='Object Name', labelAlign='center')
cmds.menu( label='Help', tearOff=True )
cmds.menuItem( l='What to do',c=help_def)
cmds.menuItem( divider=True )
cmds.menuItem( l='Contact',c=call)
cmds.columnLayout()
textFieldEntry = cmds.textField(w = 250, editable = True,h=30)
cmds.formLayout()
nm = cmds.frameLayout( label='Please select corresponding joint chain', labelAlign='center')
cmds.formLayout()
cmds.button(l='Create Rigg', align='center', c=rigg, w=250, h=100)

cmds.showWindow(window)