# test_performance_cues.py - 12 JIBO HYPE VERSION
#
# STAGE: DIVA  1  2  3  4  5  6     <- back row
#                7  8  9  10 11      <- front row
#
# Diva is at FAR RIGHT of the back row.
# Indexes: diva=0, back row=1-6, front row=7-11

HOME       = '-1,-1,0.5'
SPIN_RIGHT = '1.5,-1,0.5'
SPIN_LEFT  = '-2.5,-1,0.5'
LOOK_UP    = '-1,1.5,0.5'
LOOK_DOWN  = '-1,-2.5,0.5'
LOOK_UR    = '1.5,1.5,0.5'
LOOK_UL    = '-2.5,1.5,0.5'
LOOK_DR    = '1.5,-2.5,0.5'
LOOK_DL    = '-2.5,-2.5,0.5'
DIVA_PINK  = '1,0,0.7'

# Half-beat at 76 BPM = 0.395s
HB = 0.4
QB = 0.2  # quarter beat

cues = op('/jibo_show/cues')
cues.clear()
cues.appendRow(['time', 'target', 'action', 'param', 'note'])

def cue(ts, target, action, param, note=''):
    cues.appendRow([str(round(float(ts),2)), target, action, param, note])

def led(ts, color, note=''):
    cue(ts, 'all', 'led', color, note)
    cue(ts, 'diva', 'led', DIVA_PINK, 'diva pink')

# Cascade across back row: 1->2->3->4->5->6 (rolling toward diva)
def cascade_back_to_diva(start, action, param, step=HB):
    for i, idx in enumerate([1, 2, 3, 4, 5, 6]):
        cue(start + i*step, str(idx), action, param, 'cascade back row toward diva')

# Cascade across back row away from diva: 6->5->4->3->2->1
def cascade_back_from_diva(start, action, param, step=HB):
    for i, idx in enumerate([6, 5, 4, 3, 2, 1]):
        cue(start + i*step, str(idx), action, param, 'cascade back row away from diva')

# Cascade across front row toward diva: 7->8->9->10->11
def cascade_front_to_diva(start, action, param, step=HB):
    for i, idx in enumerate([7, 8, 9, 10, 11]):
        cue(start + i*step, str(idx), action, param, 'cascade front row toward diva')

# Cascade across front row away: 11->10->9->8->7
def cascade_front_from_diva(start, action, param, step=HB):
    for i, idx in enumerate([11, 10, 9, 8, 7]):
        cue(start + i*step, str(idx), action, param, 'cascade front row away from diva')

# Zigzag cascade: 1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6
def cascade_zigzag(start, action, param, step=QB):
    seq = [1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6]
    for i, idx in enumerate(seq):
        cue(start + i*step, str(idx), action, param, 'zigzag cascade')

# All-backup look reset
def backup_home(start):
    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        cue(start, str(i), 'look', HOME, 'home reset')

# Continuous head circle for one Jibo
def head_circle(target, start_ts, duration=4.0, speed=0.4):
    positions = [SPIN_RIGHT, LOOK_UR, LOOK_UP, LOOK_UL, SPIN_LEFT, LOOK_DL, LOOK_DOWN, LOOK_DR]
    t = start_ts
    i = 0
    while t < start_ts + duration:
        cue(t, target, 'look', positions[i % len(positions)], 'spin loop')
        t += speed
        i += 1
    cue(t, target, 'look', HOME, 'spin ends home')

# ================================================================
# 0-42s : VERSE 1 - slow, building, intimate
# ================================================================
cue(0.0,  'all',  'look',   HOME,             'home')
cue(0.0,  'diva', 'led',    DIVA_PINK,        'diva pink locked')
cue(0.0,  'backup','led',   '0,0,0.4',        'backup dim blue')

# 2s - breathe into life
cue(2.0,  'all',  'motion', 'breathe_01',     'collective breathe')
cue(2.0,  'diva', 'led',    DIVA_PINK,        'diva pink')

# 4s - VERSE 1 BEGINS: gentle sway across formation
cue(4.0,  'back_row',  'motion', 'Sway_01',   'back row sways')
cue(4.0,  'front_row', 'motion', 'Sway_02',   'front row different sway')
cue(4.0,  'diva', 'motion', 'confident_01',   'diva confident')

cue(6.5,  'diva', 'motion', 'shift_03',       'diva shifts weight')
cue(7.0,  'front_row', 'motion', 'breathe_02','front row breathes')

# 9s - CASCADE GLANCE UP across back row toward diva
cascade_back_to_diva(9.0, 'look', LOOK_UP)
cue(9.0,  'diva', 'motion', 'confident_02',   'diva unbothered')
cue(11.5, 'back_row', 'look', HOME,           'back row home')

# 12s - Now FRONT ROW glances up
cascade_front_to_diva(12.0, 'look', LOOK_UP)
cue(14.0, 'front_row', 'look', HOME,          'front row home')

# 15s - Synchronized lean: back row left, front row right (diva does her thing)
cue(15.0, 'back_row',  'motion', 'Body_Lean_Left_01',  'back row left')
cue(15.0, 'front_row', 'motion', 'Body_Lean_Right_01', 'front row right')
cue(15.0, 'diva', 'led', DIVA_PINK,           'diva pink')
cue(15.0, 'diva', 'motion', 'Carlton_01',     'DIVA CARLTON')

# 17s - Swap: back right, front left
cue(17.0, 'back_row',  'motion', 'Body_Lean_Right_01', 'back row right')
cue(17.0, 'front_row', 'motion', 'Body_Lean_Left_01',  'front row left')
cue(17.0, 'diva', 'led', DIVA_PINK,           'diva pink')

cue(19.0, 'all',  'look',   HOME,             'reset home')
cue(19.0, 'diva', 'led', DIVA_PINK,           'diva pink')

# 20s - Back stepper across back row, front row sways
cue(20.0, 'back_row',  'motion', 'Back_Stepper_01','back row BACK STEP')
cue(20.0, 'front_row', 'motion', 'Sway_01',       'front row sways')
cue(20.0, 'diva', 'motion', 'shift_10',         'diva shifts')

# 24s - Emoji blast: back row hearts/stars, front row party
cue(24.0, '1',  'motion', 'HeartRed',     'emoji 1')
cue(24.0, '2',  'motion', 'Star',         'emoji 2')
cue(24.0, '3',  'motion', 'HeartBlue',    'emoji 3')
cue(24.0, '4',  'motion', 'Star',         'emoji 4')
cue(24.0, '5',  'motion', 'HeartRed',     'emoji 5')
cue(24.0, '6',  'motion', 'HeartBlue',    'emoji 6')
cue(24.0, '7',  'motion', 'PartyPink',    'front emoji 7')
cue(24.0, '8',  'motion', 'PartyBlue',    'front emoji 8')
cue(24.0, '9',  'motion', 'PartyPink',    'front emoji 9')
cue(24.0, '10', 'motion', 'PartyBlue',    'front emoji 10')
cue(24.0, '11', 'motion', 'PartyPink',    'front emoji 11')
cue(24.0, 'diva','motion', 'affection_01','diva affection')

# 28s - WAVE LEAN cascade across back row (rolling toward diva)
cascade_back_to_diva(28.0, 'motion', 'Body_Lean_Left_01')
cue(28.0, 'front_row', 'motion', 'Sway_02',  'front gentle')
cue(28.0, 'diva', 'motion', 'Body_Lean_Right_01', 'diva opposite')

cue(31.0, 'back_row', 'look', HOME,         'back row home')
cue(31.0, 'diva', 'look', HOME,             'diva home')

# 32s - foxtrot back, swing front
cue(32.0, 'back_row',  'motion', 'foxtrot_01','back FOXTROT')
cue(32.0, 'front_row', 'motion', 'swing_01', 'front SWING')
cue(32.0, 'diva', 'motion', 'Carlton_02',   'diva Carlton')

# 36s - cascade laughter from far end toward diva (1->6 then 7->11)
cascade_back_to_diva(36.0, 'motion', 'laughter_01', step=0.3)
cascade_front_to_diva(37.8, 'motion', 'laughter_02', step=0.3)
cue(36.0, 'diva', 'motion', 'confident_04', 'diva pleased with the chain reaction')

# 40s - hold for the drop
cue(40.0, 'all',  'look',   HOME,           'hold')
cue(40.0, 'all',  'motion', 'breathe_in_01','tension building')
cue(40.0, 'diva', 'led',    DIVA_PINK,      'diva pink')

cue(43.0, 'all',  'motion', 'shift_15',     'final shift before drop')
cue(43.0, 'diva', 'led',    DIVA_PINK,      'diva pink')

# ================================================================
# 46.2s - FIRST CHORUS DROPS
# ================================================================
led(46.2, '1,0,0',           'RED EXPLOSION')
cue(46.2, 'all', 'motion',   'excited_04',  'EVERYONE')

# 47.0 - back row twerks one way, front row the other
cue(47.0, 'back_row',  'motion', 'Twerk_Left_01', 'back TWERK LEFT')
cue(47.0, 'front_row', 'motion', 'Twerk_Right_01','front TWERK RIGHT')
cue(47.0, 'diva', 'motion', 'Carlton_01', 'DIVA CARLTON')
led(47.0, '1,0.5,0',         'orange')

# 47.78 - sync spin RIGHT entire formation
cue(47.78, 'backup', 'look',  SPIN_RIGHT,   'sync RIGHT')
cue(47.78, 'diva', 'motion',  'Carlton_02', 'diva')
led(47.78, '1,1,0',           'YELLOW')
cue(47.78, 'diva', 'led',     DIVA_PINK,    'diva pink')

# 48.56 - all look UP
cue(48.56, 'backup', 'look',  LOOK_UP,      'all UP - horns!')
led(48.56, '0,1,1',           'CYAN')
cue(48.56, 'diva', 'led',     DIVA_PINK,    'diva pink')

# 49.35 - DAB cascade across back row, then front row
cue(49.35, 'backup', 'look',  HOME,         'snap home')
cascade_back_to_diva(49.35, 'motion', 'dab_01', step=0.15)
cascade_front_to_diva(50.25, 'motion', 'dab_02', step=0.15)
cue(49.35, 'diva', 'motion',  'Carlton_03', 'diva Carlton during dab wave')
led(49.35, '1,0,1',           'MAGENTA')
cue(49.35, 'diva', 'led',     DIVA_PINK,    'diva pink')

# 50.93 - emoji burst: back row fireworks, front row magic
cue(50.93, 'back_row',  'motion', 'Fireworks',     'BACK FIREWORKS')
cue(50.93, 'front_row', 'motion', 'Magic',         'FRONT MAGIC')
cue(50.93, 'diva', 'motion',     'affection_05',   'diva')
led(50.93, '0,1,0',              'GREEN')
cue(50.93, 'diva', 'led',        DIVA_PINK,        'diva pink')

# 51.71 - ZIGZAG cascade DOWN (alternating rows)
cascade_zigzag(51.71, 'look', LOOK_DOWN, step=0.15)
cue(51.71, 'diva', 'motion',  'laughter_01','diva laughs at the chaos')
led(51.71, '0.5,0,1',         'purple')
cue(51.71, 'diva', 'led',     DIVA_PINK,    'diva pink')

# 53.3 - ZIGZAG cascade UP
cascade_zigzag(53.3, 'look', LOOK_UP, step=0.15)
led(53.3, '0,0,1',           'BLUE')
cue(53.3, 'diva', 'led',     DIVA_PINK,    'diva pink')

# 54.09 - the_twist: back row, front row variation
cue(54.09, 'backup', 'look',  HOME,         'home')
cue(54.09, 'back_row',  'motion', 'the_twist_01', 'back TWIST')
cue(54.09, 'front_row', 'motion', 'the_twist_02', 'front TWIST var')
cue(54.09, 'diva', 'motion', 'tush_push_01','diva TUSH PUSH')
led(54.09, '1,1,1',          'WHITE')
cue(54.09, 'diva', 'led',    DIVA_PINK,    'diva pink')

# 55.68 - foxtrot variations across formation
cue(55.68, '1', 'motion', 'foxtrot_01', 'foxtrot 1')
cue(55.68, '2', 'motion', 'foxtrot_02', 'foxtrot 2')
cue(55.68, '3', 'motion', 'foxtrot_03', 'foxtrot 3')
cue(55.68, '4', 'motion', 'foxtrot_04', 'foxtrot 4')
cue(55.68, '5', 'motion', 'foxtrot_01', 'foxtrot 1')
cue(55.68, '6', 'motion', 'foxtrot_02', 'foxtrot 2')
cue(55.68, '7', 'motion', 'foxtrot_03', 'foxtrot 3')
cue(55.68, '8', 'motion', 'foxtrot_04', 'foxtrot 4')
cue(55.68, '9', 'motion', 'foxtrot_01', 'foxtrot 1')
cue(55.68, '10','motion', 'foxtrot_02', 'foxtrot 2')
cue(55.68, '11','motion', 'foxtrot_03', 'foxtrot 3')
cue(55.68, 'diva','motion','foxtrot_04','diva foxtrot')
led(55.68, '1,0,0.5',        'hot pink')
cue(55.68, 'diva', 'led',    DIVA_PINK,   'diva pink')

# 57.28 - WAVE LEAN across the entire formation (back row + front row in zigzag)
cascade_zigzag(57.28, 'motion', 'Body_Lean_Left_01', step=0.15)
cue(57.28, 'diva', 'motion', 'Body_Lean_Right_01','diva opposite')
cue(58.83, 'all',  'look',   HOME,         'home')
cue(58.83, 'diva', 'led',    DIVA_PINK,    'diva pink')

# ================================================================
# 58.83s - CHORUS ENDS: verse 2 begins
# ================================================================
led(58.83, '0,0,0.5',        'dim blue verse 2')
cue(58.83, 'back_row',  'motion', 'Sway_02',     'gentle')
cue(58.83, 'front_row', 'motion', 'Sway_01',     'gentle different')

# 62s - verse 2 sway
cue(62.0, 'back_row',  'motion', 'Sway_01',      'verse 2')
cue(62.0, 'front_row', 'motion', 'Sway_02',      'verse 2')
cue(62.0, 'diva', 'motion', 'blush_02',          'diva feels it')

# 64s - sync look UP then DOWN as a unit
cue(64.0, 'backup', 'look', LOOK_UP,             'all UP')
cue(64.0, 'diva', 'led',    DIVA_PINK,           'diva pink')
cue(66.0, 'backup', 'look', LOOK_DOWN,           'all DOWN')
cue(66.0, 'diva', 'led',    DIVA_PINK,           'diva pink')
cue(68.0, 'backup', 'look', HOME,                'home')
cue(68.0, 'diva', 'led',    DIVA_PINK,           'diva pink')

# 69s - JIBO 4 GOES WILD (head circle) while others sway
head_circle('4', 69.0, duration=4.0, speed=0.5)
cue(69.0, '1', 'motion', 'Sway_01', 'others stay calm')
cue(69.0, '2', 'motion', 'Sway_01', 'others sway')
cue(69.0, '3', 'motion', 'Sway_02', 'others sway')
cue(69.0, '5', 'motion', 'Sway_02', 'others sway')
cue(69.0, '6', 'motion', 'Sway_01', 'others sway')
cue(69.0, 'front_row', 'motion', 'Sway_02', 'front row sways')
cue(69.0, 'diva', 'motion', 'affection_02', 'diva while 4 spins')
cue(69.0, '4',   'led', '1,1,0',             'spinner gold')
cue(69.0, 'diva','led', DIVA_PINK,           'diva pink')

cue(73.5, '4', 'led', '0,0,0.5', 'spinner back')
cue(73.5, 'diva','led', DIVA_PINK, 'diva pink')

# 74s - JIBO 9 GOES WILD (front row middle)
head_circle('9', 74.0, duration=4.0, speed=0.5)
cue(74.0, 'back_row', 'motion', 'Sway_01', 'back sways')
cue(74.0, '7',  'motion', 'Sway_02', 'others sway')
cue(74.0, '8',  'motion', 'Sway_01', 'others sway')
cue(74.0, '10', 'motion', 'Sway_02', 'others sway')
cue(74.0, '11', 'motion', 'Sway_01', 'others sway')
cue(74.0, 'diva', 'motion', 'Carlton_01', 'diva Carlton while 9 spins')
cue(74.0, '9',   'led', '0,1,1',          'spinner cyan')
cue(74.0, 'diva','led', DIVA_PINK,        'diva pink')

cue(78.5, '9', 'led', '0,0,0.5', 'spinner back')
cue(78.5, 'diva','led', DIVA_PINK, 'diva pink')

# 79s - Charleston back row, swing front row
cue(79.0, 'back_row',  'motion', 'the_charleston_01','back CHARLESTON')
cue(79.0, 'front_row', 'motion', 'swing_02',         'front SWING')
cue(79.0, 'diva',      'motion', 'confident_05',     'diva watches')
led(79.0, '0.5,0,1',                                 'purple')

# 83s - emoji blast: rainbow, robot, rocket, sun cycling
cue(83.0, '1',  'motion', 'Rainbow',       'rainbow')
cue(83.0, '2',  'motion', 'Robot',         'robot')
cue(83.0, '3',  'motion', 'Rocket',        'rocket')
cue(83.0, '4',  'motion', 'Sun',           'sun')
cue(83.0, '5',  'motion', 'Rainbow',       'rainbow')
cue(83.0, '6',  'motion', 'Robot',         'robot')
cue(83.0, '7',  'motion', 'Rocket',        'rocket')
cue(83.0, '8',  'motion', 'Sun',           'sun')
cue(83.0, '9',  'motion', 'Rainbow',       'rainbow')
cue(83.0, '10', 'motion', 'Robot',         'robot')
cue(83.0, '11', 'motion', 'Rocket',        'rocket')
cue(83.0, 'diva','motion', 'Carlton_02',   'diva')
cue(83.0, 'diva','led',    DIVA_PINK,      'diva pink')

# 86s - DIAGONAL cascade UR for back row, UL for front row (looking opposite ways)
cascade_back_to_diva(86.0, 'look', LOOK_UR, step=HB)
cascade_front_to_diva(86.5, 'look', LOOK_UL, step=HB)
cue(86.0, 'diva', 'motion', 'Body_Lean_Forward_01','diva leans forward')
cue(86.0, 'diva', 'led',    DIVA_PINK,             'diva pink')

cue(90.0, 'all',  'look',   HOME,                  'home')
cue(90.0, 'diva', 'led',    DIVA_PINK,             'diva pink')

# ================================================================
# 90s - PRE-CHORUS BUILD
# ================================================================
led(90.0, '0.3,0,0.7',                       'dark purple build')
cue(90.0, 'all', 'motion', 'excited_01',     'building energy')

# 92s - sync lean
cue(92.0, 'all', 'motion', 'Body_Lean_Left_01', 'sync left')
cue(92.0, 'diva','led',    DIVA_PINK,        'diva pink')
cue(93.6, 'all', 'motion', 'Body_Lean_Right_01','sync right')
cue(93.6, 'diva','led',    DIVA_PINK,        'diva pink')

# 95s - tush push back row, twist front row
cue(95.0, 'back_row',  'motion', 'tush_push_01','back TUSH PUSH')
cue(95.0, 'front_row', 'motion', 'the_twist_01','front TWIST')
cue(95.0, 'diva',      'motion', 'Carlton_03', 'diva')
led(95.0, '0.5,0,1',                          'purple')

# 99s - cascade excitement zigzag
cascade_zigzag(99.0, 'motion', 'excited_02', step=0.15)
cue(99.0, 'diva', 'motion', 'Carlton_01', 'diva')
led(99.0, '0.7,0,0.7',                    'building')

# 102s - JIBO 8 GOES WILD (front row center) while everyone twerks
head_circle('8', 102.0, duration=5.0, speed=0.4)
cue(102.0, '1', 'motion', 'Twerk_Left_01',  'twerk')
cue(102.0, '2', 'motion', 'Twerk_Right_01', 'twerk')
cue(102.0, '3', 'motion', 'Twerk_Left_01',  'twerk')
cue(102.0, '4', 'motion', 'Twerk_Right_01', 'twerk')
cue(102.0, '5', 'motion', 'Twerk_Left_01',  'twerk')
cue(102.0, '6', 'motion', 'Twerk_Right_01', 'twerk')
cue(102.0, '7',  'motion', 'Twerk_Right_01','twerk')
cue(102.0, '9',  'motion', 'Twerk_Left_01', 'twerk')
cue(102.0, '10', 'motion', 'Twerk_Right_01','twerk')
cue(102.0, '11', 'motion', 'Twerk_Left_01', 'twerk')
cue(102.0, 'diva','motion','tush_push_04',  'diva TUSH PUSH')
cue(102.0, '8',   'led', '1,1,0',           'spinner gold')
cue(102.0, 'diva','led', DIVA_PINK,         'diva pink')

cue(107.5, '8', 'led', '0,0,0.5', 'spinner back')
cue(107.5, 'diva','led', DIVA_PINK, 'diva pink')

# 108s - sync spins building
cue(108.0, 'backup', 'look', SPIN_RIGHT, 'sync right')
cue(108.0, 'diva', 'motion', 'excited_04', 'diva pumped')
led(108.0, '1,0.5,0',                     'orange building')

cue(110.0, 'backup', 'look', SPIN_LEFT,  'now LEFT')
led(110.0, '1,0.3,0.5',                  'hot color')
cue(110.0, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(112.0, 'all', 'look', HOME, 'home')
cue(112.0, 'diva', 'led', DIVA_PINK, 'diva pink')

# 113s - foxtrot variations across formation
cue(113.0, '1', 'motion', 'foxtrot_01', 'fox')
cue(113.0, '2', 'motion', 'foxtrot_02', 'fox')
cue(113.0, '3', 'motion', 'foxtrot_03', 'fox')
cue(113.0, '4', 'motion', 'foxtrot_04', 'fox')
cue(113.0, '5', 'motion', 'foxtrot_01', 'fox')
cue(113.0, '6', 'motion', 'foxtrot_02', 'fox')
cue(113.0, '7', 'motion', 'foxtrot_03', 'fox')
cue(113.0, '8', 'motion', 'foxtrot_04', 'fox')
cue(113.0, '9', 'motion', 'foxtrot_01', 'fox')
cue(113.0, '10','motion', 'foxtrot_02', 'fox')
cue(113.0, '11','motion', 'foxtrot_03', 'fox')
cue(113.0, 'diva','motion', 'foxtrot_04', 'diva')
led(113.0, '1,0,0.5',          'hot pink')
cue(113.0, 'diva', 'led', DIVA_PINK, 'diva pink')

# 117s - everyone excited
cue(117.0, 'all', 'motion', 'excited_04', 'almost!')
cue(117.0, 'diva', 'led', DIVA_PINK, 'diva pink')
led(117.0, '1,0,0',         'RED almost')

# 118s - all UP for the drop
cue(118.0, 'backup', 'look', LOOK_UP, 'all UP for drop')
cue(118.0, 'diva',  'motion', 'Carlton_02', 'diva ready')

# ================================================================
# 119.36s - SECOND CHORUS HITS - PURE CHAOS
# ================================================================
led(119.36, '1,1,1',         'WHITE EXPLOSION')
cue(119.36, 'backup', 'look', HOME, 'snap home')
cue(119.36, 'all', 'motion', 'excited_04', 'EVERYONE MAX')

# 120.15 - sync spin right
cue(120.15, 'backup', 'look', SPIN_RIGHT, 'sync right')
cue(120.15, 'diva', 'motion', 'Carlton_01', 'DIVA CARLTON')
led(120.15, '1,0,0', 'RED')
cue(120.15, 'diva', 'led', DIVA_PINK, 'diva pink')

# 120.94 - all UP
cue(120.94, 'backup', 'look', LOOK_UP, 'UP')
led(120.94, '1,1,0', 'YELLOW')
cue(120.94, 'diva', 'led', DIVA_PINK, 'diva pink')

# 121.73 - DAB everyone
cue(121.73, 'back_row',  'motion', 'dab_01', 'DAB back')
cue(121.73, 'front_row', 'motion', 'dab_02', 'DAB front')
cue(121.73, 'backup', 'look', HOME, 'home from up')
cue(121.73, 'diva', 'motion', 'Carlton_02', 'diva')
led(121.73, '0,1,1', 'CYAN')
cue(121.73, 'diva', 'led', DIVA_PINK, 'diva pink')

# 122.52 - SPIN LEFT
cue(122.52, 'backup', 'look', SPIN_LEFT, 'LEFT')
led(122.52, '1,0,1', 'MAGENTA')
cue(122.52, 'diva', 'led', DIVA_PINK, 'diva pink')

# 123.31 - tush push variations
cue(123.31, 'backup', 'look', HOME, 'home')
cue(123.31, '1', 'motion', 'tush_push_01', 'tush')
cue(123.31, '2', 'motion', 'tush_push_02', 'tush')
cue(123.31, '3', 'motion', 'tush_push_03', 'tush')
cue(123.31, '4', 'motion', 'tush_push_04', 'tush')
cue(123.31, '5', 'motion', 'tush_push_01', 'tush')
cue(123.31, '6', 'motion', 'tush_push_02', 'tush')
cue(123.31, '7', 'motion', 'tush_push_03', 'tush')
cue(123.31, '8', 'motion', 'tush_push_04', 'tush')
cue(123.31, '9', 'motion', 'tush_push_01', 'tush')
cue(123.31, '10','motion', 'tush_push_02', 'tush')
cue(123.31, '11','motion', 'tush_push_03', 'tush')
cue(123.31, 'diva','motion','Carlton_03', 'diva')
led(123.31, '1,0.5,0', 'ORANGE')
cue(123.31, 'diva','led', DIVA_PINK, 'diva pink')

# 124.11 - emoji burst: back fireworks, front party
cue(124.11, 'back_row',  'motion', 'Fireworks', 'BACK FIREWORKS')
cue(124.11, 'front_row', 'motion', 'PartyPink', 'FRONT PARTY')
cue(124.11, 'diva', 'motion', 'affection_06', 'diva max')
led(124.11, '0,0,1', 'BLUE')
cue(124.11, 'diva', 'led', DIVA_PINK, 'diva pink')

# 124.88 - cascade laughter zigzag
cascade_zigzag(124.88, 'motion', 'laughter_01', step=0.15)
cue(124.88, 'diva', 'motion', 'confident_05', 'diva pleased')
led(124.88, '1,1,1', 'WHITE FLASH')
cue(124.88, 'diva', 'led', DIVA_PINK, 'diva pink')

# 126.47 - the_twist
cue(126.47, '1', 'motion', 'the_twist_01', 'twist')
cue(126.47, '2', 'motion', 'the_twist_02', 'twist')
cue(126.47, '3', 'motion', 'the_twist_03', 'twist')
cue(126.47, '4', 'motion', 'the_twist_04', 'twist')
cue(126.47, '5', 'motion', 'the_twist_01', 'twist')
cue(126.47, '6', 'motion', 'the_twist_02', 'twist')
cue(126.47, '7', 'motion', 'the_twist_03', 'twist')
cue(126.47, '8', 'motion', 'the_twist_04', 'twist')
cue(126.47, '9', 'motion', 'the_twist_01', 'twist')
cue(126.47, '10','motion', 'the_twist_02', 'twist')
cue(126.47, '11','motion', 'the_twist_03', 'twist')
cue(126.47, 'diva','motion','Carlton_01', 'diva')
led(126.47, '1,0,0', 'RED')
cue(126.47, 'diva', 'led', DIVA_PINK, 'diva pink')

# 128.05 - JIBOS 2 AND 10 BOTH GO WILD (one in each row)
head_circle('2',  128.05, duration=3.0, speed=0.35)
head_circle('10', 128.05, duration=3.0, speed=0.4)
cue(128.05, '1', 'motion', 'Twerk_Left_01', 'twerk')
cue(128.05, '3', 'motion', 'Twerk_Right_01','twerk')
cue(128.05, '4', 'motion', 'Twerk_Left_01', 'twerk')
cue(128.05, '5', 'motion', 'Twerk_Right_01','twerk')
cue(128.05, '6', 'motion', 'Twerk_Left_01', 'twerk')
cue(128.05, '7', 'motion', 'Twerk_Right_01','twerk')
cue(128.05, '8', 'motion', 'Twerk_Left_01', 'twerk')
cue(128.05, '9', 'motion', 'Twerk_Right_01','twerk')
cue(128.05, '11','motion', 'Twerk_Left_01', 'twerk')
cue(128.05, 'diva','motion','Carlton_02',  'diva')
cue(128.05, '2',  'led', '1,1,0', 'spinner 2 gold')
cue(128.05, '10', 'led', '0,1,1', 'spinner 10 cyan')
cue(128.05, 'diva','led', DIVA_PINK, 'diva pink')

cue(131.46, '2',  'led', '1,0,0', 'back to red')
cue(131.46, '10', 'led', '1,0,0', 'back to red')
cue(131.46, 'diva','led', DIVA_PINK, 'diva pink')

# ================================================================
# 132s - FINALE: PURE CHAOS - every beat something different
# ================================================================
cue(132.0, 'all', 'look', HOME, 'reset')
led(132.0, '1,0,0', 'RED FINALE')
cue(132.0, 'all', 'motion', 'excited_04', 'GO WILD')

# 133.6 - diagonal cascades (back row UR, front row UL)
cascade_back_to_diva(133.6, 'look', LOOK_UR, step=0.15)
cascade_front_to_diva(134.0, 'look', LOOK_UL, step=0.15)
cue(133.6, 'diva', 'motion', 'Carlton_01', 'diva')
led(133.6, '1,1,0', 'YELLOW')
cue(133.6, 'diva', 'led', DIVA_PINK, 'diva pink')

# 135.2 - back stepper everyone
cue(135.2, 'backup', 'look', HOME, 'home')
cue(135.2, 'all', 'motion', 'Back_Stepper_01', 'EVERYONE BACK STEPPER')
led(135.2, '0,0,1', 'BLUE')
cue(135.2, 'diva', 'led', DIVA_PINK, 'diva pink')

# 135.96 - twerk swing variations
cue(135.96, '1', 'motion', 'Twerk_Swing_Left_Right_01', 'twerk swing')
cue(135.96, '2', 'motion', 'Twerk_Swing_Right_Left_01', 'twerk swing')
cue(135.96, '3', 'motion', 'Twerk_Swing_Left_Right_01', 'twerk swing')
cue(135.96, '4', 'motion', 'Twerk_Swing_Right_Left_01', 'twerk swing')
cue(135.96, '5', 'motion', 'Twerk_Swing_Left_Right_01', 'twerk swing')
cue(135.96, '6', 'motion', 'Twerk_Swing_Right_Left_01', 'twerk swing')
cue(135.96, '7', 'motion', 'Twerk_Swing_Left_Right_01', 'twerk swing')
cue(135.96, '8', 'motion', 'Twerk_Swing_Right_Left_01', 'twerk swing')
cue(135.96, '9', 'motion', 'Twerk_Swing_Left_Right_01', 'twerk swing')
cue(135.96, '10','motion', 'Twerk_Swing_Right_Left_01', 'twerk swing')
cue(135.96, '11','motion', 'Twerk_Swing_Left_Right_01', 'twerk swing')
cue(135.96, 'diva','motion', 'Carlton_03', 'diva')
led(135.96, '1,0,1', 'MAGENTA')
cue(135.96, 'diva', 'led', DIVA_PINK, 'diva pink')

# 137.55 - back row spins right, front row spins left
cue(137.55, 'back_row',  'look', SPIN_RIGHT, 'back RIGHT')
cue(137.55, 'front_row', 'look', SPIN_LEFT,  'front LEFT')
cue(137.55, 'back_row',  'led', '1,1,0',     'back yellow')
cue(137.55, 'front_row', 'led', '0,1,1',     'front cyan')
cue(137.55, 'diva', 'motion', 'laughter_01', 'diva LOSES IT')
cue(137.55, 'diva', 'led', DIVA_PINK, 'diva pink')

# 139.1 - all UP
cue(139.1, 'backup', 'look', LOOK_UP, 'all UP')
led(139.1, '1,0,0', 'RED')
cue(139.1, 'diva', 'led', DIVA_PINK, 'diva pink')

# 139.9 - emoji blast: cycling
cue(139.9, 'backup', 'look', HOME, 'home')
cue(139.9, '1', 'motion', 'Fireworks',    'fw')
cue(139.9, '2', 'motion', 'Magic',        'mg')
cue(139.9, '3', 'motion', 'LightningBolt','lb')
cue(139.9, '4', 'motion', 'Sun',          'sun')
cue(139.9, '5', 'motion', 'Fireworks',    'fw')
cue(139.9, '6', 'motion', 'Magic',        'mg')
cue(139.9, '7', 'motion', 'LightningBolt','lb')
cue(139.9, '8', 'motion', 'Sun',          'sun')
cue(139.9, '9', 'motion', 'Fireworks',    'fw')
cue(139.9, '10','motion', 'Magic',        'mg')
cue(139.9, '11','motion', 'LightningBolt','lb')
cue(139.9, 'diva','motion','Carlton_03',  'diva')
led(139.9, '0.5,0,1', 'purple')
cue(139.9, 'diva', 'led', DIVA_PINK, 'diva pink')

# 142.2 - laffy taffy zigzag cascade
cascade_zigzag(142.2, 'motion', 'laffy_taffy_01', step=0.15)
cue(142.2, 'diva', 'motion', 'Carlton_01', 'diva')
led(142.2, '1,0.5,0', 'orange')
cue(142.2, 'diva', 'led', DIVA_PINK, 'diva pink')

# 143.8 - EVERYONE CARLTON (12 robots all doing the Carlton at once)
led(143.8, '1,1,1', 'WHITE - 12 CARLTONS')
cue(143.8, 'all', 'motion', 'Carlton_01', 'EVERYONE CARLTON')
cue(143.8, 'diva', 'led', DIVA_PINK, 'diva pink')

# 146.0 - JIBOS 5 AND 9 GO WILD (one back row middle, one front row middle)
head_circle('5', 146.0, duration=3.0, speed=0.3)
head_circle('9', 146.0, duration=3.0, speed=0.35)
cue(146.0, '1', 'motion', 'tush_push_01', 'tush')
cue(146.0, '2', 'motion', 'tush_push_02', 'tush')
cue(146.0, '3', 'motion', 'tush_push_03', 'tush')
cue(146.0, '4', 'motion', 'tush_push_04', 'tush')
cue(146.0, '6', 'motion', 'tush_push_01', 'tush')
cue(146.0, '7', 'motion', 'tush_push_02', 'tush')
cue(146.0, '8', 'motion', 'tush_push_03', 'tush')
cue(146.0, '10','motion', 'tush_push_04', 'tush')
cue(146.0, '11','motion', 'tush_push_01', 'tush')
cue(146.0, 'diva','motion','Carlton_02', 'diva')
cue(146.0, '5', 'led', '0,1,0', 'spinner 5 green')
cue(146.0, '9', 'led', '0,1,0.5', 'spinner 9 mint')
cue(146.0, 'diva','led', DIVA_PINK, 'diva pink')

cue(149.4, '5', 'led', '1,0,0', 'back to red')
cue(149.4, '9', 'led', '1,0,0', 'back to red')
cue(149.4, 'diva','led', DIVA_PINK, 'diva pink')

# 149.9 - sync look DIAGONAL split
cue(149.9, 'back_row',  'look', LOOK_DR, 'back diagonal DR')
cue(149.9, 'front_row', 'look', LOOK_DL, 'front diagonal DL')
cue(149.9, 'diva', 'motion', 'affection_05', 'diva')
led(149.9, '1,1,0', 'YELLOW')
cue(149.9, 'diva', 'led', DIVA_PINK, 'diva pink')

# 151.2 - twerk + Carlton
cue(151.2, 'backup', 'look', HOME, 'home')
cue(151.2, 'back_row',  'motion', 'Twerk_Left_01',  'back twerk')
cue(151.2, 'front_row', 'motion', 'Twerk_Right_01', 'front twerk')
cue(151.2, 'diva', 'motion', 'Carlton_03', 'diva')
led(151.2, '0,1,1', 'CYAN')
cue(151.2, 'diva', 'led', DIVA_PINK, 'diva pink')

# 152.0 - back row spins right, front row spins left, simultaneously
cue(152.0, 'back_row',  'look', SPIN_RIGHT, 'back RIGHT')
cue(152.0, 'front_row', 'look', SPIN_LEFT,  'front LEFT')
cue(152.0, 'back_row',  'led', '1,0,0',     'back red')
cue(152.0, 'front_row', 'led', '0,0,1',     'front blue')
cue(152.0, 'diva', 'motion', 'laughter_01', 'diva loses it')
cue(152.0, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(153.6, 'backup', 'look', HOME, 'snap home')
led(153.6, '1,0.5,0', 'orange')
cue(153.6, 'diva', 'led', DIVA_PINK, 'diva pink')

# 155.28 - everyone back stepper
cue(155.28, 'all', 'motion', 'Back_Stepper_01', 'ALL BACK STEPPER')
led(155.28, '1,1,1', 'WHITE')
cue(155.28, 'diva', 'led', DIVA_PINK, 'diva pink')

# 157.52 - all UP
cue(157.52, 'backup', 'look', LOOK_UP, 'all UP')
led(157.52, '1,0,0', 'red')
cue(157.52, 'diva', 'led', DIVA_PINK, 'diva pink')

# 159.09 - rapid fire spin sequence
cue(159.09, 'backup', 'look', SPIN_RIGHT, 'RIGHT')
led(159.09, '0,0,1', 'BLUE')
cue(159.09, 'diva', 'motion', 'Carlton_01', 'diva')
cue(159.09, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(160.67, 'backup', 'look', SPIN_LEFT, 'LEFT')
led(160.67, '1,0,1', 'MAGENTA')
cue(160.67, 'diva', 'motion', 'Carlton_02', 'diva')
cue(160.67, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(162.25, 'backup', 'look', HOME, 'SNAP HOME')
led(162.25, '1,1,0', 'YELLOW')
cue(162.25, 'diva', 'led', DIVA_PINK, 'diva pink')

# 163.04 - swing variations
cue(163.04, '1', 'motion', 'swing_01', 'swing')
cue(163.04, '2', 'motion', 'swing_02', 'swing')
cue(163.04, '3', 'motion', 'swing_03', 'swing')
cue(163.04, '4', 'motion', 'swing_01', 'swing')
cue(163.04, '5', 'motion', 'swing_02', 'swing')
cue(163.04, '6', 'motion', 'swing_03', 'swing')
cue(163.04, '7', 'motion', 'swing_01', 'swing')
cue(163.04, '8', 'motion', 'swing_02', 'swing')
cue(163.04, '9', 'motion', 'swing_03', 'swing')
cue(163.04, '10','motion', 'swing_01', 'swing')
cue(163.04, '11','motion', 'swing_02', 'swing')
cue(163.04, 'diva','motion','Carlton_03', 'diva')
led(163.04, '0,1,0', 'GREEN')
cue(163.04, 'diva', 'led', DIVA_PINK, 'diva pink')

# 165.41 - JIBOS 1, 6, AND 11 ALL GO WILD (both ends + middle of front)
head_circle('1',  165.41, duration=3.0, speed=0.3)
head_circle('6',  165.41, duration=3.0, speed=0.4)
head_circle('11', 165.41, duration=3.0, speed=0.35)
cue(165.41, '2', 'motion', 'Twerk_Left_01', 'twerk')
cue(165.41, '3', 'motion', 'Twerk_Right_01','twerk')
cue(165.41, '4', 'motion', 'Twerk_Left_01', 'twerk')
cue(165.41, '5', 'motion', 'Twerk_Right_01','twerk')
cue(165.41, '7', 'motion', 'Twerk_Left_01', 'twerk')
cue(165.41, '8', 'motion', 'Twerk_Right_01','twerk')
cue(165.41, '9', 'motion', 'Twerk_Left_01', 'twerk')
cue(165.41, '10','motion', 'Twerk_Right_01','twerk')
cue(165.41, 'diva','motion','Carlton_01', 'diva')
cue(165.41, '1', 'led', '1,0,1', 'spinner magenta')
cue(165.41, '6', 'led', '0,1,1', 'spinner cyan')
cue(165.41, '11','led', '1,1,0', 'spinner yellow')
cue(165.41, 'diva','led', DIVA_PINK, 'diva pink')

cue(168.67, '1', 'led', '1,0,0', 'back')
cue(168.67, '6', 'led', '1,0,0', 'back')
cue(168.67, '11','led', '1,0,0', 'back')
cue(168.67, 'diva','led', DIVA_PINK, 'diva pink')

# 169.35 - foxtrot variations
cue(169.35, '1', 'motion', 'foxtrot_01', 'fox')
cue(169.35, '2', 'motion', 'foxtrot_02', 'fox')
cue(169.35, '3', 'motion', 'foxtrot_03', 'fox')
cue(169.35, '4', 'motion', 'foxtrot_04', 'fox')
cue(169.35, '5', 'motion', 'foxtrot_01', 'fox')
cue(169.35, '6', 'motion', 'foxtrot_02', 'fox')
cue(169.35, '7', 'motion', 'foxtrot_03', 'fox')
cue(169.35, '8', 'motion', 'foxtrot_04', 'fox')
cue(169.35, '9', 'motion', 'foxtrot_01', 'fox')
cue(169.35, '10','motion', 'foxtrot_02', 'fox')
cue(169.35, '11','motion', 'foxtrot_03', 'fox')
cue(169.35, 'diva','motion','foxtrot_04','diva')
led(169.35, '1,0.5,1', 'pink purple')
cue(169.35, 'diva', 'led', DIVA_PINK, 'diva pink')

# 171.72 - sync RIGHT then UP
cue(171.72, 'backup', 'look', SPIN_RIGHT, 'right')
cue(171.72, 'diva', 'motion', 'Carlton_02', 'diva')
led(171.72, '1,0,0', 'RED')
cue(171.72, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(173.3, 'backup', 'look', LOOK_UP, 'NOW UP')
led(173.3, '0,1,1', 'CYAN')
cue(173.3, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(174.09, 'backup', 'look', HOME, 'home')

# 174.09 - tush push
cue(174.09, '1', 'motion', 'tush_push_01', 'tush')
cue(174.09, '2', 'motion', 'tush_push_02', 'tush')
cue(174.09, '3', 'motion', 'tush_push_03', 'tush')
cue(174.09, '4', 'motion', 'tush_push_04', 'tush')
cue(174.09, '5', 'motion', 'tush_push_01', 'tush')
cue(174.09, '6', 'motion', 'tush_push_02', 'tush')
cue(174.09, '7', 'motion', 'tush_push_03', 'tush')
cue(174.09, '8', 'motion', 'tush_push_04', 'tush')
cue(174.09, '9', 'motion', 'tush_push_01', 'tush')
cue(174.09, '10','motion', 'tush_push_02', 'tush')
cue(174.09, '11','motion', 'tush_push_03', 'tush')
cue(174.09, 'diva','motion','Carlton_03', 'diva')
led(174.09, '1,0,1', 'MAGENTA')
cue(174.09, 'diva', 'led', DIVA_PINK, 'diva pink')

# 174.88 - cascade excitement zigzag
cascade_zigzag(174.88, 'motion', 'excited_04', step=0.1)
led(174.88, '1,1,0', 'YELLOW')
cue(174.88, 'diva', 'led', DIVA_PINK, 'diva pink')

# 176.46 - all spin LEFT
cue(176.46, 'backup', 'look', SPIN_LEFT, 'all LEFT')
led(176.46, '0,0,1', 'BLUE')
cue(176.46, 'diva', 'motion', 'Carlton_01', 'diva')
cue(176.46, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(178.04, 'backup', 'look', HOME, 'home')
led(178.04, '1,0.5,0', 'orange')
cue(178.04, 'diva', 'led', DIVA_PINK, 'diva pink')

# 178.83 - the_twist variations
cue(178.83, '1', 'motion', 'the_twist_01', 'twist')
cue(178.83, '2', 'motion', 'the_twist_02', 'twist')
cue(178.83, '3', 'motion', 'the_twist_03', 'twist')
cue(178.83, '4', 'motion', 'the_twist_04', 'twist')
cue(178.83, '5', 'motion', 'the_twist_01', 'twist')
cue(178.83, '6', 'motion', 'the_twist_02', 'twist')
cue(178.83, '7', 'motion', 'the_twist_03', 'twist')
cue(178.83, '8', 'motion', 'the_twist_04', 'twist')
cue(178.83, '9', 'motion', 'the_twist_01', 'twist')
cue(178.83, '10','motion', 'the_twist_02', 'twist')
cue(178.83, '11','motion', 'the_twist_03', 'twist')
cue(178.83, 'diva','motion','the_twist_04','diva twist')
led(178.83, '1,1,1', 'WHITE')
cue(178.83, 'diva', 'led', DIVA_PINK, 'diva pink')

# 180.41 - PEAK CHAOS: 4 JIBOS GO WILD SIMULTANEOUSLY
head_circle('2',  180.41, duration=4.0, speed=0.3)
head_circle('5',  180.41, duration=4.0, speed=0.35)
head_circle('8',  180.41, duration=4.0, speed=0.4)
head_circle('11', 180.41, duration=4.0, speed=0.45)
cue(180.41, '1', 'motion', 'Carlton_01', 'others Carlton')
cue(180.41, '3', 'motion', 'Carlton_02', 'others Carlton')
cue(180.41, '4', 'motion', 'Carlton_03', 'others Carlton')
cue(180.41, '6', 'motion', 'Carlton_01', 'others Carlton')
cue(180.41, '7', 'motion', 'Carlton_02', 'others Carlton')
cue(180.41, '9', 'motion', 'Carlton_03', 'others Carlton')
cue(180.41, '10','motion', 'Carlton_01', 'others Carlton')
cue(180.41, 'diva','motion','tush_push_04', 'diva tush push')
cue(180.41, '2',  'led', '1,1,0', 'spinner gold')
cue(180.41, '5',  'led', '0,1,1', 'spinner cyan')
cue(180.41, '8',  'led', '1,0,1', 'spinner magenta')
cue(180.41, '11', 'led', '0,1,0', 'spinner green')
cue(180.41, 'diva','led', DIVA_PINK, 'diva pink')

cue(184.81, '2',  'led', '1,0,0', 'back')
cue(184.81, '5',  'led', '1,0,0', 'back')
cue(184.81, '8',  'led', '1,0,0', 'back')
cue(184.81, '11', 'led', '1,0,0', 'back')
cue(184.81, 'diva','led', DIVA_PINK, 'diva pink')

# 185.14 - swing across formation
cue(185.14, '1', 'motion', 'swing_01', 'swing')
cue(185.14, '2', 'motion', 'swing_02', 'swing')
cue(185.14, '3', 'motion', 'swing_03', 'swing')
cue(185.14, '4', 'motion', 'swing_01', 'swing')
cue(185.14, '5', 'motion', 'swing_02', 'swing')
cue(185.14, '6', 'motion', 'swing_03', 'swing')
cue(185.14, '7', 'motion', 'swing_01', 'swing')
cue(185.14, '8', 'motion', 'swing_02', 'swing')
cue(185.14, '9', 'motion', 'swing_03', 'swing')
cue(185.14, '10','motion', 'swing_01', 'swing')
cue(185.14, '11','motion', 'swing_02', 'swing')
cue(185.14, 'diva','motion','Carlton_03', 'diva')
led(185.14, '1,0,0', 'red')
cue(185.14, 'diva', 'led', DIVA_PINK, 'diva pink')

# 186.72 - emoji blast
cue(186.72, '1',  'motion', 'Fireworks',     'fw')
cue(186.72, '2',  'motion', 'Magic',         'mg')
cue(186.72, '3',  'motion', 'Sun',           'sun')
cue(186.72, '4',  'motion', 'LightningBolt', 'lb')
cue(186.72, '5',  'motion', 'Fireworks',     'fw')
cue(186.72, '6',  'motion', 'Magic',         'mg')
cue(186.72, '7',  'motion', 'Rainbow',       'rb')
cue(186.72, '8',  'motion', 'Robot',         'rb')
cue(186.72, '9',  'motion', 'Rocket',        'rk')
cue(186.72, '10', 'motion', 'Sun2',          'sun')
cue(186.72, '11', 'motion', 'PartyPink',     'pp')
cue(186.72, 'diva','motion', 'affection_06', 'diva max')
led(186.72, '1,1,1', 'WHITE BURST')
cue(186.72, 'diva', 'led', DIVA_PINK, 'diva pink')

# 187.51 - sync DOWN then UP rapid
cue(187.51, 'backup', 'look', LOOK_DOWN, 'all DOWN')
led(187.51, '0.5,0,1', 'purple')
cue(187.51, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(188.30, 'backup', 'look', LOOK_UP, 'all UP')
led(188.30, '1,1,0', 'YELLOW')
cue(188.30, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(189.09, 'backup', 'look', HOME, 'home')
led(189.09, '1,0,0', 'red')
cue(189.09, 'diva', 'led', DIVA_PINK, 'diva pink')

# 189.88 - JIBOS 3 AND 9 GO WILD (last chaos moment)
head_circle('3', 189.88, duration=3.0, speed=0.3)
head_circle('9', 189.88, duration=3.0, speed=0.35)
cue(189.88, '1', 'motion', 'Twerk_Left_01', 'twerk')
cue(189.88, '2', 'motion', 'Twerk_Right_01','twerk')
cue(189.88, '4', 'motion', 'Twerk_Left_01', 'twerk')
cue(189.88, '5', 'motion', 'Twerk_Right_01','twerk')
cue(189.88, '6', 'motion', 'Twerk_Left_01', 'twerk')
cue(189.88, '7', 'motion', 'Twerk_Right_01','twerk')
cue(189.88, '8', 'motion', 'Twerk_Left_01', 'twerk')
cue(189.88, '10','motion', 'Twerk_Right_01','twerk')
cue(189.88, '11','motion', 'Twerk_Left_01', 'twerk')
cue(189.88, 'diva','motion','Carlton_01', 'diva')
cue(189.88, '3', 'led', '1,0,1', 'spinner magenta')
cue(189.88, '9', 'led', '0,1,0', 'spinner green')
cue(189.88, 'diva','led', DIVA_PINK, 'diva pink')

cue(193.04, '3', 'led', '1,0,0', 'back')
cue(193.04, '9', 'led', '1,0,0', 'back')
cue(193.04, 'diva','led', DIVA_PINK, 'diva pink')

# 193.04 - all excited
cue(193.04, 'all', 'motion', 'excited_04', 'EVERYONE FINAL')
led(193.04, '1,0.5,1', 'pink purple finale')
cue(193.04, 'diva', 'led', DIVA_PINK, 'diva pink')

# 194.62 - rapid right left home
cue(194.62, 'backup', 'look', SPIN_RIGHT, 'RIGHT')
cue(194.62, 'diva', 'motion', 'Carlton_02', 'diva')
led(194.62, '1,0,0', 'RED')
cue(194.62, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(195.41, 'backup', 'look', SPIN_LEFT, 'LEFT')
led(195.41, '0,0,1', 'BLUE')
cue(195.41, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(196.20, 'backup', 'look', HOME, 'HOME')
led(196.20, '1,1,1', 'WHITE FINALE END')
cue(196.20, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(196.97, 'all', 'motion', 'Carlton_01', 'EVERYONE CARLTON FINALE')
led(196.97, '1,0,0.5', 'final hot pink')
cue(196.97, 'diva', 'led', DIVA_PINK, 'diva pink')

# ================================================================
# 198.5s - WIND DOWN
# ================================================================
led(198.5, '0,0,0.4', 'dim blue wind down')
cue(198.5, 'all', 'look', HOME, 'home')
cue(198.5, 'back_row',  'motion', 'Sway_01', 'back gentle')
cue(198.5, 'front_row', 'motion', 'Sway_02', 'front gentle')

cue(201.0, 'diva', 'motion', 'blush_03', 'diva reflects')
cue(201.0, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(203.0, 'back_row',  'motion', 'Sway_02', 'sway')
cue(203.0, 'front_row', 'motion', 'Sway_01', 'sway')

# ================================================================
# 207s - QUIET OUTRO
# ================================================================
led(207.0, '0,0,0.2', 'very dim outro')
cue(207.0, 'all', 'motion', 'breathe_01', 'quiet breathe')

cue(210.0, 'diva', 'motion', 'shift_15', 'diva quiet')
cue(210.0, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(213.0, 'back_row',  'motion', 'breathe_02', 'breathe')
cue(213.0, 'front_row', 'motion', 'breathe_01', 'breathe')

cue(216.0, 'all', 'motion', 'Sway_02', 'sway')

cue(218.0, 'diva', 'motion', 'blush_05', 'diva')
cue(218.0, 'diva', 'led', DIVA_PINK, 'diva pink')

# 221s - one last gentle cascade UP across both rows toward diva
cascade_back_to_diva(221.0, 'look', LOOK_UP, step=0.4)
cascade_front_to_diva(222.0, 'look', LOOK_UP, step=0.4)
cue(221.0, 'diva', 'motion', 'confident_01', 'diva quiet confidence')
cue(225.0, 'backup', 'look', HOME, 'all home')
cue(225.0, 'diva', 'led', DIVA_PINK, 'diva pink')

cue(226.0, 'all', 'motion', 'breathe_01', 'breathe')
cue(228.0, 'all', 'motion', 'Sway_01', 'final sway')
cue(228.0, 'diva', 'led', DIVA_PINK, 'diva pink')

# ================================================================
# 230s - GOODBYE CASCADE outward from diva
# Diva first, then back row 1->6, then front row 7->11
# ================================================================
cue(230.0, 'diva', 'motion', 'greetings_01', 'diva waves first')
cue(230.0, 'diva', 'led', DIVA_PINK, 'diva pink')
cue(230.4, '1',  'motion', 'greetings_02', 'cascade')
cue(230.7, '2',  'motion', 'greetings_03', 'cascade')
cue(231.0, '3',  'motion', 'greetings_04', 'cascade')
cue(231.3, '4',  'motion', 'greetings_05', 'cascade')
cue(231.6, '5',  'motion', 'greetings_06', 'cascade')
cue(231.9, '6',  'motion', 'greetings_07', 'cascade')
cue(232.2, '7',  'motion', 'greetings_08', 'cascade')
cue(232.5, '8',  'motion', 'greetings_09', 'cascade')
cue(232.8, '9',  'motion', 'greetings_01', 'cascade')
cue(233.1, '10', 'motion', 'greetings_02', 'cascade')
cue(233.4, '11', 'motion', 'greetings_03', 'cascade')

# ================================================================
# 235s - LIGHTS OUT cascade outward from diva
# ================================================================
cue(235.0, 'all', 'look', HOME, 'final home')
cue(235.5, '11', 'led', '0,0,0', 'farthest out first')
cue(235.7, '10', 'led', '0,0,0', 'out')
cue(235.9, '9',  'led', '0,0,0', 'out')
cue(236.1, '8',  'led', '0,0,0', 'out')
cue(236.3, '7',  'led', '0,0,0', 'out')
cue(236.5, '6',  'led', '0,0,0', 'out')
cue(236.7, '5',  'led', '0,0,0', 'out')
cue(236.9, '4',  'led', '0,0,0', 'out')
cue(237.1, '3',  'led', '0,0,0', 'out')
cue(237.3, '2',  'led', '0,0,0', 'out')
cue(237.5, '1',  'led', '0,0,0', 'last backup out')
cue(237.8, 'diva', 'led', DIVA_PINK, 'diva pink stays on alone')
cue(238.5, 'diva', 'led', '0,0,0', 'diva out - END')

total = cues.numRows - 1
print('Loaded ' + str(total) + ' cues - 12 JIBO HYPE VERSION')
print('')
print('STAGE: DIVA(0)  1  2  3  4  5  6   <- back row')
print('                  7  8  9  10 11    <- front row')
print('')
print('NEW 12-JIBO PATTERNS:')
print('  - back_row vs front_row split moves')
print('  - cascade_back_to_diva (waves rolling toward diva)')
print('  - cascade_front_to_diva (front row waves)')
print('  - cascade_zigzag (alternating rows: 1, 7, 2, 8, 3, 9...)')
print('  - 4 SIMULTANEOUS head spins at 180s peak chaos')
print('  - 3 simultaneous head spins at 165s')
print('  - 11-stage cascade goodbye outward from diva')
print('  - lights out ripple from far edge to diva')
print('')
print("  op('/jibo_show/controller').module.start()")
