"""
JiboMCP.tox Builder for TouchDesigner

Paste this entire script into the Textport (Dialogs > Textport and DATs)
and press Enter. It creates a JiboMCP COMP at /project1/JiboMCP that
references an external MCP.tox (at /project1/MCP by default).

Build MCP.tox first (paste build_mcp_tox.py), then paste this script.

After building, right-click the JiboMCP COMP > Save Component .tox > JiboMCP.tox

Features:
  - Jibo-specific lifecycle: agency mode, attention, position, LED reset
  - Configurable startup/exit behaviors via custom parameters
  - Multi-Jibo broadcast via the MCP component
  - Convenience methods: Speak, LookAt, LedOn, LedOff, TakePhoto, etc.
  - Startup speech, default position, LED ring reset
  - Clean exit: LED off, exit agency mode

Requires: MCP.tox component at the path specified by the Mcpcomp parameter.
"""

# ── Create or reuse the COMP ─────────────────────────────────────────

p = op('/project1')

def _node(parent, op_type, name, x, y):
    existing = parent.op(name)
    if existing: return existing
    n = parent.create(op_type, name)
    n.nodeX = x; n.nodeY = y
    return n

# ── The COMP itself ──────────────────────────────────────────────────

comp = _node(p, baseCOMP, 'JiboMCP', 400, -300)
comp.par.opviewer = True

# ── Custom Parameters ────────────────────────────────────────────────

_existing_pages = [pg.name for pg in comp.customPages]

if 'Jibo' not in _existing_pages:
    _page = comp.appendCustomPage('Jibo')
    _p = _page.appendOP('Mcpcomp', label='MCP Component')[0]; _p.default = '/project1/MCP'; _p.val = '/project1/MCP'
    _p = _page.appendStr('Startupphrase', label='Startup Phrase')[0]; _p.default = 'TouchDesigner Connected.'; _p.val = 'TouchDesigner Connected.'
    _p = _page.appendFloat('Defaultposx', label='Default Pos X')[0]; _p.default = 0.0; _p.val = 0.0
    _p = _page.appendFloat('Defaultposy', label='Default Pos Y')[0]; _p.default = 0.0; _p.val = 0.0
    _p = _page.appendFloat('Defaultposz', label='Default Pos Z')[0]; _p.default = 0.5; _p.val = 0.5

if 'Startup' not in _existing_pages:
    _page = comp.appendCustomPage('Startup')
    _p = _page.appendToggle('Enteragencyonstartup', label='Enter Agency Mode')[0]; _p.default = True; _p.val = True
    _p = _page.appendToggle('Resetattentiononstartup', label='Set Attention OFF')[0]; _p.default = True; _p.val = True
    _p = _page.appendToggle('Resetpositiononstartup', label='Reset Position')[0]; _p.default = True; _p.val = True
    _p = _page.appendToggle('Resetledonstartup', label='LED Ring Off')[0]; _p.default = True; _p.val = True
    _p = _page.appendToggle('Speakonstartup', label='Speak Greeting')[0]; _p.default = True; _p.val = True

if 'Exit' not in _existing_pages:
    _page = comp.appendCustomPage('Exit')
    _p = _page.appendToggle('Resetledonexit', label='LED Ring Off')[0]; _p.default = True; _p.val = True
    _p = _page.appendToggle('Resetpositiononexit', label='Reset Position')[0]; _p.default = True; _p.val = True
    _p = _page.appendToggle('Exitagencyonexit', label='Exit Agency Mode')[0]; _p.default = True; _p.val = True

# ── Layout constants (inside the COMP) ───────────────────────────────
_COL = 200
_ROW = 120

# ══════════════════════════════════════════════════════════════════════
# JiboMCPExt — Jibo-specific module on top of MCP
# ══════════════════════════════════════════════════════════════════════

ext_code = _node(comp, textDAT, 'JiboMCPExt', _COL, 0)
ext_code.text = '''"""
JiboMCP Module for TouchDesigner.

Jibo-specific layer on top of a generic MCP component.
Handles agency mode lifecycle, startup/exit behaviors,
and provides convenience methods for common Jibo actions.

Usage:
    jibo = op(\'/project1/JiboMCP/JiboMCPExt\').module
    jibo.Speak(text=\'Hello!\')
    jibo.LookAt(x=0, y=0.3, z=0.5)
    jibo.LedOn(r=1, g=0, b=0)
    jibo.LedOff()
    jibo.TakePhoto()
    jibo.Call(\'any_tool\', arg=val)
"""

import threading
import time


# ── Module state ──────────────────────────────────────────────────────
_connected = False


def _comp():
    """Get the owning COMP."""
    return me.parent()


def _mcp():
    """Get the MCP module from the referenced MCP component."""
    try:
        comp = _comp()
        mcp_comp = comp.par.Mcpcomp.eval()
        if mcp_comp:
            return mcp_comp.op(\'MCPExt\').module
    except:
        pass
    return None


# ── Lifecycle ─────────────────────────────────────────────────────────

def Connect():
    """Connect MCP, then run Jibo startup sequence."""
    global _connected
    mcp = _mcp()
    if not mcp:
        _log(\'ERROR: MCP component not found. Set the Mcpcomp parameter.\')
        return

    # Connect the MCP layer
    mcp.Connect()

    if mcp.ConnectedCount() == 0:
        _log(\'No servers connected. Check URLs in MCP servers DAT.\')
        _connected = False
        return

    _connected = True
    comp = _comp()

    # Startup sequence (configurable via parameters)
    if comp.par.Enteragencyonstartup.eval():
        _log(\'Entering agency mode...\')
        mcp.Call(\'enter_agency_mode\')

    if comp.par.Resetattentiononstartup.eval():
        _log(\'Setting attention OFF...\')
        mcp.Call(\'set_attention_mode\', mode=\'OFF\')

    if comp.par.Resetpositiononstartup.eval():
        x = comp.par.Defaultposx.eval()
        y = comp.par.Defaultposy.eval()
        z = comp.par.Defaultposz.eval()
        _log(\'Resetting position to ({}, {}, {})...\'.format(x, y, z))
        mcp.Call(\'lookat\', x=x, y=y, z=z)

    if comp.par.Resetledonstartup.eval():
        _log(\'Resetting LED ring...\')
        mcp.Call(\'light_ring_off\')

    if comp.par.Speakonstartup.eval():
        phrase = comp.par.Startupphrase.eval()
        if phrase:
            _log(\'Speaking: {}\'.format(phrase))
            mcp.Call(\'speak\', text=phrase)

    count = mcp.ConnectedCount()
    _log(\'Jibo startup complete. {} {} ready.\'.format(
        count, \'Jibo\' if count == 1 else \'Jibos\'))


def Disconnect():
    """Run Jibo exit sequence, then disconnect MCP."""
    global _connected
    mcp = _mcp()
    if not mcp or not _connected:
        return

    comp = _comp()

    if comp.par.Resetledonexit.eval():
        _log(\'Turning off LED ring...\')
        try:
            mcp.Call(\'light_ring_off\')
        except:
            pass

    if comp.par.Resetpositiononexit.eval():
        x = comp.par.Defaultposx.eval()
        y = comp.par.Defaultposy.eval()
        z = comp.par.Defaultposz.eval()
        _log(\'Resetting position...\')
        try:
            mcp.Call(\'lookat\', x=x, y=y, z=z)
        except:
            pass

    if comp.par.Exitagencyonexit.eval():
        _log(\'Exiting agency mode...\')
        try:
            mcp.Call(\'exit_agency_mode\')
        except:
            pass

    _connected = False
    mcp.Disconnect()
    _log(\'Jibo disconnected.\')


# ── Convenience methods ───────────────────────────────────────────────

def Speak(text=\'\', **kwargs):
    """Make all Jibos speak."""
    return Call(\'speak\', text=text, **kwargs)


def SpeakAsync(text=\'\', callback=None, **kwargs):
    """Speak without blocking the UI."""
    return CallAsync(\'speak\', callback=callback, text=text, **kwargs)


def LookAt(x=0.0, y=0.0, z=0.5, **kwargs):
    """Make all Jibos look at a position."""
    return Call(\'lookat\', x=x, y=y, z=z, **kwargs)


def LookAtAsync(x=0.0, y=0.0, z=0.5, callback=None, **kwargs):
    """LookAt without blocking the UI."""
    return CallAsync(\'lookat\', callback=callback, x=x, y=y, z=z, **kwargs)


def LedOn(r=1.0, g=1.0, b=1.0, **kwargs):
    """Turn on LED ring on all Jibos."""
    return Call(\'light_ring_on\', r=r, g=g, b=b, **kwargs)


def LedOnAsync(r=1.0, g=1.0, b=1.0, callback=None, **kwargs):
    """LED on without blocking."""
    return CallAsync(\'light_ring_on\', callback=callback, r=r, g=g, b=b, **kwargs)


def LedOff(**kwargs):
    """Turn off LED ring on all Jibos."""
    return Call(\'light_ring_off\', **kwargs)


def LedOffAsync(callback=None, **kwargs):
    """LED off without blocking."""
    return CallAsync(\'light_ring_off\', callback=callback, **kwargs)


def DisplayText(text=\'\', color=\'#ffffff\', hold_seconds=5, font_size=100, **kwargs):
    """Display text on all Jibos\' screens."""
    return Call(\'display_text\', text=text, color=color,
                hold_seconds=hold_seconds, font_size=font_size, **kwargs)


def TakePhoto(server_index=0):
    """Take a photo from a specific Jibo (default: first). Returns result dict."""
    mcp = _mcp()
    if not mcp:
        return None
    return mcp.CallTo(server_index, \'lps_get_image\')


def PlayMotion(anim_name=None, category=None, **kwargs):
    """Play an animation on all Jibos."""
    kw = kwargs.copy()
    if anim_name:
        kw[\'anim_name\'] = anim_name
    if category:
        kw[\'category\'] = category
    return Call(\'play_motion\', **kw)


def Stop(**kwargs):
    """Stop TTS and animations on all Jibos."""
    return Call(\'stop\', **kwargs)


# ── Pass-through to MCP ───────────────────────────────────────────────

def Call(tool, **kwargs):
    """Call any tool on all servers (broadcast). Returns list of results."""
    mcp = _mcp()
    if not mcp:
        _log(\'Not connected\')
        return None
    return mcp.Call(tool, **kwargs)


def CallTo(index, tool, **kwargs):
    """Call a tool on a specific server by index."""
    mcp = _mcp()
    if not mcp:
        _log(\'Not connected\')
        return None
    return mcp.CallTo(index, tool, **kwargs)


def CallAsync(tool, callback=None, **kwargs):
    """Call any tool on all servers asynchronously."""
    mcp = _mcp()
    if not mcp:
        _log(\'Not connected\')
        return None
    return mcp.CallAsync(tool, callback=callback, **kwargs)


def Servers():
    """List of MCP connection objects."""
    mcp = _mcp()
    return mcp.Servers() if mcp else []


def Tools():
    """Dict of tool name -> tool definition."""
    mcp = _mcp()
    return mcp.Tools() if mcp else {}


def ConnectedCount():
    """Number of connected Jibos."""
    mcp = _mcp()
    return mcp.ConnectedCount() if mcp else 0


def Help(tool_name=None):
    """Print help for a tool or list all tools."""
    mcp = _mcp()
    if mcp:
        mcp.Help(tool_name)


def Text(result):
    """Extract first text content block from an MCP result."""
    mcp = _mcp()
    if mcp:
        return mcp.Text(result)
    return None


# ── Internal ──────────────────────────────────────────────────────────

def _log(msg):
    """Log to the MCP component\'s log DAT."""
    mcp = _mcp()
    if mcp:
        try:
            mcp._log(\'[Jibo] \' + msg)
        except:
            print(\'[JiboMCP] \' + msg)
    else:
        print(\'[JiboMCP] \' + msg)
'''

# ── Startup Execute DAT ──────────────────────────────────────────────
startup = _node(comp, executeDAT, 'startup', _COL, -_ROW)
startup.par.start = True
startup.par.exit = True
startup.text = '''def onStart():
\tme.parent().op('JiboMCPExt').module.Connect()
\treturn

def onCreate():
\treturn

def onExit():
\ttry:
\t\tme.parent().op('JiboMCPExt').module.Disconnect()
\texcept:
\t\tpass
\treturn

def onFrameStart(frame):
\treturn

def onFrameEnd(frame):
\treturn

def onPlayStateChange(state):
\treturn

def onDeviceChange():
\treturn

def onProjectPreSave():
\treturn

def onProjectPostSave():
\treturn
'''

# ══════════════════════════════════════════════════════════════════════
# Done!
# ══════════════════════════════════════════════════════════════════════

print("")
print("=== JiboMCP.tox Component Built! ===")
print("")
print("Created: /project1/JiboMCP")
print("")
print("Custom parameters (click JiboMCP COMP to see):")
print("  Jibo page:")
print("    Mcpcomp         - Path to MCP component (default: /project1/MCP)")
print("    Startupphrase   - What Jibo says on connect")
print("    Defaultpos X/Y/Z - Forward-facing position")
print("  Startup page:")
print("    Enteragencyonstartup    - Enter agency mode on connect")
print("    Resetattentiononstartup - Set attention OFF on connect")
print("    Resetpositiononstartup  - LookAt default pos on connect")
print("    Resetledonstartup       - LED ring off on connect")
print("    Speakonstartup          - Speak greeting on connect")
print("  Exit page:")
print("    Resetledonexit          - LED ring off on disconnect")
print("    Resetpositiononexit     - LookAt default pos on disconnect")
print("    Exitagencyonexit        - Exit agency mode on disconnect")
print("")
print("API:")
print("  jibo = op('/project1/JiboMCP/JiboMCPExt').module")
print("  jibo.Speak(text='Hello!')")
print("  jibo.LookAt(x=0, y=0.3, z=0.5)")
print("  jibo.LedOn(r=1, g=0, b=0)")
print("  jibo.LedOff()")
print("  jibo.TakePhoto()               # from first Jibo")
print("  jibo.DisplayText(text='Hi!')")
print("  jibo.Call('any_tool', arg=val)  # pass-through")
print("  jibo.Help()                     # list all tools")
print("")
print("Server URLs: edit /project1/MCP/servers (inside the MCP COMP)")
print("")
print("To save as reusable component:")
print("  Right-click JiboMCP COMP > Save Component .tox")
print("")
