# Miss Jiba: AI Live

A robot stage show starring Miss Jiba, a diva Jibo, backed by a chorus of 21 more Jibos. The show was run live from TouchDesigner, which sent timed commands (motions, head movements, light ring colors) to all 22 robots over the network and drove a big-screen display with curtain animations and a live cue log.

Performed at AI Live at the MIT Museum, July 2026.

## What's in here

| Path | What it is |
|---|---|
| `missJiba_Original.toe` | The TouchDesigner project. This is the actual show file. |
| `toe_export/` | Readable copies of every script and table inside the .toe, so you can read the code without TouchDesigner. |
| `toe_export/jibo_show__cues.tsv` | The full choreography: every timed cue for every robot. |
| `toe_export/jibo_show__dispatcher.txt` | Turns each cue into commands for the right robots. |
| `toe_export/project1__MCP__MCPExt.txt` | Talks to each Jibo over MCP. |
| `toe_export/project1__MCP__servers.tsv` | The network address of each robot. |
| `jiboPerformanceAbleton Project/..._PANNED_LEFT.mp3` | The show's audio track, played by the .toe. Panned left so Miss Jiba's voice seemed to come from her side of the stage. |
| `MissJiba/Curtain Animations/` | Curtain open and close videos for the big screen. |
| `MissJiba/build_display.py` | Builds the big-screen display inside TouchDesigner. |
| `MissJiba/voice_clips/` | Source voice lines and crowd effects that were mixed into the audio track in Ableton. The show doesn't load these directly. |
| `build_scripts_history/` | The scripts that built the first version of the project. The show changed a lot after this, so the .toe and `toe_export/` are the source of truth. |
| `export_toe_contents.py` | Regenerates `toe_export/` from the .toe (instructions inside). |

## Running it

1. Open `missJiba_Original.toe` in TouchDesigner.
2. The curtain videos are linked with full paths from the original computer. If they don't load, point `/jibo_show/display/curtain_open` and `curtain_close` at the files in `MissJiba/Curtain Animations/`.
3. Robots: each Jibo runs an MCP server on port 9010. Update `/project1/MCP/servers` with their addresses (Miss Jiba first), then connect with `op('/project1/JiboMCP/JiboMCPExt').module.Connect()`.
4. Start the show: `op('/jibo_show/display/display_ctl').module.Go()`

Without robots, the .toe still opens, and the audio, display, and cue log all run.
