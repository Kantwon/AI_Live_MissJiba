"""
MCP.tox Builder for TouchDesigner

Paste this entire script into the Textport (Dialogs > Textport and DATs)
and press Enter. It creates a self-contained MCP COMP at /project1/MCP
with TD-native inputs and outputs.

After building, right-click the MCP COMP > Save Component .tox > MCP.tox

Features:
  - Manages N server connections (one URL per line)
  - Auto-discovers tools via MCP tools/list
  - TD-native outputs: status DAT, tools DAT, info CHOP, log DAT
  - Module-based API: Connect/Disconnect/Call/CallAsync
  - Parallel broadcast to all servers
  - Thread-safe output updates via main-thread scheduling

Usage after building:
  mcp = op('/project1/MCP/MCPExt').module
  mcp.Connect()
  mcp.Call('speak', text='Hello!')
  mcp.Help()
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

comp = _node(p, baseCOMP, 'MCP', 0, -300)
comp.par.opviewer = True

# ── Custom Parameters ────────────────────────────────────────────────

# Only add the page if it doesn't exist yet
_existing_pages = [pg.name for pg in comp.customPages]
if 'MCP' not in _existing_pages:
    _page = comp.appendCustomPage('MCP')
    _p = _page.appendOP('Serversdat', label='Servers DAT')[0]; _p.default = ''; _p.val = ''
    _p = _page.appendToggle('Autoconnect', label='Auto Connect')[0]; _p.default = True; _p.val = True
    _p = _page.appendFloat('Timeout', label='Timeout (sec)')[0]; _p.default = 10.0; _p.val = 10.0
    _p = _page.appendInt('Loglines', label='Max Log Lines')[0]; _p.default = 500; _p.val = 500

# ── Layout constants (inside the COMP) ───────────────────────────────
_COL = 200
_ROW = 120

# ══════════════════════════════════════════════════════════════════════
# Internal operators
# ══════════════════════════════════════════════════════════════════════

# ── servers: URL list (user-editable, never overwritten if has content)
servers_dat = _node(comp, textDAT, 'servers', 0, 0)
servers_dat.viewer = True
if not servers_dat.text.strip(): servers_dat.text = "# Enter MCP server URLs, one per line:\n# http://my-server.local:9010/mcp\n"

# ── status: Table DAT output ─────────────────────────────────────────
status_dat = _node(comp, tableDAT, 'status', _COL * 2, 0)
status_dat.clear()
status_dat.appendRow(['url', 'connected', 'tool_count', 'last_error'])
status_dat.viewer = True

# ── tools: Table DAT output ──────────────────────────────────────────
tools_dat = _node(comp, tableDAT, 'tools', _COL * 2, -_ROW)
tools_dat.clear()
tools_dat.appendRow(['name', 'description', 'parameters', 'server'])
tools_dat.viewer = True

# ── info: Constant CHOP output ───────────────────────────────────────
info_chop = _node(comp, constantCHOP, 'info', _COL * 2, -_ROW * 2)
info_chop.par.name0 = 'connected_count'
info_chop.par.value0 = 0
info_chop.par.name1 = 'server_count'
info_chop.par.value1 = 0
info_chop.par.name2 = 'tool_count'
info_chop.par.value2 = 0

# ── log: Text DAT output ─────────────────────────────────────────────
log_dat = _node(comp, textDAT, 'log', _COL * 2, -_ROW * 3)
log_dat.viewer = True

# ── _updater: trigger script for thread-safe output updates ──────────
updater = _node(comp, textDAT, '_updater', _COL * 3, -_ROW * 3)
updater.text = "op('./MCPExt').module._updateOutputs()"

# ── Out operators (promote outputs to COMP exterior) ─────────────────
out_status = _node(comp, outDAT, 'out_status', _COL * 4, 0)
out_status.inputConnectors[0].connect(status_dat.outputConnectors[0])

out_tools = _node(comp, outDAT, 'out_tools', _COL * 4, -_ROW)
out_tools.inputConnectors[0].connect(tools_dat.outputConnectors[0])

out_info = _node(comp, outCHOP, 'out_info', _COL * 4, -_ROW * 2)
out_info.inputConnectors[0].connect(info_chop.outputConnectors[0])

out_log = _node(comp, outDAT, 'out_log', _COL * 4, -_ROW * 3)
out_log.inputConnectors[0].connect(log_dat.outputConnectors[0])

# ══════════════════════════════════════════════════════════════════════
# MCPExt — the core module (loaded via .module access)
# ══════════════════════════════════════════════════════════════════════

ext_code = _node(comp, textDAT, 'MCPExt', _COL, 0)
ext_code.text = '''"""
MCP Client Module for TouchDesigner.

Manages connections to one or more MCP servers (JSON-RPC 2.0 over HTTP).
Auto-discovers tools on connect. Provides parallel broadcast and per-server calls.

Access this module:
    mcp = op('/project1/MCP/MCPExt').module
    mcp.Connect()
    mcp.Call('speak', text='Hello!')
    mcp.Help()
"""

import json
import threading
import time

try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import Request, urlopen, URLError


# ── Module-level state ────────────────────────────────────────────────
_connections = []
_tools = {}
_lock = threading.Lock()


def _comp():
    """Get the owning COMP."""
    return me.parent()


class _MCPConnection:
    """Single MCP server connection with state tracking."""

    def __init__(self, url, timeout=10):
        self.url = url
        self.timeout = timeout
        self.session_id = None
        self.connected = False
        self.tools = {}
        self.tool_count = 0
        self.last_error = \'\'
        self.server_name = \'\'
        self.server_version = \'\'
        self._request_id = 0

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    def _post(self, method, params=None):
        body = json.dumps({
            \'jsonrpc\': \'2.0\',
            \'id\': self._next_id(),
            \'method\': method,
            \'params\': params or {},
        }).encode(\'utf-8\')

        headers = {\'Content-Type\': \'application/json\'}
        if self.session_id:
            headers[\'Mcp-Session-Id\'] = self.session_id

        req = Request(self.url, data=body, headers=headers)
        resp = urlopen(req, timeout=self.timeout)

        sid = resp.headers.get(\'Mcp-Session-Id\')
        if sid:
            self.session_id = sid

        return json.loads(resp.read().decode(\'utf-8\'))

    def connect(self):
        """Initialize session and discover tools."""
        try:
            result = self._post(\'initialize\', {
                \'protocolVersion\': \'2024-11-05\',
                \'capabilities\': {},
                \'clientInfo\': {\'name\': \'touchdesigner-mcp\', \'version\': \'1.0\'},
            })
            info = result.get(\'result\', {}).get(\'serverInfo\', {})
            self.server_name = info.get(\'name\', \'?\')
            self.server_version = info.get(\'version\', \'?\')

            tools_result = self._post(\'tools/list\')
            tool_list = tools_result.get(\'result\', {}).get(\'tools\', [])

            self.tools = {}
            for td in tool_list:
                self.tools[td[\'name\']] = td
            self.tool_count = len(self.tools)
            self.connected = True
            self.last_error = \'\'
            return True
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            return False

    def disconnect(self):
        self.connected = False
        self.session_id = None
        self.tools = {}
        self.tool_count = 0
        self.last_error = \'\'

    def call(self, tool_name, **kwargs):
        """Call an MCP tool. Returns the parsed JSON-RPC result dict."""
        try:
            result = self._post(\'tools/call\', {
                \'name\': tool_name,
                \'arguments\': kwargs,
            })
            if \'error\' in result:
                self.last_error = result[\'error\'].get(\'message\', str(result[\'error\']))
            return result
        except Exception as e:
            self.last_error = str(e)
            return {\'error\': {\'message\': str(e)}}

    def call_async(self, tool_name, callback=None, **kwargs):
        """Call a tool in a background thread."""
        def _run():
            r = self.call(tool_name, **kwargs)
            if callback:
                callback(r)
        t = threading.Thread(target=_run)
        t.daemon = True
        t.start()
        return t

    @staticmethod
    def extract_text(result):
        """Pull the first text content block from an MCP result."""
        try:
            for block in result[\'result\'][\'content\']:
                if block[\'type\'] == \'text\':
                    return block[\'text\']
        except (KeyError, TypeError):
            pass
        return None

    def __repr__(self):
        state = \'connected\' if self.connected else \'disconnected\'
        return \'_MCPConnection({}, {}, {} tools)\'.format(self.url, state, self.tool_count)


# ══════════════════════════════════════════════════════════════════════
# Public API — module-level functions
# ══════════════════════════════════════════════════════════════════════

def Connect():
    """Connect to all servers listed in the servers DAT."""
    global _connections, _tools
    Disconnect()
    urls = _parseServers()
    if not urls:
        _log(\'No server URLs configured. Edit the servers DAT.\')
        return

    connections = []
    comp = _comp()
    timeout = comp.par.Timeout.eval()

    # Connect sequentially on main thread (urlopen fails from bg threads in TD)
    for url in urls:
        conn = _MCPConnection(url, timeout=timeout)
        connections.append(conn)
        _log(\'Connecting to {} ...\'.format(url))
        conn.connect()

    with _lock:
        _connections = connections

    # Merge tool catalogs (first-seen wins for duplicates)
    merged = {}
    ok_count = 0
    for conn in connections:
        if conn.connected:
            ok_count += 1
            _log(\'Connected to {} {} ({} tools)\'.format(
                conn.server_name, conn.server_version, conn.tool_count))
            for name, tdef in conn.tools.items():
                if name not in merged:
                    merged[name] = tdef
        else:
            _log(\'FAILED {}: {}\'.format(conn.url, conn.last_error))

    with _lock:
        _tools = merged

    _log(\'{}/{} servers connected, {} unique tools\'.format(
        ok_count, len(connections), len(merged)))
    _scheduleUpdate()


def Disconnect():
    """Disconnect all servers."""
    global _connections, _tools
    with _lock:
        for conn in _connections:
            conn.disconnect()
        _connections = []
        _tools = {}
    _scheduleUpdate()


def Call(tool, **kwargs):
    """Call a tool on ALL connected servers in parallel. Returns list or single result."""
    with _lock:
        conns = [c for c in _connections if c.connected]
    if not conns:
        _log(\'Call({}): no servers connected\'.format(tool))
        return []

    results = [None] * len(conns)
    threads = []
    for i, conn in enumerate(conns):
        def worker(idx, c, kw):
            results[idx] = c.call(tool, **kw)
        t = threading.Thread(target=worker, args=(i, conn, kwargs))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    results = [r for r in results if r is not None]
    if len(results) == 1:
        return results[0]
    return results


def CallTo(index, tool, **kwargs):
    """Call a tool on a specific server by index. Returns single result."""
    with _lock:
        conns = [c for c in _connections if c.connected]
    if index < 0 or index >= len(conns):
        _log(\'CallTo: index {} out of range (0-{})\'.format(index, len(conns) - 1))
        return {\'error\': {\'message\': \'Server index out of range\'}}
    result = conns[index].call(tool, **kwargs)
    return result


def CallAsync(tool, callback=None, **kwargs):
    """Call a tool on all servers in a background thread. Non-blocking."""
    # Check for connections before spawning thread (avoids TD object access from bg thread)
    with _lock:
        has_conns = any(c.connected for c in _connections)
    if not has_conns:
        return None
    def _run():
        result = Call(tool, **kwargs)
        if callback:
            callback(result)
    t = threading.Thread(target=_run)
    t.daemon = True
    t.start()
    return t


def Servers():
    """List of _MCPConnection objects."""
    with _lock:
        return list(_connections)


def Tools():
    """Dict of tool name -> tool definition (merged from all servers)."""
    with _lock:
        return dict(_tools)


def ConnectedCount():
    """Number of connected servers."""
    with _lock:
        return sum(1 for c in _connections if c.connected)


def Text(result):
    """Extract first text content block from an MCP tool result."""
    return _MCPConnection.extract_text(result)


def Help(tool_name=None):
    """Print help for a tool, or list all tools."""
    tools = Tools()
    if tool_name is None:
        print(\'Available tools ({}):\'.format(len(tools)))
        for name in sorted(tools.keys()):
            desc = tools[name].get(\'description\', \'\')
            if len(desc) > 70:
                desc = desc[:67] + \'...\'
            print(\'  {:30s} {}\'.format(name, desc))
        print()
        print(\'Call:  mcp.Call("tool_name", arg=val)\')
        print(\'Async: mcp.CallAsync("tool_name", callback=fn, arg=val)\')
        return

    if tool_name not in tools:
        print(\'Unknown tool: {}\'.format(tool_name))
        return

    tdef = tools[tool_name]
    print(\'--- {} ---\'.format(tool_name))
    print(tdef.get(\'description\', \'(no description)\'))
    schema = tdef.get(\'inputSchema\', {})
    props = schema.get(\'properties\', {})
    required = set(schema.get(\'required\', []))
    if props:
        print()
        print(\'Parameters:\')
        for pname in sorted(props.keys()):
            pinfo = props[pname]
            ptype = pinfo.get(\'type\', \'any\')
            req = \' (required)\' if pname in required else \'\'
            desc = pinfo.get(\'description\', \'\')
            default = pinfo.get(\'default\')
            if default is not None:
                desc += \' [default: {}]\'.format(default)
            enum = pinfo.get(\'enum\')
            if enum:
                desc += \' [options: {}]\'.format(\', \'.join(str(e) for e in enum))
            print(\'  {:20s} {:10s} {}{}\'.format(pname, ptype, desc, req))


# ── Internal ──────────────────────────────────────────────────────────

def _parseServers():
    """Read servers DAT, return list of URLs (skip blanks and # comments).
    Uses the Serversdat parameter if set, otherwise the internal servers DAT."""
    comp = _comp()
    dat = None
    try:
        ext = comp.par.Serversdat.eval()
        if ext:
            dat = ext
    except:
        pass
    if not dat:
        dat = comp.op(\'servers\')
    if not dat:
        return []
    urls = []
    for line in dat.text.strip().split(\'\\n\'):
        line = line.strip()
        if line and not line.startswith(\'#\'):
            urls.append(line)
    return urls


def _log(msg):
    """Append a timestamped line to the log DAT. Falls back to print() if not on main thread."""
    ts = time.strftime(\'%H:%M:%S\')
    line = \'{} {}\'.format(ts, msg)
    if threading.current_thread() is not threading.main_thread():
        print(\'[MCP] \' + line)
        return
    try:
        log = _comp().op(\'log\')
        if not log:
            return
        if log.text.strip():
            log.text += \'\\n\' + line
        else:
            log.text = line
        # Truncate if too long
        max_lines = _comp().par.Loglines.eval()
        lines = log.text.split(\'\\n\')
        if len(lines) > max_lines:
            log.text = \'\\n\'.join(lines[-max_lines:])
    except:
        print(\'[MCP] \' + line)


def _scheduleUpdate():
    """Schedule a main-thread output update. Only safe from main thread."""
    if threading.current_thread() is not threading.main_thread():
        return
    try:
        _comp().op(\'_updater\').run()
    except:
        pass


def _updateOutputs():
    """Refresh all output operators from current state. Must run on main thread."""
    try:
        comp = _comp()
        with _lock:
            conns = list(_connections)
            tools = dict(_tools)

        # Status table
        status = comp.op(\'status\')
        if status:
            status.clear()
            status.appendRow([\'url\', \'connected\', \'tool_count\', \'last_error\'])
            for c in conns:
                status.appendRow([c.url, int(c.connected), c.tool_count, c.last_error])

        # Tools table
        tools_dat = comp.op(\'tools\')
        if tools_dat:
            tools_dat.clear()
            tools_dat.appendRow([\'name\', \'description\', \'parameters\', \'server\'])
            for c in conns:
                if not c.connected:
                    continue
                for name, tdef in sorted(c.tools.items()):
                    desc = tdef.get(\'description\', \'\')
                    params = json.dumps(tdef.get(\'inputSchema\', {}).get(\'properties\', {}))
                    tools_dat.appendRow([name, desc, params, c.url])

        # Info CHOP
        info = comp.op(\'info\')
        if info:
            info.par.value0 = sum(1 for c in conns if c.connected)
            info.par.value1 = len(conns)
            info.par.value2 = len(tools)
    except Exception as e:
        _log(\'Output update error: {}\'.format(e))
'''

# ── Startup Execute DAT ──────────────────────────────────────────────
startup = _node(comp, executeDAT, 'startup', _COL, -_ROW)
startup.par.start = True
startup.text = '''def onStart():
\tcomp = me.parent()
\tif comp.par.Autoconnect.eval():
\t\tcomp.op('MCPExt').module.Connect()
\treturn

def onCreate():
\treturn

def onExit():
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
print("=== MCP.tox Component Built! ===")
print("")
print("Created: /project1/MCP")
print("")
print("Internal operators:")
print("  servers       - Edit this: one MCP server URL per line")
print("  MCPExt        - MCP client module (the brains)")
print("  status        - Table: URL, connected, tool_count, last_error")
print("  tools         - Table: name, description, parameters, server")
print("  info          - CHOP: connected_count, server_count, tool_count")
print("  log           - Activity log")
print("  startup       - Auto-connects on project load (if Autoconnect is ON)")
print("")
print("Outputs on COMP exterior:")
print("  out_status, out_tools, out_info, out_log")
print("")
print("Usage:")
print("  mcp = op('/project1/MCP/MCPExt').module")
print("  mcp.Connect()                        # connect to all servers")
print("  mcp.Call('tool_name', arg=val)        # broadcast call")
print("  mcp.CallTo(0, 'tool_name', arg=val)   # call specific server")
print("  mcp.CallAsync('tool_name', callback=fn)")
print("  mcp.Help()                            # list all tools")
print("  mcp.Help('tool_name')                 # tool details")
print("  mcp.Servers()                         # connection objects")
print("  mcp.Tools()                           # tool definitions")
print("")
print("To save as reusable component:")
print("  Right-click MCP COMP > Save Component .tox")
print("")
