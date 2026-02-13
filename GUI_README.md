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
- [x] territories don't get stored correctly if they themselves contain pre-computed territories. I.e. if I define a new Flag and build a territory for it KURU | gadm("IND.31") | polygon([[25.483,74.8389],[21.6166,70.2246],[14.1792,68.7305],[15.5807,75.6299],[16.6362,80.6836]]), it will just get stored as: india =  |  |  |  - gadm("IND.12") | polygon([[25.483,74.8389],[21.6166,70.2246],[14.1792,68.7305],[15.5807,75.6299],[16.6362,80.6836]]).
- [x] Bugs with the code editor
  - [x] Weird bug: Every time I switch away from the Code window and then back to it, another copy of each item in the autocomplete appears. So when one first clicks out and back, there are two copies of "xatra" in the autocomplete menu, and if you type `xatra.` then there are two copies of `Admin` etc.; do it again and there are three copies of each, etc.
  - [x] Code editor is weirdly smaller vertically than the space available in the boxes for them 
    - [x] Map Code editor now uses ResizeObserver to fill available height in the Code tab panel.
      - [x] Map Code is fine, but Predefined Territories code editor is still much smaller than its box.
  - [x] This tip: `Type xatra. or map. for map methods. Use Ctrl+Space for suggestions.` should not say `map.`, it should just be `Type xatra. for map methods. Use Ctrl+Space for suggestions.`
  - [x] I have vimium installed, and when I try typing in the code editor it doesn't realize I'm in insert mode. This is weird, since I haven't had this issue on other sites using Monaco. Can you figure out how to fix this? 
    - [x] The current attempted fixes, "Force focus" etc. don't work, and should be removed to avoid bloat. Instead, just put a blaring banner at the top of the code screen saying "If you are using<b>Vimium</b>, please DISABLE it on this website."

Basic extensions
- [x] Allow adding any feature to the map, not just flags and rivers. Every single method listed under #### Methods in the main README should have an appropriate interface for adding it:
  - [x] Flags (already exist, but allow adding any attribute, not just label, note and GADM code)
  - [x] Rivers
    - [x] Needs to allow overpass() rivers as well---let the user choose overpass or natural earth, and enter the ID. Also it should not say "NE ID / Name", only ID works (for now at least). You can use naturalearth("1159122643") (Ganga) as a sample example.
    - [x] Do not prefill the ID with the text "Ganges". Instead prefill with "1159122643" for Naturalearth and "1159233" for Overpass.
  - [x] Admin
  - [x] AdminRivers
  - [x] Path, Point, Text.
    - [x] For Point, think carefully about how to implement the icon choice UI (whatever is supported by .Icon() in the library---both the in-built icons, geometric and any custom ones).
  - [x] Dataframes will be complicated, but at least the user should be able to upload a CSV. (See README.md for the format of the pandas dataframe)
    - [x] The sample example prefilled when adding a dataframe has the GID column titled "gadm". This is wrong, it should be "GID".
    - [x] Remove the "Find in GADM" field. Even in the original package it's kind of irrelevant.
    - [x] plotting data doesn't really work for some reason, it generates the following error.
    - [x] We should not need to enter the data and year columns manually.
      - [x] Actually just remove the fields for entering data and year columns entirely, we don't need them.

  - [x] NOTE: allow adding any attribute to those objects, not just label, note and GADM code. Period is especially important. The less important attributes could be hidden under a "More..."
    - [x] "Period" should not be under a "More Options" It is optional, but should still be accessible without clicking "More Options". All the other things under "More Options" are fine there.
  - Global options---only TitleBox should be displayed prominently, the rest can be under a "More..." button and shown if expanded
    - [X] .TitleBox() (this already exists, but it should be a multiline textbox instead of a single line, it should be called "TitleBox (HTML)" instead of "Map Title", and the font for the content should be monospace)
      - [x] Thanks for fixing the other things, but change this to "TitleBox (HTML) please, not just "Title (HTML)".
    - [x] .CSS() --- the interface for this should be as follows: we have a list of classes (record all the classes used in rendering the map and use them here, and also add any custom CSS classes the user added for any element he added); each row is a pair of a dropdown (containing that list of classes) and the corresponding style for it in a text field. The user can add or delete rows, or change the class from that dropdown.
      - [x] Right now this is implemented in a weird way where the input is a text field prefilled with ".flag" and the options appear as autocomplete options. I think this is unintuitive for users---instead, make it an actual dropdown, with a "Custom..." option which if selected lets the user input any custom class/CSS selector.
    - [x] Base Layers: allow adding any number of base layers, and selecting one as default.
      - [x] Fixed. But the UI is a bit clumsy. Instead, just have the list of available base layers as checkboxes (where checking a box means it will be included in the base layer options) and include buttons next to them to make default (it should only be possible to make one default).
  - [x] FlagColorSequence, AdminColorSequence, DataColormap --- think through the interface for this carefully; users should be able to set the obvious ones easily, or create their own color sequence or map, just like in the package itself (see the README for details). [This still needs to be done better---also it should be possible to set multiple color sequences for different classes].
    - [x] Nah the FlagColorSequence interface is still totally wrong. See the colorseq.py file---basically we should always construct a linear color sequence, and the user should be able to enter the step-sizes in H,S,L and optionally a list of starting colors, and we initialize a LinearColorSequence(colors=those optional colors or None if not provided, step=Color.hsl(those values)). It should be pre-loaded with the default color sequence, LinearColorSequence(colors=None,step=Color.hsl(1.6180339887, 0.0, 0.0)) (and there doesn't need to be that cluttery explanatory note explaining that this is a default, like there is now). The user should also be able to restrict the color sequence to any particular class if need be, but the dropdown should not consist of all the classes present but only the custom classes that have been applied to Flags.
      - [x] Ok, it's better now---but it doesn't fit in the horizontal space.
      - [x] AdminColorSequence should work the same way as FlagColorSequence.
        - [x] Except one thing: the UI shouldn't allow adding multiple AdminColorSequences, and there should not be a class dropdown for it. Unlike FlagSequences, there can only be one AdminColorSequence, and it doesn't take any `class_name` parameter since it applies to all classes.
      - [x] The Datacolormap UI is also weird. Instead, there should be a dropdown to select the color map (e.g. viridis etc.), and if "LinearSegmented" is selected, it should allow the user to input a list of colors. By default "LinearSegmented" should be selected, and the colors should be yellow, orange, red.
  - [x] zoom and focus
    - [x] this should include a button to just use the current zoom and focus levels at the map is at
    - [x] there's a weird bug where I can't clear the contents of Initial focus manually because if I clear Latitude, Longitude becomes filled again (with 0) and if I clear Longitude, Latitude gets filled again. Fix that.
    - [x] Add a little clear button to the Initial View and Time slider buttons to reset their contents to emptiness.
  - [x] slider()
    - [x] It has the same bug of not allowing 0 as a year
  Wherever something is a bit complicated for the user to know how to set---e.g. color sequences and color maps, or icons for Point; there should be a little info tooltip with helpful documentation.
- [x] Exporting map JSON and HTML

Features
- [x] Visual ways to draw Paths, picking locations for Texts and Points.
  - [x] Amazing, well done. Just one thing: show some visual cues on the map when picking points or drawing paths and polygons; i.e. actually show/preview the path or polygon being drawn.
  - [x] Also allow a user to undo the last point by pressing backspace.
    - [x] I think a previous AI agent attempted to implement this, but has failed.
      - [x] Fixed by forwarding Backspace/Escape/Space from the map iframe to the parent (focus is in iframe when user clicks map)
  - [x] Also allow a user to draw a path "freehand" by pressing spacebar (or maybe some other key---you pick whatever makes sense, like what's in line with tools like photoshop?) once, then holding and dragging. Press spacebar again to get out of freehand mode (and then you can continue clicking points normally).
    - [x] Ok, one issue: holding and dragging *also* moves the map around at the same time. Maybe instead of pressing spacebar + dragging, we should change it to holding shift and dragging, and prevent Leaflet from moving the map when shift is pressed.
      - [x] Fixed. However, Shift is actually also used for zooming in to maps, so another conflict. Can we switch to Ctrl+dragging (Cmd should also work for Mac users)?
        - [x] This works as long as I click at least one point on the map before going freehand, or if I hold down my mouse at a point then press control---but if I already have control held and then start drawing, the moving-around doesn't get cancelled---kind of like it needs the map to be in focus for the Ctrl to have the desired effect?
  - [x] Display these tips (backspace, freehand mode)
    - [x] These tips should be shown in a blaring message on the map while picker mode is on, not underneath the box like it currently is.
  - [x] One problem is that the user may forget to un-click the picker and leave it on while picking other co-ordinates. To avoid this, only one picker should be turned on at a time: clicking another picker should turn off all the other ones (and show this visually too).
  - [x] Oh, and for Path the co-ordinates should not be pre-filled with [[28.6, 77.2], [19.0, 72.8]] like they are now: it should start out blank, like polygon does.
- [x] Better Territory setting interface---right now it just lets you pick one individual GADM for a flag, rather than any complex territory. Instead, we should have a fancier system: where you can compose the territory with the | and - operations (so you have buttons "add" and "subtract" which let you define a new step of the operation); in each component you can select `gadm`, Predefined territory or `polygon`.
  - [x] `gadm` should have autocomplete search for all the gadm entities in the data based on their GIDs, names and varnames (there should be a pre-computed list---and make sure you know what these look like, e.g. the "_1"s in the GIDs are not considered by xatra, so we just give gadm("IND.31") not gadm("IND.31_1")).
    - [x] The `_1`s are a bit of a problem, because it means IND.31_1 comes *after* IND.31.1_1, IND.31.8_1 etc. which basically makes it invisible as it is under all its children. Instead you should strip the codes of their `_1`.
      - [x] No, no no---you fixed this wrong. I didn't ask you to strip `_1` from the input field if the user inputs it (please revert this), I asked you to strip it out in the list of GIDs that we search.
  - [x] Predefined territories should be a section under the Code tab, also in the form of a code field. For any existing territory in the Flags, there should be a button to add it to pre-existing territories.
  - [x] `polygon` should, in addition to just typing out co-ordinates manually, have a visual way to draw it on the map---by picking points or tracing them out if some key is held.
  - [x] Still need to implement the ability to actually *use* pre-defined territories in the territory-making (i.e. as an option in the dropdown alongside GADM and polygon).
    - [x] a previous AI agent has attempted to do this, but it doesn't really work: the pre-defined territories do not seem to contribute to the computed territories at all.
    - [x] then there should be autocomplete search for entering pre-defined territories in the pre-defined territory option
    - [x] xatra.territory_library should be imported in the Pre-defined territories code, and available in the list of pre-defined territories (for autocomplete search)
- [x] The user should be able to create AN auxillary "Picker map" for visualizing and selecting admin features and pre-defined territories. The map panel should be tabbed, so the user can create a new (or switch to THE) Picker Map tab---when they create a new Picker Map tab, they will get to set any number of countries whose admin maps (at any level) to load, or instead to create a map with .AdminRivers(), or instead to load the pre-defined territories for visualization.
  - [x] Nice, I like the implementation. However, instead of just one field for Countries and one field for Level, the user should be able to add multiple rows, one for each country and set the level for each. So e.g. I can have IND: 2: PAK: 3.
    - [x] Nice. However, the box and its contents are a bit weirdly-sized (the contents don't fit the box which causes a horizontal scrollbar to appear)
    - [x] The user should be able to search for their country (either by GID or by country name) when entering a country code--just like they can while entering GADM territories for Flags.
  - [x] Then they will be able to select gadm territories from an admin Picker map.
  - [x] that can also be extended to select multiple gadm territories at once from the admin Picker map by pressing some key, and add them as multiple `| gadm(...)` or `- gadm(...)` fields. This will need some re-thinking of how the solution is currently implemented.
    - [x] Very nice implementation. However, I want this to be implemented a bit differently, because there can actually be multiple flag layers with the same label (and this is an important aspect of the app). So instead:
      - The GADM territories have a pick button (use the little arrow icon instead of "Use Picked" text), and that sets the flag layer being selected for to this particular element and also switches the view to Reference Map.
      - The user should not be able to select this flag layer from a dropdown in the Reference Map Options box like they are now (it's too confusing), however it should lightly display the flag name and a number representing which layer with that Flag label is being selected for (e.g. 15 if the 15th instance of that Flag label in the Layers list is being selected for).
      - Clicking a territory should add it to the list of territories being multi-selected, or remove it if it is already in the list. No need for Ctrl/Cmd/Shift, since we're going to do away with the separate single selections feature anyway. Holding Ctrl and moving the mouse should select all territories it moves over (no undoing already-selected territories in this mode); holding Alt and moving the mouse should unselect all territories it moves over. There should be a little tip mentioning this in the Reference Map Options.
      - Instead of choosing +, -, & from a dropdown, let us just have three buttons for us to choose how to add these selections to our territory. Keep the Clear button as it is. These are added/subtracted/intersected to our territory based on the operation button chosen.
      - The divisions in our selection list should be visually indicated on the map.
      - River selection should also just have a pick icon and we pick a river on the Admin Rivers.
      - We can then do away with the legacy "Last picked" and "Use Picked" features.
      - In all of this, make sure these new Pick buttons have the same "exclusivity" as the existing Pick buttons (for paths, points, polygons and texts)---only one is allowed to be on at a time, clicking it turns off the previous Picker.
  - [x] And also selecting rivers
- [x] Code editor should be nice, not just a simple text editor.
  - [x] Main thing I'd like is autocomplete---like in VS Code or in online coding sites like leetcode. It should work as though xatra is actually imported. Maybe can use an actual code editor plugin or something.
- [x] Loading a previously-built map. I think the best way to do this will be to keep the state of the Builder and Code synchronized two-way and just export/import the code both ways.
  - [x] Code generation is quite buggy.
    - [x] One issue I've observed: for rivers it creates a random attribute source_type for River objects, which doesn't exist. This is not necessary, the value is already either naturalearth() or overpass()---you just need to make sure these are imported at the top.
    - [x] When a Flag has a blank value (i.e. nothing has been built in Territory) or anything else is blank, it should default be converted to None in the code, not just left empty causing a syntax error.
    - [x] Eventually we should also implement reverse-syncing the code to the builder, so might be worth thinking about how to better store the state
    - [x] Also need to make sure any changes to the pre-defined territories code will update the stored territories.
    - [x] Once we have arranged the two-way synchronization perfectly, the Builder-Code syncing should be modified to happen automatically upon switching from Builder to Code and vice versa, rather than manually clicking Sync from Builder
- [x] Better keyboard-based navigation. This will need to be implemented very carefully and thoroughly, making sure everything is easily accessible by keyboard or has convenient keyboard shortcuts---these should all be documented in the little keyboard shortcuts hint panel that appears when pressing ? or clicking the button for it.
    - [x] It should be made possible to navigate the autocomplete searches via keyboard---both in the territory GADM picker and in the Reference Map autocomplete-search for countries.
      - [x] When going down on an autocomplete search, it should scroll the autocomplete search box as necessary.
    - [x] Keyboard shortcuts for adding a new layer
    - [x] When a new layer is created, its first input field should immediately be focused.
      - [x] A previous agent attempted to do this, but it doesn't seem to be working. The input field should be focused so that the user can immediately start typing.
    - [x] Keyboard shortcut Ctrl+Space to run "Update Reference Map" if in the Reference Map tab or "Update Territory Library Map" if in the Territory Library tab
      - [x] This is a bit unreliable---Ctrl+Space stops working if I click on the map, or if I click on the checkboxes in the Territory Library options, or if I click on the input fields in the Reference Map Options.
- [x] Territory library tab (Ctrl/Cmd+5)
  - This will be a third map tab after "Map Preview" and "Reference Map", and will serve to visualize territories in the territory library.
  - Within this tab, there are multiple tabs. There is one tab for xatra.territory_library and one tab for those that the user has saved to library/entered in the Territory library code editor.
    - [ ] In future, when we have multiple territory libraries (i.e. when it's a proper website where people can publish their own territory libraries), it will show 
  - Within each sub-tab, the territories in that list are plotted on the map (i.e. by wrapping them in Flags and letting their labels be their variable names).
  - [x] When the user is entering an item from Territory library while building a Territory for a Flag, he will have a little Picker button. Clicking this will take him to the Territory Library where there will be a very similar multi-selection UI as in the Reference Map tab.
  - [x] Hmm, ther seem to be too many things in the territory library to render. Instead, the territory library file should include an index at the end __TERRITORY_INDEX__ = ["TERRITORY_1_NAME", "TERRITORY_2_NAME", ...] and there should be a checklist of territories in the Territory library map---the checklist will contain all the territories in the library, but only the ones in the index will be checked by default, while extra ones can be selected and rendered by the user. If there is no __TERRITORY_INDEX__ variable in the territory library (whether xatra.territory_library, the user's custom territory library for this map, or in future any imported territory library), then it should be considered [], i.e. all the boxes should be un-checked. When the user selects a bunch of checkboxes, there should be a button to copy the list consisting of those selected territory names so that they can be used as a __TERRITORY_INDEX__.
    - [x] The Orange banner (about Shift and backspace) should not appear for territory picker.
    - [x] It shouldn't re-render the territory library map every time a checkbox is marked or unmarked---instead it should only update when the button to re-render the map is pressed
    - [x] It also shouldn't re-render the territory library map every time we navigate to the territory library tab.
    - [x] However, it _should_ render the territory library map in the background when the page is loaded (just like the reference map is loaded in the background).
    - [x] Why is there a tip saying "Default index: VRJISTHANA, VARNU, VANAVYA, APRITA, PSEUDOSATTAGYDIA_S, ..."? We don't need this, we can already see in the checklist which boxes are marked.
    - [x] The territory library checklist should have a search bar to filter and select the checkboxes based on your search term.
    - [x] The "Copy index" button should be an icon instead of text, and when it is clicked it should temporarily show a visual cue that it has been copied to clipboard.
    - [x] When it is rendering one of the maps (Map Preview, Reference Map, Territory library), why do all the other maps also need to get blurred out and blocked from interaction?
    - [x] with regard to how the Reference Map and Territory Library render in the background when we first load the page, it is a bit misleading because it just shows "No map rendered yet" with no sign of rendering going on. Instead it should show the usual blur Generating screen over those maps. Also in the Territory Library box the checklist and everything should be fully displayed before waiting for the map to load.

Minor changes
- [x] "Rivers" in the add Layers panel should be "All Rivers".
- [x] "Picker Map" should be called "Reference Map" instead.
- [x] The panel for adding layers should be at the *bottom* of the layer list, so that new layers just get added on top of it (while scrolling just to compensate for the new element to ensure the panel is still in view) rather than having to scroll all the way to the bottom like it is now.
  - [x] Thank you---but can you make it automatically scroll to the very bottom of the panel after adding any new layer?
- [x] should be able to reorder the lines of the territory builder (the operations) around by dragging them (and it should also reorder them in the internal state)
- [x] when you save a territory to library, it should be case-sensitive, i.e. if you store the territory of a flag called "India" its variable name should be "India" and not "india".
- [x] We now have visual cues for drawing paths and polygons, thank you---just one thing: the *vertices* of paths and polygons should also be shown in this visual cue, with dots, so that even the first point drawn can be seen on the map before any actual line is drawn.
  - [x] Also implement this for Points and Texts. When a point has a pre-existing value for Position and you hit the "Click on map" button, it should show that little point on that map with the same sort of dot.
    - [x] Also: these visual cues should appear regardless of which map (Map Preview, Reference Map, Territory Library) we're on. Right now they appear for the former two but not the last one.
    - [x] For points and texts, the visual cue (the dot) at the point where we click should persist for a fraction of a second after we press it, so that we can still see it even though the Picker mode is instantly turned off.
- [x] The "Note" field should have monospaced font.
- [x] Everywhere we use the term "Pre-defined territory", use "Territory library" instead.
  - [x] And include a from xatra.territory_library import * line at the top, since all those territories are included in our library---and in a comment right next to it, link to https://github.com/srajma/xatra/blob/master/src/xatra/territory_library.py. Remove all the other junk comments pre-filled there by default.
- [x] In "Reference Map Options", just like there's a label "Countries" for the country field there should be a label "Admin Level" for the Admin Level field.
  - [x] Also, the levels entry field should be a dropdown with all the admin levels available for their country (these should be pre-computed and kept in an index).
- [x] The Keyboard Shortcuts panel should have a little icon to toggle it so the user can see the keyboard shortcuts list even if he doesn't already know that `?` does the job.
- [x] Clicking "Render Map" (from either Builder or Code) should set the tab (which can currently be "Map Preview" or "Reference Map") to "Map Preview".
- [x] The picker icons for picking GADMs and Rivers from the Reference Map, and for picking territories from the Territory library map, should match the nicer icon that is used for picking co-ordinates from the map for Points/Texts/Paths/Polygons.
- [x] Under the title "Flag" in a Flag layer, there should be a small note: "A <b>Flag</b> asserts the reign of a State over a Territory (perhaps for a particular period of time). Flag layers with the same State name are rendered as the same geometry."
  - [x] Oh, and change the displayed label of the "Label" input field to "State name" instead of "Label" (obviously the underlying parameter should still be "label").
- [x] In the GADM picker, when we press the Add/Subtract/Intersect buttons (to add the selections to a Flag layer's territory as operations), any blank GADM row in that Flag layer's territory (blank meaning: without a value/with the value field blank) should be deleted after the new operations are added. Similarly in the Territory library picker, when we press the Add/Subtract/Intersect buttons, any blank Territory library row in that Flag layer's territory should be automatically deleted after the new operations are added.
- [x] By default, the Reference Map should be loaded as IND-2, PAK-3, BGD-2, NPL-3, BTN-1, LKA-1, AFG-2 with Admin Rivers. The loading can happen in the background while the user can still work on things.
- [x] The countries column in the reference map should allow any GADM ID, not just country codes---since xatra.Admin() allows for it. So its search autocomplete should be exactly like that of the GADM entries in the Flag layer territory building, and there should not be any restriction on the characters (since we might want to search for these things by name). The level dropdown should still be taken from the country code part of the GADM ID (i.e. for IND.20 still take the levels list from that of IND).
- [x] When "Generating Map" is going on (for whatever generation---either the Map Preview, the Reference Map or the Territory Library), it blurs out everything in the map frame, including the Reference Map options box and the Territory library box. It should leave these boxes available for the user to interact with while the map renders.
- [x] Remove this hint: `Ctrl/Cmd+5` opens this tab. `Custom Library` uses the code from the Code tab's Territory library editor.
- [x] TitleBox should actually not be a global element, but a layer---xatra supports adding as many "TitleBox" elements as you want, e.g. with different periods. As with the other layers, the "period" field should be present.

Design improvements
- [x] introduce a dark mode
- [x] the "Xatra Studio" title is cheesy. Replace it with just xatra (lowercase), and no icon.

Experiments I have to do
- [ ] Make sure my existing maps work in this
- [ ] experiment with some different designs

Development difficulties
- [x] keeping synchrony between things---this should be documented, i.e. "if you change this, then change this too"
  - See "Development / Synchrony" section below.

For eventually publishing this as an app
- [ ] Move GUI to a separate repo instead of being part of the main xatra package
- [ ] Sandboxing code (like in those online coding assessment platforms)
- [ ] Database of user accounts, maps created by them etc.
  - [ ] saving and publishing maps on platform (publishing can be for paid users only)
  - [ ] publishing territory libraries and CSS
  - [ ] importing existing map content, territory libraries and CSS into project
- [ ] AI agent --- only for paid users

Efficiency and scalability for publishing as an app
- [ ] Re-rendering the whole map each time is inefficient

---

## Implementation plans for remaining roadmap items

### 1) Vimium/editor insert mode
- Add an optional "Force editor focus" mode that keeps focus in Monaco while the Code tab is active.
- Add a fallback keyboard shortcut in-app (e.g. `Ctrl+Alt+I`) that focuses the active editor without mouse.
- Document hard limit: browser extensions can still intercept keys globally before page handlers.

### 2) Reverse sync (Code -> Builder) and predefined-territory sync
- Define a canonical intermediate JSON schema for map state (elements, options, predefined territories).
- Build a Python AST parser pipeline for supported `xatra.*` calls and loader expressions (`gadm`, `polygon`, `naturalearth`, `overpass`).
- Parse `predefined_code` assignments into structured territory expressions and update in-memory territory namespace used by builder render requests.
- Add conflict reporting when code contains unsupported dynamic constructs (loops/functions) and keep those in code-only mode.

### 3) Reference map multi-select for GADM and bulk add/subtract
- Add a reference-picker mode with explicit target flag + operator (`union`/`difference`).
- Support modifier-key multi-select on map (Ctrl/Cmd) and maintain a selected-GADM chip list.
- Add "Apply selected to territory" action that appends ordered operations into `TerritoryBuilder` state.

### 4) Keyboard navigation completeness
- Add global command palette / shortcut map (`?` overlay) for tab switch, render, stop, and picker toggles.
- Ensure picker controls, layer cards, and operation rows are fully reachable via Tab/Shift+Tab with visible focus rings.
- Add keyboard reordering for territory rows (`Alt+ArrowUp/Down`) in addition to drag-and-drop.

### 5) Production platform features (sandboxing/accounts/publishing/AI)
- Sandbox:
  Use isolated worker containers (Firecracker/containers), strict CPU/memory/timeouts, blocked outbound network by default, signed artifact export only.
- Accounts + projects:
  Introduce auth (OIDC + sessions), project ownership, versioned saves, and RBAC tiers (free/paid).
- Publishing:
  Store published HTML/JSON + assets in object storage with immutable versions and moderated public links.
- AI agent:
  Add paid-tier feature gate, request quotas, audited tool execution logs, and policy-enforced prompt/tool sandboxing.

## Development / Synchrony

When changing behaviour that is shared between frontend and backend or between Builder and Code, keep these in sync:

| If you change… | Also change… |
|----------------|---------------|
| **Builder payload** (elements/options shape) | `xatra_gui/main.py` `run_rendering_task` for `task_type == 'builder'`, and any code generation in `App.jsx` `generatePythonCode`. |
| **River element** (source_type, value) | Backend: `main.py` river branch (naturalearth/overpass); Frontend: `generatePythonCode` (no `source_type` in generated code, use `naturalearth(...)` or `overpass(...)`). |
| **Point icon** (builtin / geometric / custom) | Backend: `main.py` point branch (resolve `args.icon` to `Icon`); Frontend: `LayerItem.jsx` icon UI and `generatePythonCode` (emit `Icon.builtin` / `Icon.geometric` / `Icon(...)`). |
| **Flag territory** (parts: gadm / polygon / predefined) | Backend: `main.py` Flag branch and `predefined_namespace` from `predefined_code`; Frontend: `TerritoryBuilder.jsx` and `formatTerritory` in `App.jsx`. |
| **Pre-defined territories** (variable names) | Backend: exec `predefined_code` with `territory_library` in scope; Frontend: send `predefined_code` in builder request; `TerritoryBuilder` uses parsed names + `GET /territory_library/names` for autocomplete. |
| **Draft overlay** (path/polygon/point on map) | Frontend: `postMessage({ type: 'setDraft', points, shapeType })` (use `shapeType` not `type`); Backend: `src/xatra/render.py` message handler `setDraft` uses `shapeType`. |
| **Rename in UI** (e.g. "Rivers" → "All Rivers", "Picker Map" → "Reference Map") | `Builder.jsx` (button/label), `App.jsx` (tab and panel titles). |
