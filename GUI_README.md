# Xatra Studio GUI

## How to Start / Restart

To start the full application (backend + frontend):
```bash
./start_gui.sh
```

To restart if the page is blank or not responding:
1. Stop the current process (usually `Ctrl+C` in the terminal where you ran the script).
2. If it doesn't stop cleanly, kill any remaining processes:
   ```bash
   pkill -f uvicorn
   pkill -f vite
   ```
3. Run `./start_gui.sh` again.

## TODO

Bugs
- [x] Base map doesn't appear by default---it appears in the Base Layer dropdown and I can select it and it appears, but the map renders with None by default even though I have a Base Layer selected which is odd
- [x] Period field has a bug: it doesn't allow commas, so I cannot actually enter a range. It also doesn't seem to allow minus signs (which is how we enter BC dates---in fact, the example shown should be something like [-320, -180] and the "format" helper should explicitly say "use negative numbers for BC years".), or for the first entry to be 0 (which should be possible since these are years). This applies to all elements.
- [x] Admin and AdminRivers elements have a bug: Error: Map.Admin() got an unexpected keyword argument 'label'.
- [x] I get an Error: object of type 'int' has no len() sometimes ... leave this issue for now, I think fixing the Period field will fix it.
- [x] Start year end year fields for the Time Slider in Global Options are broken again
  - [x] This is still broken, entering "-" leaves it blank.
- [x] Code Editor is broken (shows a blank page)
- [x] In case of any error where the map runs into "Rendering..." "Generating map..." forever, there should be something to let the user stop the generation. Sometimes even reloading the page doesn't work.
  - [x] While the feature has been implemented, it doesn't solve the underlying problem, which is that the server is itself in an error state, so no other operation runs afterward. It should stop the underlying Python process that is in error. 
  - [x] Also in general errors should always break the process, right (I might be talking nonsense, IDK)? Why does the execution not return things to normal upon these errors? 
- [x] In all the forms there should be something to ensure when the contents are cleared, it is treated exactly as it would be exactly as if it were never edited. E.g. when I enter something into the Flag Color Sequence box and then remove it, I get an error while generating the map "Error: name 'parse_color_sequence' is not defined" even though its contents are clear again.

Basic extensions
- [x] Allow adding any feature to the map, not just flags and rivers. Every single method listed under #### Methods in the main README should have an appropriate interface for adding it:
  - [x] Flags (already exist, but allow adding any attribute, not just label, note and GADM code)
  - [x] Rivers
    - [x] Needs to allow overpass() rivers as well---let the user choose overpass or natural earth, and enter the ID. Also it should not say "NE ID / Name", only ID works (for now at least). You can use naturalearth("1159122643") (Ganga) as a sample example.
    - [x] Do not prefill the ID with the text "Ganges". Instead prefill with "1159122643" for Naturalearth and "1159233" for Overpass.
  - [x] Admin
  - [x] AdminRivers
  - [x] Path, Point, Text.
    - [ ] For Point, think carefully about how to implement the icon choice UI (whatever is supported by .Icon() in the library---both the in-built icons, geometric and any custom ones).
  - [x] Dataframes will be complicated, but at least the user should be able to upload a CSV. (See README.md for the format of the pandas dataframe)
    - [x] The sample example prefilled when adding a dataframe has the GID column titled "gadm". This is wrong, it should be "GID".
    - [x] Remove the "Find in GADM" field. Even in the original package it's kind of irrelevant.
    - [x] plotting data doesn't really work for some reason, it generates the following error.
    - [ ] We should not need to enter the data and year columns manually.
    - [ ] disputed territories don't plot correctly [this might be an issue with the package itself, I'll have to see]

  - [x] NOTE: allow adding any attribute to those objects, not just label, note and GADM code. Period is especially important. The less important attributes could be hidden under a "More..."
    - [x] "Period" should not be under a "More Options" It is optional, but should still be accessible without clicking "More Options". All the other things under "More Options" are fine there.
  - Global options---only TitleBox should be displayed prominently, the rest can be under a "More..." button and shown if expanded
    - [X] .TitleBox() (this already exists, but it should be a multiline textbox instead of a single line, it should be called "TitleBox (HTML)" instead of "Map Title", and the font for the content should be monospace)
      - [x] Thanks for fixing the other things, but change this to "TitleBox (HTML) please, not just "Title (HTML)".
    - [x] .CSS() --- the interface for this should be as follows: we have a list of classes (record all the classes used in rendering the map and use them here, and also add any custom CSS classes the user added for any element he added); each row is a pair of a dropdown (containing that list of classes) and the corresponding style for it in a text field. The user can add or delete rows, or change the class from that dropdown.
      - [x] Right now this is implemented in a weird way where the input is a text field prefilled with ".flag" and the options appear as autocomplete options. I think this is unintuitive for users---instead, make it an actual dropdown, with a "Custom..." option which if selected lets the user input any custom class/CSS selector.
    - [x] Base Layers: allow adding any number of base layers, and selecting one as default.
      - [x] Fixed. But the UI is a bit clumsy. Instead, just have the list of available base layers as checkboxes (where checking a box means it will be included in the base layer options) and include buttons next to them to make default (it should only be possible to make one default).
    - [ ] FlagColorSequence, AdminColorSequence, DataColormap --- think through the interface for this carefully; users should be able to set the obvious ones easily, or create their own color sequence or map, just like in the package itself (see the README for details). [This still needs to be done better---also it should be possible to set multiple color sequences for different classes].
    - [x] zoom and focus
      - [x] this should include a button to just use the current zoom and focus levels at the map is at
      - [x] there's a weird bug where I can't clear the contents of Initial focus manually because if I clear Latitude, Longitude becomes filled again (with 0) and if I clear Longitude, Latitude gets filled again. Fix that.
      - [x] Add a little clear button to the Initial View and Time slider buttons to reset their contents to emptiness.
    - [x] slider()
      - [x] It has the same bug of not allowing 0 as a year
  Wherever something is a bit complicated for the user to know how to set---e.g. color sequences and color maps, or icons for Point; there should be a little info tooltip with helpful documentation.
- [x] Exporting map JSON and HTML
- [x] Loading a previously-built map. I think the best way to do this will be to keep the state of the Builder and Code synchronized two-way and just export/import the code both ways.
  - [ ] Code generation is quite buggy.
    - [ ] One issue I've observed: for rivers it creates a random attribute source_type for River objects, which doesn't exist. This is not necessary, the value is already either naturalearth() or overpass()---you just need to make sure these are imported at the top.

Features
- [x] Visual ways to draw Paths, picking locations for Texts and Points.
  - [ ] Amazing, well done. Just one thing: show some visual cues on the map when picking points or drawing paths and polygons; i.e. actually show/preview the path or polygon being drawn.
    - [ ] I think a previous AI agent attempted to implement this, but has failed: no visual cues appear.
  - [ ] Also allow a user to undo the last point by pressing backspace.
    - [ ] This doesn't seem to be working either.
  - [ ] Also allow a user to draw a path "freehand" by pressing spacebar (or maybe some other key---you pick whatever makes sense, like what's in line with tools like photoshop?) once, then holding and dragging. Press spacebar again to get out of freehand mode.
    - [ ] Nor this.
  - [ ] Display these tips (backspace, freehand mode)
    - [ ] These tips should be shown in a blaring message on the map while picker mode is on, not underneath the box like it currently is.
  - [x] One problem is that the user may forget to un-click the picker and leave it on while picking other co-ordinates. To avoid this, only one picker should be turned on at a time: clicking another picker should turn off all the other ones (and show this visually too).
  - [x] Oh, and for Path the co-ordinates should not be pre-filled with [[28.6, 77.2], [19.0, 72.8]] like they are now: it should start out blank, like polygon does.
- [x] Better Territory setting interface---right now it just lets you pick one individual GADM for a flag, rather than any complex territory. Instead, we should have a fancier system: where you can compose the territory with the | and - operations (so you have buttons "add" and "subtract" which let you define a new step of the operation); in each component you can select `gadm`, Predefined territory or `polygon`.
  - [x] `gadm` should have autocomplete search for all the gadm entities in the data based on their GIDs, names and varnames (there should be a pre-computed list---and make sure you know what these look like, e.g. the "_1"s in the GIDs are not considered by xatra, so we just give gadm("IND.31") not gadm("IND.31_1")).
    - [x] The `_1`s are a bit of a problem, because it means IND.31_1 comes *after* IND.31.1_1, IND.31.8_1 etc. which basically makes it invisible as it is under all its children. Instead you should strip the codes of their `_1`.
      - [x] No, no no---you fixed this wrong. I didn't ask you to strip `_1` from the input field if the user inputs it (please revert this), I asked you to strip it out in the list of GIDs that we search.
  - [x] Predefined territories should be a section under the Code tab, also in the form of a code field. For any existing territory in the Flags, there should be a button to add it to pre-existing territories.
  - [x] `polygon` should, in addition to just typing out co-ordinates manually, have a visual way to draw it on the map---by picking points or tracing them out if some key is held.
  - [ ] Still need to implement the ability to actually *use* pre-defined territories in the territory-making (i.e. as an option in the dropdown alongside GADM and polygon).
    - [ ] a previous AI agent has attempted to do this, but it doesn't really work: the pre-defined territories do not seem to contribute to the computed territories at all.
    - [ ] then there should be autocomplete search for entering pre-defined territories in the pre-defined territory option
    - [ ] xatra.territory_library should be imported in the Pre-defined territories code, and available in the list of pre-defined territories (for autocomplete search)
- [x] The user should be able to create AN auxillary "Picker map" for visualizing and selecting admin features and pre-defined territories. The map panel should be tabbed, so the user can create a new (or switch to THE) Picker Map tab---when they create a new Picker Map tab, they will get to set any number of countries whose admin maps (at any level) to load, or instead to create a map with .AdminRivers(), or instead to load the pre-defined territories for visualization.
  - [x] Nice, I like the implementation. However, instead of just one field for Countries and one field for Level, the user should be able to add multiple rows, one for each country and set the level for each. So e.g. I can have IND: 2: PAK: 3.
    - [x] Nice. However, the box and its contents are a bit weirdly-sized (the contents don't fit the box which causes a horizontal scrollbar to appear)
    - [x] The user should be able to search for their country (either by GID or by country name) when entering a country code--just like they can while entering GADM territories for Flags.
  - [ ] Then they will be able to select gadm territories from an admin Picker map.
  - [ ] that can also be extended to select multiple gadm territories at once from the admin Picker map by pressing some key, and add them as multiple `| gadm(...)` or `- gadm(...)` fields.
  - [ ] And also selecting rivers
- [x] Code editor should be nice, not just a simple text editor.
  - [ ] Main thing I'd like is autocomplete---like in VS Code or in online coding sites like leetcode. It should work as though xatra is actually imported. Maybe can use an actual code editor plugin or something.

Minor changes
- [ ] "Rivers" in the add Layers panel should be "All Rivers".
- [ ] "Picker Map" should be called "Reference Map" instead.

Development difficulties
- [ ] keeping synchrony between things---this should be documented, i.e. "if you change this, then change this too"

For eventually publishing this as an app
- [ ] Sandboxing code (like in those online coding assessment platforms)
- [ ] User accounts
  - [ ] saving and publishing maps on platform (publishing can be for paid users only)
  - [ ] publishing territory libraries and CSS
  - [ ] importing existing map content, territory libraries and CSS into project
- [ ] AI agent --- only for paid users
  - [ ]