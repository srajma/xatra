## TODO

Bugs
- [x] Base map doesn't appear by default---it appears in the Base Layer dropdown and I can select it and it appears, but the map renders with None by default even though I have a Base Layer selected which is odd
- [ ] Period field has a bug: it doesn't allow commas, so I cannot actually enter a range. It also doesn't seem to allow minus signs (which is how we enter BC dates---in fact, the example shown should be something like [-320, -180] and the "format" helper should explicitly say "use negative numbers for BC years".), or for the first entry to be 0 (which should be possible since these are years). This applies to all elements.
- [ ] Admin and AdminRivers elements have a bug: Error: Map.Admin() got an unexpected keyword argument 'label'.
- [ ] I get an Error: object of type 'int' has no len() sometimes ... leave this issue for now, I think fixing the Period field will fix it.

Basic extensions
- [x] Allow adding any feature to the map, not just flags and rivers. Every single method listed under #### Methods in the main README should have an appropriate interface for adding it:
  - [x] Flags (already exist, but allow adding any attribute, not just label, note and GADM code)
  - [x] Rivers
    - [ ] Needs to allow overpass() rivers as well---let the user choose overpass or natural earth, and enter the ID. Also it should not say "NE ID / Name", only ID works (for now at least). You can use naturalearth("1159122643") (Ganga) as a sample example.
  - [x] Admin
  - [x] AdminRivers
  - [x] Path, Point, Text.
    - [ ] For Point, think carefully about how to implement the icon choice UI (whatever is supported by .Icon() in the library---both the in-built icons, geometric and any custom ones).
  - [ ] Dataframes will be complicated, but at least the user should be able to upload a CSV. 
  - [x] NOTE: allow adding any attribute to those objects, not just label, note and GADM code. Period is especially important. The less important attributes could be hidden under a "More..."
    - [ ] "Period" should not be under a "More Options" It is optional, but should still be accessible without clicking "More Options". All the other things under "More Options" are fine there.
  - Global options---only TitleBox should be displayed prominently, the rest can be under a "More..." button and shown if expanded
    - [X] .TitleBox() (this already exists, but it should be a multiline textbox instead of a single line, it should be called "TitleBox (HTML)" instead of "Map Title", and the font for the content should be monospace)
      - [ ] Thanks for fixing the other things, but change this to "TitleBox (HTML) please, not just "Title (HTML)".
    - [x] .CSS() --- the interface for this should be as follows: we have a list of classes (record all the classes used in rendering the map and use them here, and also add any custom CSS classes the user added for any element he added); each row is a pair of a dropdown (containing that list of classes) and the corresponding style for it in a text field. The user can add or delete rows, or change the class from that dropdown.
      - [ ] Thank you, this is quite nice, however there are more classes used in xatra, which should be in the dropdown. See render.py for more.
      - [ ] Also add a "Custom..." option
    - [x] Base Layers: allow adding any number of base layers, and selecting one as default.
      - [ ] Fixed. But the UI is a bit clumsy. Instead, just have the list of available base layers as checkboxes (where checking a box means it will be included in the base layer options) and include buttons next to them to make default (it should only be possible to make one default).
    - [ ] FlagColorSequence, AdminColorSequence, DataColormap --- think through the interface for this carefully; users should be able to set the obvious ones easily, or create their own color sequence or map, just like in the package itself (see the README for details). [This still needs to be done better].
    - [x] zoom and focus
      - [ ] this should include a button to just use the current zoom and focus levels at the map is at
    - [x] slider()
      - [ ] It has the same bug of not allowing 0 as a year
  Wherever something is a bit complicated for the user to know how to set---e.g. color sequences and color maps, or icons for Point; there should be a little info tooltip with helpful documentation.
- [x] Exporting map JSON and HTML
- [ ] Loading a previously-built map. I think the best way to do this will be to keep the state of the Builder and Code synchronized two-way and just export/import the code both ways.

Features
- [ ] Visual ways to draw Paths, picking locations for Texts and Points.
- [x] Better Territory setting interface---right now it just lets you pick one individual GADM for a flag, rather than any complex territory. Instead, we should have a fancier system: where you can compose the territory with the | and - operations (so you have buttons "add" and "subtract" which let you define a new step of the operation); in each component you can select `gadm`, Predefined territory or `polygon`.
  - [x] `gadm` should have autocomplete search for all the gadm entities in the data based on their GIDs, names and varnames (there should be a pre-computed list---and make sure you know what these look like, e.g. the "_1"s in the GIDs are not considered by xatra, so we just give gadm("IND.31") not gadm("IND.31_1")).
    - [ ] The `_1`s are a bit of a problem, because it means IND.31_1 comes *after* IND.31.1_1, IND.31.8_1 etc. which basically makes it invisible as it is under all its children. Instead you should strip the codes of their `_1`.
  - [ ] Predefined territories should be a section under the Code tab, also in the form of a code field. For any existing territory in the Flags, there should be a button to add it to pre-existing territories.
  - [ ] `polygon` should, in addition to just typing out co-ordinates manually, have a visual way to draw it on the map---by picking points or tracing them out if some key is held.
- [ ] The user should be able to create auxillary "Picker maps" for visualizing and selecting admin features and pre-defined territories. The map panel should be tabbed, so the user can create a new (or switch to a) Picker Map tab---when they create a new Picker Map tab, they will get to set any number of countries whose admin maps (at any level) to load, or instead to create a map with .AdminRivers(), or instead to load the pre-defined territories for visualization.
  - [ ] Then they will be able to select gadm territories from an admin Picker map.
  - [ ] that can also be extended to select multiple gadm territories at once from the admin Picker map by pressing some key, and add them as multiple `| gadm(...)` or `- gadm(...)` fields.
- [ ] Code editor should be nice, not just a simple text editor.

Development difficulties
- [ ] keeping synchrony between things---this should be documented, i.e. "if you change this, then change this too"

For eventually publishing this as an app
- [ ] Sandboxing code (like in those online coding assessment platforms)
- [ ] User accounts
  - [ ] saving and publishing maps on platform (publishing can be for paid users only)
  - [ ] publishing territory libraries and CSS