# ============================================================
# BUILD: /jibo_show/display  -- FINAL consolidated version
# Big screen: cue log + webcam + curtains, Non-Commercial-safe (1280x720)
#
# Run from Textport:
#   exec(open(r'C:/Users/kroge/Dropbox/Documents/Postdoc/Fun/Jibo Performance/MissJiba/build_display.py').read())
#
# After a successful build: SAVE THE PROJECT (Ctrl+S).
# The network persists in the .toe -- no rebuild needed on fresh open.
# ============================================================

MEDIA_DIR = 'C:/Users/kroge/Dropbox/Documents/Postdoc/Fun/Jibo Performance/MissJiba/Curtain Animations'  # <-- EDIT if curtain .movs live elsewhere
CAM_LABEL = 'j5create 360 Meeting Webcam'
CONTROLLER_PATH = '/jibo_show/controller'      # verified: .start() / .stop() live here

# License-capped canvas (TD Non-Commercial = 1280x1280 max).
# If a Commercial/Educational license lands: 1920,1080 and 960 below, rebuild.
RES_W, RES_H = 1280, 720
PANEL_W = 640

# ---------------- helpers ----------------
def setp(o, name, val):
    try:
        setattr(o.par, name, val); return True
    except Exception as e:
        print('  [warn] %s.%s = %r failed: %s' % (o.name, name, val, e)); return False

def setmenu(o, name, tokens):
    for t in tokens:
        try:
            setattr(o.par, name, t)
            if getattr(o.par, name).eval() == t: return True
        except: pass
    print('  [warn] set %s.%s manually (tried %r)' % (o.name, name, tokens)); return False

def setexpr(o, name, expr):
    try:
        p = getattr(o.par, name); p.mode = ParMode.EXPRESSION; p.expr = expr
    except Exception as e:
        print('  [warn] expr %s.%s failed: %s' % (o.name, name, e))

def set_camera(camop, label):
    p = camop.par.device
    labels = list(p.menuLabels)
    if label in labels:
        p.menuIndex = labels.index(label)
        print('  [cam] using: ' + label)
        return True
    print('  [warn] camera %r not found. Available: %r' % (label, labels))
    return False

# ---------------- rebuild container ----------------
show = op('/jibo_show')
old = show.op('display')
if old:
    old.destroy()
d = show.create(containerCOMP, 'display')

def force_res(name, w=RES_W, h=RES_H):
    o = d.op(name)
    setp(o, 'resmult', False)                 # ignore global res multiplier
    setmenu(o, 'outputresolution', ['custom'])
    setp(o, 'resolutionw', w)
    setp(o, 'resolutionh', h)
    setmenu(o, 'outputaspect', ['resolution'])  # aspect = pixels; stops useinput
    print('  [res] %-14s -> %d x %d  aspect:%s' % (name, o.width, o.height,
          o.par.outputaspect.eval()))

# ---------------- background ----------------
bg = d.create(constantTOP, 'bg')
setp(bg,'colorr',0); setp(bg,'colorg',0); setp(bg,'colorb',0)

# ---------------- live cue log ----------------
log = d.create(textDAT, 'show_log'); log.text = ''

def make_log_text(name, fontsize):
    t = d.create(textTOP, name)
    setexpr(t,'text',"op('show_log').text")
    setp(t,'fontsizex',fontsize)
    setmenu(t,'alignx',['left']); setmenu(t,'aligny',['top'])
    setp(t,'wordwrap',False)                  # clip long lines, no ugly folds
    setp(t,'fontcolorr',0.3); setp(t,'fontcolorg',1.0); setp(t,'fontcolorb',0.45)
    setp(t,'bgalpha',0)
    setp(t,'fontfile','C:/Windows/Fonts/consola.ttf')
    return t

lt_full  = make_log_text('log_text_full', 24)   # solo view: whole screen
lt_split = make_log_text('log_text_split', 17)  # split view: fits beside cam

# ---------------- webcam ----------------
cam = d.create(videodeviceinTOP, 'cam')
set_camera(cam, CAM_LABEL)
fit = d.create(fitTOP, 'cam_fit')
fit.inputConnectors[0].connect(cam)
setmenu(fit,'fit',['fitoutside','outside','fill'])   # aspect-preserving crop first

# ---------------- split value (0 = log solo, 1 = log left + cam right) ----------------
c1 = d.create(constantCHOP, 'split_target')
setp(c1,'name0','split'); setp(c1,'value0',0)
f1 = d.create(filterCHOP, 'split_smooth')
f1.inputConnectors[0].connect(c1)
setp(f1,'width',0.6)

# ---------------- solo view: full-width log over bg ----------------
o1 = d.create(overTOP, 'over_log')
o1.inputConnectors[0].connect(lt_full); o1.inputConnectors[1].connect(bg)
setmenu(o1,'prefit',['nativeres','native','nativeresolution'])
setp(o1,'tx',0)

# ---------------- split view: deterministic side-by-side ----------------
lay = d.create(layoutTOP, 'split_layout')
lay.inputConnectors[0].connect(lt_split)
lay.inputConnectors[1].connect(fit)
setmenu(lay,'align',['horizlr'])

cx = d.create(crossTOP, 'split_cross')
cx.inputConnectors[0].connect(o1)
cx.inputConnectors[1].connect(lay)
setexpr(cx,'cross',"op('split_smooth')['split']")

# ---------------- curtains ----------------
mo = d.create(moviefileinTOP, 'curtain_open')
setp(mo,'file', MEDIA_DIR + '/curtain_open_hap.mov')
mc = d.create(moviefileinTOP, 'curtain_close')
setp(mc,'file', MEDIA_DIR + '/curtain_close_hap.mov')
for m in (mo, mc):
    setp(m,'play',1); setp(m,'cue',1); setp(m,'cuepoint',0)
    setmenu(m,'textendright',['hold'])        # correct param name; keeps last frame

sw = d.create(switchTOP, 'curtain_switch')
sw.inputConnectors[0].connect(mo); sw.inputConnectors[1].connect(mc)
setp(sw,'index',0)

o3 = d.create(overTOP, 'over_curtain')
o3.inputConnectors[0].connect(sw); o3.inputConnectors[1].connect(cx)

out = d.create(nullTOP, 'OUT')
out.inputConnectors[0].connect(o3)

# ---------------- resolution tripwire: force + report every node ----------------
force_res('bg')
force_res('log_text_full', RES_W, RES_H)
force_res('log_text_split', PANEL_W, RES_H)
force_res('cam_fit', PANEL_W, RES_H)
force_res('split_layout')
force_res('over_log')
force_res('split_cross')
force_res('curtain_open')
force_res('curtain_close')
force_res('curtain_switch')
force_res('over_curtain')
force_res('OUT')

# ---------------- output window ----------------
w = d.create(windowCOMP, 'out_window')
setp(w,'winop','OUT')
setp(w,'borders',False)
setmenu(w,'justifyoffsetto',['specifydisplay','monitor'])
setp(w,'display',1)                            # placement still verified by hand:
setmenu(w,'size',['fill'])                     # open -> click -> Win+Shift+arrow

# ---------------- controller module ----------------
ctl = d.create(textDAT, 'display_ctl')
_CTL = '''BASE = '/jibo_show/display'
CAM_LABEL = '__CAMLABEL__'
CONTROLLER = '__CONTROLLER__'

def _op(name): return op(BASE + '/' + name)

def Log(msg, lines=24):
    dat = _op('show_log')
    txt = dat.text.rstrip('\\n')
    buf = txt.split('\\n') if txt else []
    buf.append(str(msg))
    dat.text = '\\n'.join(buf[-lines:]) + '\\n'

def ClearLog():
    _op('show_log').text = ''

def AssertCamera():
    p = _op('cam').par.device
    labels = list(p.menuLabels)
    if CAM_LABEL in labels:
        p.menuIndex = labels.index(CAM_LABEL)
    else:
        Log('[warn] camera not found: ' + CAM_LABEL)

def Preshow():
    _op('curtain_switch').par.index = 0
    for n in ('curtain_open','curtain_close'):
        m = _op(n); m.par.play = 1; m.par.cue = 1
    _op('split_target').par.value0 = 0
    ClearLog()
    AssertCamera()
    Log('[preshow] curtains closed, standing by')

def OpenCurtain():
    _op('curtain_switch').par.index = 0
    _op('curtain_open').par.cue = 0
    Log('[curtain] opening')

def CloseCurtain():
    _op('curtain_switch').par.index = 1
    _op('curtain_close').par.cue = 1
    run("op('" + BASE + "/curtain_close').par.cue = 0", delayFrames=2)
    Log('[curtain] closing')

def Split(param=1):
    p = str(param).strip().lower()
    on = p not in ('0', 'off', 'false', '')
    _op('split_target').par.value0 = 1 if on else 0
    Log('[display] split view ' + ('ON' if on else 'OFF'))

def Go(delay=5.0, start_after=4.5):
    Preshow()
    Log('[go] curtain opens in %.1fs' % float(delay))
    run("op('" + BASE + "/display_ctl').module.OpenCurtain()",
        delayMilliSeconds=int(float(delay) * 1000))
    run("op('" + CONTROLLER + "').module.start()",
        delayMilliSeconds=int((float(delay) + float(start_after)) * 1000))

def End():
    CloseCurtain()

def Cue(action, param=''):
    a = str(action).strip().lower()
    if a == 'curtain_open':    OpenCurtain()
    elif a == 'curtain_close': CloseCurtain()
    elif a == 'split':         Split(param)
    elif a == 'log':           Log(param)
    else: Log('[display] unknown action: ' + a)
'''
ctl.text = _CTL.replace('__CAMLABEL__', CAM_LABEL).replace('__CONTROLLER__', CONTROLLER_PATH)

print('=== display build complete ===')
print('1) op("/jibo_show/display/out_window").par.winopen.pulse()')
print('   click window -> Win+Shift+arrow to the show screen')
print('2) op("/jibo_show/display/display_ctl").module.Preshow()')
print('3) SAVE THE PROJECT (Ctrl+S)')