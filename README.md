# CamBatch

CamBatch is a Blender extension that renders still images from an ordered list of cameras. It supports Final Render and the current 3D Viewport appearance, making multi-camera output and quick comparisons straightforward.

Developed by **WTH_creative_NYC**. Maintained by **Wentao Huang**.

## Compatibility

- Blender 4.5 LTS
- Blender 5.x
- Windows, macOS, and Linux

## Features

- Build and reorder a persistent camera list inside each `.blend` file.
- Add all selected cameras at once.
- Rename cameras directly in the list.
- Click a list row to preview that camera automatically.
- Render a single active camera for a quick test.
- Batch Final Render or the current Viewport appearance.
- Save files using camera and render-type names, such as `Camera_A_Final.png` and `Camera_A_view.png`.
- Use Blender's native output format, transparency, resolution, and output-folder settings.
- Detect existing output files and ask whether to overwrite them.
- Show progressive Cycles renders in a Render Result window.

## Installation

1. Download `cam_batch-1.0.0.zip` from the latest GitHub Release. Do not unzip it.
2. In Blender, open **Edit > Preferences > Extensions**.
3. Open the menu in the upper-right corner and choose **Install from Disk**.
4. Select `cam_batch-1.0.0.zip` and enable **CamBatch** if needed.
5. Open a 3D Viewport, press **N**, and select the **Batch Render** tab.

## Quick Start

1. Select one or more camera objects in the 3D Viewport or Outliner.
2. Click **Add Selected Cameras**.
3. Reorder the cameras with the arrow buttons if needed.
4. Choose **Viewport Render** or **Final Render**.
5. Expand **Output** to choose the output folder, image format, transparency, and overwrite behavior.
6. Expand **Resolution** to set X, Y, and scale percentage.
7. Click **Render Active Camera** for a Final Render test, or start the selected batch mode.

## Output Names

- Viewport Render: `<CameraName>_view.<ext>`
- Final Render: `<CameraName>_Final.<ext>`

Characters that are invalid in filenames are replaced safely. If existing files are detected, CamBatch asks whether they should be overwritten; otherwise they are skipped.

## Notes

- Viewport Render must be started from the CamBatch panel in a 3D Viewport.
- Viewport output uses that viewport's current shading, overlays, and display state.
- Cancelling a batch stops it after the current camera finishes.
- Camera references and render order are saved with the `.blend` file.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

## Issues

When reporting a problem, include your Blender version, operating system, render engine, steps to reproduce, and any error shown in Blender's system console.
