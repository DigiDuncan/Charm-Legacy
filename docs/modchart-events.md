# Modchart Events
*Charm* (and specifically, it's gamemode of the same name,) plans on adding "modchart events," events in a `.chart` file that manipulate the highway or notes in some way.

A chart with these events need to be marked as modcharts in some way, due to their oddness. This is so players can avoid modcharts if deisred, or seek them out.

## The Events

### Flip (`highway_flip`)
Flip the highway from the current status, either righty to lefty or vice versa.

### Note Speed (`notespeed <value>`)
Changes the current note speed to `value`.

### Spritesheet Change (`spritesheet <sheetname>`)
Changes the spritesheet (for the notes) to `{chart folder}/{spritesheets}/{sheetname}`.

### Highway Change `(highway <imagename>)`
Changes the highway background to `{chart folder}/{highways}/{imagename}`.

### Chart Change `(chart <chartname>)`
Changes the current chart to `{chartname}.chart`.

