# Running the Show

Everything is run from TouchDesigner by typing commands into the **Textport** (Alt+T). The show is about 7.5 minutes long. The last cue fires at 434 seconds.

## Before show day: the robots

The robot side was set up by Jon Ferguson. Check with him before any new performance.

- **22 Jibos** running the newer software with the MCP server (port 9010). Older home Jibos don't have it.
- **Custom animations** loaded on every robot: `3-kisses`, `big-bow-01`, `looking-around-base-muttering-01`, `missjibo-screen-crack-01` (made by Fardad).
- **Show network.** Each robot needs the address listed in `toe_export/project1__MCP__servers.tsv` (192.168.42.100 to .111 for Miss Jiba and the back row, .201 to .210 for the front row). Miss Jiba must be first in that list.
- On Windows, use IP addresses, not `.local` names. The `.local` names don't connect reliably.

## Stage layout

```
MISS JIBA(0)  1   2   3   4   5   6   7   8   9  10  11    <- back row
                12  13  14  15  16  17  18  19  20  21     <- front row
```

## Show day checklist

**1. Open the show.** Open `missJiba_Original.toe` in TouchDesigner.

**2. Check the media.** The curtain videos are linked by full paths from Kantwon's laptop. If you're on a different computer and the curtains are black, point `/jibo_show/display/curtain_open` and `curtain_close` at the files in `MissJiba/Curtain Animations/`. The audio track path is relative, so it should just work.

**3. Connect to the robots.**
```
op('/project1/JiboMCP/JiboMCPExt').module.Connect()
```
Watch for "Jibo startup complete. 22 Jibos ready." If the number is lower, some robots didn't connect. Check that they're on and on the show network.

**4. Turn off "Hey Jibo" reactions.** This isn't saved in the show file, so run it every time after connecting. Otherwise the robots may react to people talking.
```
op('/project1/JiboMCP/JiboMCPExt').module.Call('set_hey_jibo_mode', mode='disabled')
```

**5. Open the big-screen window.**
```
op('/jibo_show/display/out_window').par.winopen.pulse()
```
Click the window, then press Win+Shift+Arrow to move it to the projector screen. The webcam feed expects a "j5create 360 Meeting Webcam".

**6. Pre-show.** Closes the curtains and clears the log.
```
op('/jibo_show/display/display_ctl').module.Preshow()
```

**7. GO.** Curtains open after 5 seconds, and the show starts 4.5 seconds after that.
```
op('/jibo_show/display/display_ctl').module.Go()
```
The webcam split-screen comes on automatically at 63 seconds, and the curtains close automatically at the end.

**Stop at any time:**
```
op('/jibo_show/controller').module.stop()
```

## Rehearsing a section

Start from any point in the show (in seconds). The robots snap to face the audience first, since the opening setup gets skipped.
```
op('/jibo_show/controller').module.start_at(120)
```
Stop with `stop()` as above.

## Troubleshooting

- **Robots drop out or freeze.** Keep TouchDesigner in focus and don't minimize it. Minimizing or switching windows caused robots to drop during testing.
- **Only some robots respond.** Reconnect (step 3). Check that the addresses in `/project1/MCP/servers` match the robots.
- **Changing the choreography.** Edit the `/jibo_show/cues` table in TouchDesigner. Each row is a time, target, action, and param. Targets like `backup`, `diva`, `odd`, `even`, `left_half`, and `col1` to `col11` are defined in `/jibo_show/dispatcher`.
