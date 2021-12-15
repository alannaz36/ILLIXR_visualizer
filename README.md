# ILLIXR_visualizer

This project is designed to be a modular addition to the ILLIXR project: https://illixr.github.io/. It is a desktop GUI application for the visualization of logged ILLIXR data.

<p align="center">
  <img width="75%" src="https://raw.githubusercontent.com/alannaz36/ILLIXR_visualizer/main/gallery/visualize_data.png">
</p>

Launch the ILLIXR Visualizer from the terminal with `python illixr_visualizer.py`. The start-up screen will appear with instructions for loading ILLIXR data:

<p align="center">
  <img width="75%" src="https://raw.githubusercontent.com/alannaz36/ILLIXR_visualizer/main/gallery/startup.png">
</p>

In order to load demo ILLIXR data, go to Data &#8594; Load Data or use the shortcut key `Ctrl+L`. The loading menu will appear:

<p align="center">
  <img width="40%" src="https://raw.githubusercontent.com/alannaz36/ILLIXR_visualizer/main/gallery/load.png">
</p>
 
`Browse` to your cloned repository, open the `metrics` folder, and select the following for each database:

- Plugin Database: `plugin_name.sqlite`
- Switchboard Database: `switchboard_callback.sqlite`
- Threadloop Database: `threadloop_iteration.sqlite`

The data will be loaded from the databases into the Visualizer. 

<p align="center">
  <img width="75%" src="https://raw.githubusercontent.com/alannaz36/ILLIXR_visualizer/main/gallery/visualize_data.png">
</p>

The left **Plugins** window can be used to reorder the plugins by dragging a plugin to a desired location in the listing, then clicking `Reorder Plot`.

The arrows at the bottom of the window are used to page left and right through the data. 

Plugins can be toggled on and off by selecting/deselecting them in the Plugin Name legend on the right.

<p align="center">
  <img width="75%" src="https://raw.githubusercontent.com/alannaz36/ILLIXR_visualizer/main/gallery/toggle.png">
</p>

The interactive graph has additional functionalities, including zooming in on a selected region of interest.

<p align="center">
  <img width="75%" src="https://raw.githubusercontent.com/alannaz36/ILLIXR_visualizer/main/gallery/zoom.png">
</p>
