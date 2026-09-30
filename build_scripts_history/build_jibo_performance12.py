# build_jibo_performance.py  (v5 - 12 Jibos)
#
# HOW TO USE:
#   1. TouchDesigner > File > New
#   2. File > Save As -> JiboPerformance.toe
#   3. Alt+T to open Textport
#   4. Paste build_mcp_tox.py      -> Enter -> wait for "Built!"
#   5. Paste build_jibo_mcp_tox.py -> Enter -> wait for "Built!"
#   6. Paste THIS script           -> Enter -> wait for "READY TO PERFORM"
#   7. Connect:  op('/project1/JiboMCP/JiboMCPExt').module.Connect()
#   8. Start:    op('/jibo_show/controller').module.start()


# ================================================================
# CONFIGURE
# ================================================================

AUDIO_FILE = 'C:/Users/Kantwon/Documents/JiboPerformance/feeling-good-michael-buble-arrangement.wav'

# STAGE LAYOUT:
#   DIVA  1   2   3   4   5   6        (back row of 6)
#          7   8   9  10  11           (front row of 5, in the gaps)
#
# The diva is index 0. Back row 1-6 = indexes 1-6. Front row 7-11 = indexes 7-11.
# Order URLs in the servers DAT to match: diva first, then back row, then front row.

JIBO_URLS = [
    'http://192.168.41.197:9010/mcp',  # diva  (index 0, far right back)
    'http://192.168.41.213:9010/mcp',  # 1     (back row)
    'http://192.168.41.36:9010/mcp',  # 2     (back row)
    'http://192.168.41.57:9010/mcp',  # 3     (back row)
    'http://192.168.41.54:9010/mcp',  # 4     (back row)
    'http://192.168.41.187:9010/mcp',  # 5     (back row)
    'http://192.168.41.30:9010/mcp',  # 6     (back row)
    'http://192.168.41.209:9010/mcp',  # 7     (front row)
    'http://192.168.41.203:9010/mcp',  # 8     (front row)
    'http://192.168.41.172:9010/mcp',  # 9     (front row)
    'http://192.168.41.239:9010/mcp',  # 10    (front row)
    'http://192.168.41.159:9010/mcp',  # 11    (front row)
]

SONG_LENGTH_SECONDS = 240

DIVA_INDEX = 0  # diva is always index 0

# ================================================================


def safe_set(node, param_name, value):
    par = getattr(node.par, param_name, None)
    if par is None:
        return False
    try:
        par.val = value
        return True
    except Exception:
        return False


def safe_pos(node, x, y):
    try:
        node.nodeX = x
        node.nodeY = y
    except Exception:
        pass


# ---- Wipe any previous build ----
root = op('/')
existing = root.op('jibo_show')
if existing:
    existing.destroy()
    print('Removed previous /jibo_show')

show = root.create(containerCOMP, 'jibo_show')
print('Created /jibo_show')


# ---- Push Jibo URLs into MCP servers DAT ----
try:
    mcp_comp = op('/project1/MCP')
    if mcp_comp:
        servers_dat = mcp_comp.op('servers')
        if servers_dat:
            servers_dat.clear()
            for url in JIBO_URLS:
                servers_dat.appendRow([url])
            print('Set ' + str(len(JIBO_URLS)) + ' Jibo URL slots in MCP servers DAT')
            print('  Edit /project1/MCP/servers with the actual IPs when you have them')
        else:
            print('  (MCP servers DAT not found - set URLs manually)')
    else:
        print('  (MCP component not found - run build_mcp_tox.py first)')
except Exception as e:
    print('  (Could not set Jibo URLs: ' + str(e) + ')')


# ---- Audio ----
audio = show.create(audiofileinCHOP, 'audio_track')
safe_set(audio, 'file', AUDIO_FILE)
safe_set(audio, 'play', 0)
safe_pos(audio, 0, 400)

audio_out = show.create(audiodeviceoutCHOP, 'speakers_out')
audio_out.inputConnectors[0].connect(audio)
safe_pos(audio_out, 250, 400)
print('Created audio_track -> speakers_out')


# ---- Master clock ----
timer = show.create(timerCHOP, 'master_clock')
safe_set(timer, 'length', SONG_LENGTH_SECONDS)
safe_set(timer, 'play', 0)
safe_set(timer, 'cycle', 0)
safe_pos(timer, 0, 200)
print('Created master_clock - REMEMBER: set Outputs > Timer Count to Seconds')


# ---- Cue table (placeholder, replace via test_performance_cues.py) ----
cues = show.create(tableDAT, 'cues')
cues.clear()
cues.appendRow(['time', 'target', 'action', 'param', 'note'])
cues.appendRow(['0.0', 'all',  'look', '-1,-1,0.5', 'home'])
cues.appendRow(['0.0', 'diva', 'led',  '1,0,0.7',   'diva pink'])
cues.appendRow(['2.0', 'all',  'motion', 'breathe_01', 'placeholder'])
safe_pos(cues, 400, 200)
print('Created cues table (placeholder - replace with full choreography)')


# ---- Dispatcher ----
# Plain string with placeholder for DIVA_INDEX (no f-strings)
dispatcher = show.create(textDAT, 'dispatcher')
dispatcher_code = (
    'import threading\n'
    '\n'
    'DIVA_INDEX = ' + str(DIVA_INDEX) + '\n'
    '\n'
    '# STAGE LAYOUT (12 Jibos):\n'
    '#   DIVA(0)  1  2  3  4  5  6        <- back row\n'
    '#               7  8  9  10 11        <- front row\n'
    '#\n'
    '# TARGET options in cue table:\n'
    '#   all                every Jibo (incl diva)\n'
    '#   backup             every Jibo except diva (1-11)\n'
    '#   diva               just the diva\n'
    '#   1..11              specific Jibo\n'
    '#   back_row           1, 2, 3, 4, 5, 6\n'
    '#   front_row          7, 8, 9, 10, 11\n'
    '#   odd                1, 3, 5, 7, 9, 11\n'
    '#   even               2, 4, 6, 8, 10\n'
    '#   left_half          1, 2, 3, 7, 8       (stage left)\n'
    '#   right_half         4, 5, 6, 9, 10, 11  (closer to diva)\n'
    '#   ends               1, 6, 7, 11         (outer corners)\n'
    '#   middle             3, 4, 9             (middle of formation)\n'
    '#   zigzag             1, 8, 3, 10, 5      (alternating rows)\n'
    '#   zigzag2            7, 2, 9, 4, 11, 6   (other zigzag)\n'
    '\n'
    '\n'
    'def resolve_targets(target):\n'
    '    """Turn a target name into a list of 0-based Jibo indexes."""\n'
    '    jibo = op(\'/project1/JiboMCP/JiboMCPExt\').module\n'
    '    total = jibo.ConnectedCount()\n'
    '    if total == 0:\n'
    '        return []\n'
    '    \n'
    '    if target == \'all\':\n'
    '        return list(range(total))\n'
    '    elif target == \'backup\':\n'
    '        return [i for i in range(total) if i != DIVA_INDEX]\n'
    '    elif target == \'diva\':\n'
    '        return [DIVA_INDEX]\n'
    '    elif target == \'back_row\':\n'
    '        return [i for i in [1, 2, 3, 4, 5, 6] if i < total]\n'
    '    elif target == \'front_row\':\n'
    '        return [i for i in [7, 8, 9, 10, 11] if i < total]\n'
    '    elif target == \'odd\':\n'
    '        return [i for i in [1, 3, 5, 7, 9, 11] if i < total]\n'
    '    elif target == \'even\':\n'
    '        return [i for i in [2, 4, 6, 8, 10] if i < total]\n'
    '    elif target == \'left_half\':\n'
    '        return [i for i in [1, 2, 3, 7, 8] if i < total]\n'
    '    elif target == \'right_half\':\n'
    '        return [i for i in [4, 5, 6, 9, 10, 11] if i < total]\n'
    '    elif target == \'ends\':\n'
    '        return [i for i in [1, 6, 7, 11] if i < total]\n'
    '    elif target == \'middle\':\n'
    '        return [i for i in [3, 4, 9] if i < total]\n'
    '    elif target == \'zigzag\':\n'
    '        return [i for i in [1, 8, 3, 10, 5] if i < total]\n'
    '    elif target == \'zigzag2\':\n'
    '        return [i for i in [7, 2, 9, 4, 11, 6] if i < total]\n'
    '    else:\n'
    '        try:\n'
    '            idx = int(target)\n'
    '            if 0 <= idx < total:\n'
    '                return [idx]\n'
    '            return []\n'
    '        except ValueError:\n'
    '            print(\'[CUE] Unknown target: \' + str(target))\n'
    '            return []\n'
    '\n'
    '\n'
    'def send(jibo, indexes, tool, **kwargs):\n'
    '    """Send a command to specific Jibos, always non-blocking."""\n'
    '    total = jibo.ConnectedCount()\n'
    '    if set(indexes) == set(range(total)):\n'
    '        # All Jibos - broadcast\n'
    '        jibo.CallAsync(tool, **kwargs)\n'
    '    else:\n'
    '        # Specific Jibos - CallTo in background threads\n'
    '        mcp = op(\'/project1/MCP/MCPExt\').module\n'
    '        for idx in indexes:\n'
    '            def _call(i=idx):\n'
    '                try:\n'
    '                    mcp.CallTo(i, tool, **kwargs)\n'
    '                except Exception as e:\n'
    '                    print(\'[CUE] CallTo error \' + str(i) + \': \' + str(e))\n'
    '            t = threading.Thread(target=_call)\n'
    '            t.daemon = True\n'
    '            t.start()\n'
    '\n'
    '\n'
    'def fire_cue(target, action, param):\n'
    '    """Send one cue."""\n'
    '    try:\n'
    '        jibo = op(\'/project1/JiboMCP/JiboMCPExt\').module\n'
    '    except Exception as e:\n'
    '        print(\'[CUE ERROR] \' + str(e))\n'
    '        return\n'
    '    indexes = resolve_targets(target)\n'
    '    if not indexes:\n'
    '        return\n'
    '    if action == \'motion\':\n'
    '        send(jibo, indexes, \'play_motion\', name=param)\n'
    '    elif action == \'face\':\n'
    '        send(jibo, indexes, \'display_text\', text=param, hold_seconds=-1)\n'
    '    elif action == \'dismissface\':\n'
    '        send(jibo, indexes, \'dismiss_display\')\n'
    '    elif action == \'sway\':\n'
    '        x = 0.35 if param == \'right\' else -0.35 if param == \'left\' else 0.0\n'
    '        send(jibo, indexes, \'lookat\', x=x, y=0.0, z=0.5)\n'
    '    elif action == \'look\':\n'
    '        try:\n'
    '            x, y, z = [float(v) for v in param.split(\',\')]\n'
    '        except Exception:\n'
    '            x, y, z = 0.0, 0.0, 0.5\n'
    '        send(jibo, indexes, \'lookat\', x=x, y=y, z=z)\n'
    '    elif action == \'led\':\n'
    '        try:\n'
    '            r, g, b = [float(v) for v in param.split(\',\')]\n'
    '        except Exception:\n'
    '            r, g, b = 1.0, 1.0, 1.0\n'
    '        if r == 0 and g == 0 and b == 0:\n'
    '            send(jibo, indexes, \'light_ring_off\')\n'
    '        else:\n'
    '            send(jibo, indexes, \'light_ring_on\', r=r, g=g, b=b)\n'
    '    elif action == \'speak\':\n'
    '        send(jibo, indexes, \'speak\', text=param)\n'
    '    print(\'[CUE] \' + str(target) + \'  \' + str(action) + \'  \' + str(param))\n'
    '\n'
    '\n'
    'def check_cues(current_t, last_t):\n'
    '    """Fire cues in (last_t, current_t]."""\n'
    '    cue_table = op(\'cues\')\n'
    '    for row in range(1, cue_table.numRows):\n'
    '        try:\n'
    '            cue_time = float(cue_table[row, \'time\'].val)\n'
    '        except (ValueError, AttributeError):\n'
    '            continue\n'
    '        if last_t < cue_time <= current_t:\n'
    '            fire_cue(\n'
    '                cue_table[row, \'target\'].val,\n'
    '                cue_table[row, \'action\'].val,\n'
    '                cue_table[row, \'param\'].val,\n'
    '            )\n'
)
dispatcher.text = dispatcher_code
safe_pos(dispatcher, 400, 0)
print('Created dispatcher (12-Jibo aware)')


# ---- Frame executor ----
executor = show.create(executeDAT, 'frame_executor')
safe_set(executor, 'framestart', 1)
executor.text = (
    'def onStart():\n'
    '    parent().store(\'last_t\', -1.0)\n'
    '\n'
    'def onCreate():\n'
    '    parent().store(\'last_t\', -1.0)\n'
    '\n'
    'def onExit():\n'
    '    return\n'
    '\n'
    'def onFrameStart(frame):\n'
    '    timer = op(\'master_clock\')\n'
    '    if timer is None:\n'
    '        return\n'
    '    running = timer[\'running\']\n'
    '    if running is None or running.eval() == 0:\n'
    '        return\n'
    '    current_t = None\n'
    '    chan = timer[\'timer_seconds\']\n'
    '    if chan is not None:\n'
    '        current_t = chan.eval()\n'
    '    if current_t is None:\n'
    '        frac_chan = timer[\'timer_fraction\']\n'
    '        if frac_chan is not None:\n'
    '            length = timer.par.length.eval()\n'
    '            current_t = frac_chan.eval() * length\n'
    '    if current_t is None:\n'
    '        return\n'
    '    last_t = parent().fetch(\'last_t\', -1.0)\n'
    '    if current_t < last_t:\n'
    '        last_t = -1.0\n'
    '    if current_t > last_t:\n'
    '        op(\'dispatcher\').module.check_cues(current_t, last_t)\n'
    '        parent().store(\'last_t\', current_t)\n'
    '\n'
    'def onFrameEnd(frame):\n'
    '    return\n'
    '\n'
    'def onPlayStateChange(state):\n'
    '    return\n'
    '\n'
    'def onDeviceChange():\n'
    '    return\n'
    '\n'
    'def onProjectPreSave():\n'
    '    return\n'
    '\n'
    'def onProjectPostSave():\n'
    '    return\n'
)
safe_pos(executor, 600, 0)
print('Created frame_executor')


# ---- Controller ----
controller = show.create(textDAT, 'controller')
controller.text = (
    'def start():\n'
    '    audio = op(\'audio_track\')\n'
    '    timer = op(\'master_clock\')\n'
    '    audio.par.play = 0\n'
    '    audio.par.cuepoint = 0\n'
    '    audio.par.cuepulse.pulse()\n'
    '    parent().store(\'last_t\', -1.0)\n'
    '    timer.par.initialize.pulse()\n'
    '    timer.par.play = 1\n'
    '    timer.par.start.pulse()\n'
    '    audio.par.play = 1\n'
    '    print(\'>>> SHOW STARTED\')\n'
    '\n'
    '\n'
    'def stop():\n'
    '    op(\'audio_track\').par.play = 0\n'
    '    op(\'audio_track\').par.cuepoint = 0\n'
    '    op(\'audio_track\').par.cuepulse.pulse()\n'
    '    op(\'master_clock\').par.initialize.pulse()\n'
    '    parent().store(\'last_t\', -1.0)\n'
    '    print(\'>>> SHOW STOPPED\')\n'
)
safe_pos(controller, -200, 200)
print('Created controller')


print('')
print('=' * 60)
print('  /jibo_show READY (12-JIBO VERSION)')
print('=' * 60)
print('')
print('STAGE LAYOUT:')
print('  DIVA  1   2   3   4   5   6     <- back row')
print('          7   8   9  10  11        <- front row')
print('')
print('NEXT:')
print('  1. Edit /project1/MCP/servers with actual IPs (in stage order)')
print('  2. master_clock > Outputs tab > set Timer Count to Seconds')
print('  3. Paste test_performance_cues.py to load the choreography')
print('  4. Connect:  op(\'/project1/JiboMCP/JiboMCPExt\').module.Connect()')
print('  5. Start:    op(\'/jibo_show/controller\').module.start()')
