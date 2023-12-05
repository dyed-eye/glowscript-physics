from vpython import *
#Web VPython 3.2

# Written by Bruce Sherwood, licensed under Creative Commons 4.0.
# All uses permitted, but you must not claim that you wrote it, and
# you must include this license information in any copies you make.
# For details see http://creativecommons.org/licenses/by/4.0

# Fall 2000; major revision Fall 2002.
# 2013: Created GlowScript JavaScript version, with a quite different stucture.
# March 2015: Converted the JavaScript version to VPython.

scene.title = 'Classical motion in a potential energy well'

scene.width = 800
scene.height = 600
scene.userzoom = False
scene.userspin = False
scene.background = color.white
slopethick = 0.1 # thickness of each slope
slopedeep = 1 # depth of each slope
Lbox = 0.5 # edge length of sliding bead
scene.range = 10
scene.center = vector(10,0,0)
scene.right = 24
scene.left = -4
wkinetic = 0.1
dt = 0.01

bead = box( size=vector(2*slopethick,0.5*slopedeep,slopedeep), color=color.red, visible=False )
boffset = vector(0,0.5*bead.size.y +0.5*slopethick,0)
voffset = vector(0,bead.size.y ,0)
foffset = vector(0,2*bead.size.y ,0)
level = box( color=color.yellow, visible=False, size=vector(1,1,1) )
kinetic = box( color=color.magenta, visible=False )
parrow = arrow( shaftwidth=0.2, color=color.blue, visible=False )
farrow = arrow( shaftwidth=0.2, color=color.green, visible=False )
visualobjects = [bead, level, kinetic, parrow]

instruct = label(pos=vector(10,0,0), color=color.black, opacity=0, box=0,
                 text="Drag from left to right to create a potential energy well.", visible=False)
clicklevel = label(pos=vector(10,-9,0), color=color.black, opacity=0, box=0,
                   text="Click to specify the energy level.", visible=False)

class A: # The only instance of this class is named "args"
    def __init__(self):
        self.lastpos = None
        self.slopes = []

def run(args):
    slopes = args.slopes
    nslope = args.nslope
    xleft = slopes[nslope].xleft
    xright = slopes[nslope].xright
    Fx = -slopes[nslope].axis.y/slopes[nslope].axis.x
    oldx = bead.pos.x
    oldv = bead.p.x/bead.m
    # Need to determine dtleft (when would reach left edge of slope, if at all)
    #   and dtright (when would reach right edge of slope, if at all)
    acc = Fx/bead.m
    dts = [args.deltat]
    if acc == 0: 
        if oldv < 0: 
            dtleft = (xleft-oldx)/oldv
            if dtleft > 0:  
                dts.append(dtleft)
        if oldv > 0:
            dtright = (xright-oldx)/oldv
            if dtright > 0: 
                dts.append(dtright)
    else:
        if oldx != xleft:   # determine time when would reach left end of this slope
            vleftsq =pow( oldv,2)+2*acc*(xleft-oldx)
            if vleftsq >= 0: 
                vleft = sqrt(vleftsq)
                dtleft = (vleft-oldv)/acc
                if dtleft > 0: 
                    dts.append(dtleft)
                dtleft = (-vleft-oldv)/acc
                if dtleft > 0: 
                    dts.append(dtleft)
                
        if oldx != xright:   # determine time when would reach right end of this slope
            vrightsq = oldv**2+2*acc*(xright-oldx)
            if vrightsq >= 0:  
                vright = sqrt(vrightsq)
                dtright = (vright-oldv)/acc
                if dtright > 0: 
                    dts.append(dtright)
                dtright = (-vright-oldv)/acc
                if dtright > 0:  
                    dts.append(dtright)

    dt2 = dts[0]
    for d in dts: 
        if d < dt2: dt2 = d
    
    bead.p = bead.p+vector(Fx,0,0)*dt2
    newv = bead.p.x/bead.m
    bead.pos.x = bead.pos.x+0.5*(oldv+newv)*dt2
    if dt2 < args.deltat:
        if bead.pos.x > slopes[nslope].pos.x:
            bead.pos.x = xright
        else:  
            bead.pos.x = xleft

    args.ypotential = slopes[nslope].pos.y+(slopes[nslope].axis.y/slopes[nslope].axis.x)*(bead.pos.x-slopes[nslope].pos.x)
    kinetic.pos = vector(bead.pos.x,(level.pos.y+args.ypotential)/2,0)
    kinetic.size = vector(wkinetic,abs(level.pos.y-args.ypotential),wkinetic)
    parrow.pos = bead.pos+voffset
    parrow.axis = bead.p
    
    if bead.pos.x >= xright and newv > 0: 
        args.nslope += 1
    elif bead.pos.x <= xleft and newv <= 0:
        args.nslope -= 1
    
    if bead.pos.x >= scene.right or bead.pos.x <= scene.left: return 'end'
    
    if dt2 < args.deltat:
        args.deltat -= dt2
        ret = run(args)
        return ret
    
    return 'continue'


################################/
def makewell_1(args):
    for s in visualobjects:
        s.visible = False
    for s in args.slopes:
        s.visible = False

    args.slopes = []
    args.lastpos = None

def makesegment(args, newpos):
    v = newpos-args.lastpos
    b = box( pos=0.5*(newpos+args.lastpos), size=vector(mag(v),slopethick,slopedeep), axis=v, color=color.green )
    b.xleft = args.lastpos.x
    b.xright = newpos.x
    b.yupper = b.pos.y+abs(0.5*v.y)
    b.ylower = b.pos.y-abs(0.5*v.y)
    args.slopes.append(b)
    args.lastpos = newpos

def makewell_2(args):
    instruct.visible = False
    newpos = scene.mouse.project(normal=vector(0,0,1), d=0 )
    if newpos.x-args.lastpos.x > 0.1:   # get pathologies if slopes extremely short
        makesegment(args, newpos)
    
def makewell_3(args):
    makesegment(args, vector(scene.right,args.slopes[len(args.slopes) -1].yupper,0))

################################

def setlevel_1(args):
    pos = scene.mouse.project( normal=vector(0,0,1), d=0 )
    if pos:
        args.mx = pos.x
        args.my = pos.y
        args.possibles = [] # list of slopes for which the mouse is within upper, lower
        for s in args.slopes:
            if s.ylower < args.my and args.my <= s.yupper and s.ylower != s.yupper:
                args.possibles.append(s)
            
        if len(args.possibles) == 0 or args.my >= args.slopes[0].pos.y:
                return 'continue'  # clicked outside allowable region
        return 'done'
    
    return 'continue'

def setlevel_2(args):
    possibles = args.possibles
    slopes = args.slopes
    minxdist = 100000
    for p in possibles:
        if abs(args.mx-p.pos.x) < minxdist:
            minxdist = abs(args.mx-p.pos.x)
            best = p
        args.lastpos = vector(scene.left,fy,0)

    args.nslope = slopes.index(best)
    
    if best.axis.y < 0:   # falling to the right
        xleft = best.xright-(args.my-best.ylower)*(best.xright-best.xleft)/(best.yupper-best.ylower)
        if best != possibles[len(possibles) -1]:
            p2 = possibles[possibles.index(best)+1]
            xright = p2.xleft+(args.my-p2.ylower)*(p2.xright-p2.xleft)/(p2.yupper-p2.ylower)
        else:
            xright = scene.right
    else:  # rising to the right
        xright = best.xleft+(args.my-best.ylower)*(best.xright-best.xleft)/(best.yupper-best.ylower)
        if best != possibles[0]: 
            p2 = possibles[possibles.index(best)-1]
            xleft = p2.xright-(args.my-p2.ylower)*(p2.xright-p2.xleft)/(p2.yupper-p2.ylower)
        else:
            xleft = 0
    
    level.pos = vector(0.5*(xleft+xright),args.my,0)
    level.size = vector(xright-xleft,slopethick,slopedeep)
    if xright > slopes[len(slopes) -1].xright: 
        args.mx = xleft
    
    if xleft < slopes[0].xleft:  
        args.mx = xright
    
    if abs(args.mx-xleft) < abs(args.mx-xright) or len(possibles) == 1: 
        bead.pos = vector(xleft,args.my,0)+boffset
    else:
        bead.pos = vector(xright,args.my,0)+boffset
    
    bead.m = 1.0
    bead.p = vector(0,0,0)
    parrow.pos = bead.pos+voffset
    parrow.axis = bead.p
    for v in visualobjects:
        v.visible = True

def newwell(w):
    global state, minorstate
    state = 'makewell'
    minorstate = 0

button(text='New well', bind=newwell)

scene.append_to_caption('     ')

def reset(r):
    global state
    state = 'reset' # re-create Morse potential energy well

button(text='Reset', bind=reset)
    
scene.append_to_caption('''

Click "New well" to create a different well.
Click "Reset" to restore to Morse interatomic potential energy well.
Moving red indicator represents separation r.
Blue arrow represents momentum.
Magenta line represents kinetic energy.''')

make_well = False
got_click = False
state = 'reset'
minorstate = 0
alpha = 0.2
fx = fy = 0
args = A()

def Morse(x):
    return 8*( (1 - exp(-alpha*(x-8)))**2 - 1 )

drag = None
def getmouse(evt):
    global drag
    if evt.event == 'mousedown':
        drag = 'down'
    elif evt.event == 'mousemove':
        if drag == 'down':
            drag = 'move'
    elif evt.event == 'mouseup':
        drag = 'up'

scene.bind('mousedown mousemove mouseup', getmouse)

################################
while True:
    rate(200)
    if state == 'reset':
        makewell_1(args)
        fx = 3.6
        fy = Morse(fx)
        args.lastpos = vector(scene.left,fy,0)
        for fx in arange(fx, 26, .1):
            fy = Morse(fx)
            makesegment(args, vector(fx-5,fy,0))
        
        makewell_3(args)
        clicklevel.visible = True
        state = 'getlevel'
        
    elif state == 'makewell':
        if minorstate == 0:
            instruct.visible = True
            makewell_1(args)
            minorstate = 1
        
        if minorstate == 1: 
            if drag == 'down':
                mpos = scene.mouse.project( normal=vector(0,0,1), d=0 )
                args.lastpos = vector(scene.left, mpos.y, 0)
            elif drag == 'move': 
                makewell_2(args)
            elif drag == 'up':
                if len(args.slopes) != 0: minorstate = 2
                else: args.lastpos = None            
        
        if minorstate == 2:
            makewell_3(args)
            make_well = False
            got_click = False
            state = 'getlevel'
            drag = None
            clicklevel.visible = True
        
    elif state == 'getlevel': 
        if not got_click:
            # Wait for mouse click
            if drag != 'up': continue
        
        lev = setlevel_1(args)
        if lev == 'continue':
            got_click = False
            drag = None
            continue
        elif lev == 'done':
            clicklevel.visible = False
        
        setlevel_2(args)
        make_well = False
        state = 'run'
        drag = None
    
    else:
        if drag == 'up':
            got_click = True
            state = 'getlevel'
        
        args.deltat = dt
        ret = run(args)
        if ret == 'end': 
            got_click = False
            state = 'getlevel'
            drag = None
