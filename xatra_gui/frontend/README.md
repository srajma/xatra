# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## TODO

Bugs
- [ ] Base map doesn't appear by default---it appears in the Base Layer dropdown and I can select it and it appears, but the map renders with None by default even though I have a Base Layer selected which is odd

Basic extensions
- [ ] Allow adding any feature to the map, not just flags and rivers. Every single method listed under #### Methods in the main README should have an appropriate interface for adding it:
  - [ ] Flags, Rivers (already exist, but allow adding any attribute, not just label, note and GADM code)
  - [ ] Admin
  - [ ] AdminRivers
  - [ ] Path, Point, Text. For Point, think carefully about how to implement the icon choice UI (whatever is supported by .Icon() in the library---both the in-built icons, geometric and any custom ones).
  - [ ] Dataframes will be complicated, but at least the user should be able to upload a CSV. 
  - [ ] NOTE: allow adding any attribute to those objects, not just label, note and GADM code. Period is especially important. The less important attributes could be hidden under a "More..."
  - Global options---only TitleBox should be displayed prominently, the rest can be under a "More..." button and shown if expanded
    - [ ] .TitleBox() (this already exists, but it should be a multiline textbox instead of a single line, it should be called "TitleBox (HTML)" instead of "Map Title", and the font for the content should be monospace)
    - [ ] .CSS() --- the interface for this should be as follows: we have a list of classes (record all the classes used in rendering the map and use them here, and also add any custom CSS classes the user added for any element he added); each row is a pair of a dropdown (containing that list of classes) and the corresponding style for it in a text field. The user can add or delete rows, or change the class from that dropdown.
    - [ ] Base Layers: allow adding any number of base layers, and selecting one as default.
    - [ ] FlagColorSequence, AdminColorSequence, DataColormap --- think through the interface for this carefully; users should be able to set the obvious ones easily, or create their own color sequence or map, just like in the package itself (see the README for details).
    - [ ] zoom and focus (this should include a button to just use the current zoom and focus levels at the map is at)
    - [ ] slider()
  Wherever something is a bit complicated for the user to know how to set---e.g. color sequences and color maps, or icons for Point; there should be a little info tooltip with helpful documentation.
- [ ] Exporting map JSON and HTML
- [ ] Loading a previously-built map. I think the best way to do this will be to keep the state of the Builder and Code synchronized two-way and just export/import the code both ways.

Features
- [ ] Visual ways to draw Paths, picking locations for Texts and Points.
- [ ] Better Territory setting interface---right now it just lets you pick one individual GADM for a flag, rather than any complex territory. Instead, we should have a fancier system: where you can compose the territory with the | and - operations (so you have buttons "add" and "subtract" which let you define a new step of the operation); in each component you can select `gadm`, Predefined territory or `polygon`.
  - `gadm` should have autocomplete search for all the gadm entities in the data based on their GIDs, names and varnames (there should be a pre-computed list---and make sure you know what these look like, e.g. the "_1"s in the GIDs are not considered by xatra, so we just give gadm("IND.31") not gadm("IND.31_1")).
  - Predefined territories should be a section under the Code tab, also in the form of a code field. For any existing territory in the Flags, there should be a button to add it to pre-existing territories.
  - `polygon` should, in addition to just typing out co-ordinates manually, have a visual way to draw it on the map---by picking points or tracing them out if some key is held.
type the code for any territory, like: gadm("IND") | gadm("AFG") | KURU - (gadm("IND.31") | polygon(...)). There should be nice autocomplete --- depending on the context of where we are typing, 
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