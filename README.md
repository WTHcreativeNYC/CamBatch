# CamBatch

CamBatch is a Blender extension built to take the repetitive work out of rendering still images from multiple cameras.

If your usual workflow looks like **switch camera → render → save → rename → repeat**, CamBatch tidies that up. Add the cameras you need, put them in order, choose **Final Render** or **Viewport Render**, and let the batch run.

Developed by **WTH_creative_NYC**. Maintained by **Wentao Huang**.

## Compatibility

- Blender 4.5 LTS
- Blender 5.x
- Windows, macOS, and Linux

## Features

### 📷 Lots of cameras? Add them all at once.

Select every camera you want to render and click **Add Selected Cameras**. CamBatch keeps a persistent, reorderable camera list inside your `.blend` file, so there is no need to add Camera 01, Camera 02, Camera 03... one by one.

### 👀 Click a camera. See through it.

Click any camera in the list and Blender automatically switches to that camera for a quick preview. Need a better name? Rename it directly in the list instead of hunting through the Outliner.

### 🧪 Test one before rendering the whole batch.

Use **Render Active Camera** to run a quick Final Render test for the selected camera before committing to every angle.

### ✨ Final or Viewport? Your call.

Choose **Final Render** when you want Blender's current final render settings. Choose **Viewport Render** when you want to batch-export exactly what the current 3D Viewport is showing.

### 📁 The useful output settings stay close by.

Access Blender's native output folder, image format, transparent background, resolution, and scale settings from the CamBatch panel—fewer detours through the Properties editor.

### 🏷️ File naming takes care of itself.

CamBatch combines the camera name with the render type, producing names such as:

`Camera_A_Final.png`  
`Camera_A_view.png`

The camera tells you the angle; the suffix tells you how it was rendered. Nice and tidy.

### 🛑 Existing images do not get quietly replaced.

CamBatch checks the output folder before rendering. If matching files already exist, it asks whether to overwrite them; otherwise, those files are skipped.

### 🔄 Cycles no longer looks suspiciously frozen.

During a Cycles Final Render, the progressive result appears in the **Render Result** window. At least you can see Blender working hard.

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

---

# CamBatch 中文版

CamBatch 是一款专门用来简化多相机批量渲染的 Blender 插件。

如果你的日常流程总是 **切相机 → Render → Save → 改文件名 → 再切相机 → 再来一次……**，CamBatch 就是来收拾这些重复操作的。把需要的相机加入列表、排好顺序，选择 **Final Render** 或 **Viewport Render**，然后让它们一次出完。

开发者：**WTH_creative_NYC**。维护者：**Wentao Huang**。

## 兼容性

- Blender 4.5 LTS
- Blender 5.x
- Windows、macOS 和 Linux

## 功能

### 📷 相机很多？一次全加进来。

选中所有准备出图的相机，点击 **Add Selected Cameras**，一次加入列表。CamBatch 会把可排序的相机列表保存在当前 `.blend` 文件中，不用再 Camera 01、Camera 02、Camera 03……一个个折腾。

### 👀 点一下，就看这一台。

点击列表里的相机，Blender 会自动切换到对应视角，方便立即预览。想改名字？直接在列表里重命名，不用再跑去 Outliner 里找它。

### 🧪 全部开跑之前，先试一张。

使用 **Render Active Camera** 可以先对当前相机进行一次 Final Render 测试。确认效果没问题，再放心把整批交给 CamBatch。

### ✨ Final 还是 Viewport？你来选。

想认真出图，就选择 **Final Render**，直接按照 Blender 当前的最终渲染设置输出。

只是想把现在看到的效果快速全部导出来？选择 **Viewport Render**，CamBatch 会按照当前 3D Viewport 的样子批量出图。

### 📁 常用 Output 设置，就放在手边。

可以直接在 CamBatch 面板中使用 Blender 原生的输出文件夹、图片格式、透明背景、分辨率和缩放比例设置，少在 Properties 编辑器里绕几趟路。

### 🏷️ 文件名也不用管。

CamBatch 会根据**相机名称 + 渲染类型**自动命名文件，例如：

`Camera_A_Final.png`  
`Camera_A_view.png`

相机名告诉你是哪个角度，后缀告诉你用了哪种渲染。找图轻松一点。

### 🛑 不会偷偷覆盖你的图。

CamBatch 会在渲染前检查输出文件夹。如果发现同名文件，会先询问是否覆盖；选择不覆盖时，已有文件会被跳过。

毕竟重新 Render 可以，误删上一版就不太好玩了。

### 🔄 Cycles 不再像“卡住了”。

使用 Cycles 进行 Final Render 时，可以直接在 **Render Result** 窗口中看到渐进式渲染过程。

至少你知道 Blender 还在努力。

## 安装

1. 从最新的 **GitHub Release** 下载 `cam_batch-1.0.0.zip`，不要解压。
2. 在 Blender 中打开 **Edit > Preferences > Extensions**。
3. 点击右上角菜单，选择 **Install from Disk**。
4. 选择 `cam_batch-1.0.0.zip`，并根据需要启用 **CamBatch**。
5. 打开任意 3D Viewport，按 **N** 键，在侧边栏中选择 **Batch Render** 标签页。

## 快速开始

1. 在 3D Viewport 或 Outliner 中选择一个或多个相机对象。
2. 点击 **Add Selected Cameras**。
3. 如有需要，使用箭头按钮调整相机顺序。
4. 选择 **Viewport Render** 或 **Final Render**。
5. 展开 **Output**，设置输出文件夹、图片格式、透明背景以及文件覆盖方式。
6. 展开 **Resolution**，设置 X、Y 分辨率和缩放百分比。
7. 点击 **Render Active Camera** 测试单个相机的 Final Render，或直接启动所选择的批量渲染模式。

## 输出文件名

- Viewport Render：`<CameraName>_view.<ext>`
- Final Render：`<CameraName>_Final.<ext>`

文件名中的无效字符会被安全替换。如果检测到已有同名文件，CamBatch 会询问是否覆盖；选择不覆盖时，这些文件会被跳过。

## 注意事项

- Viewport Render 必须从 3D Viewport 中的 CamBatch 面板启动。
- Viewport 输出会使用该视口当前的着色、叠加显示和显示状态。
- 取消批量渲染后，CamBatch 会在当前相机完成时停止。
- 相机引用和渲染顺序会保存在 `.blend` 文件中。

## 许可证

采用 GPL-3.0-or-later 许可证，详见 [LICENSE](LICENSE)。

## 问题反馈

报告问题时，请附上 Blender 版本、操作系统、渲染引擎、复现步骤，以及 Blender 系统控制台中显示的错误信息。
