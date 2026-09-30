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

See **[RUNNING_THE_SHOW.md](RUNNING_THE_SHOW.md)** for the full show day checklist, rehearsal commands, and troubleshooting.

## Credits

- **Show, choreography, audio, and TouchDesigner project:** Kantwon Rogers
- **Jibo MCP server, TouchDesigner connection, and robot fleet:** Jon Ferguson. The MCP and JiboMCP components in this project build on his examples at [mitmedialab/jibo-mcp-examples](https://github.com/mitmedialab/jibo-mcp-examples/tree/main/touchdesigner).
- **Custom Jibo animations** (`3-kisses`, `big-bow-01`, `looking-around-base-muttering-01`, `missjibo-screen-crack-01`): Fardad
