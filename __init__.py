"""CamBatch for Blender 4.5 LTS and 5.x."""

import os
import re
import time
from pathlib import Path

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup, UIList


ADDON_VERSION = "1.0.0"
DEVELOPER_NAME = "WTH_creative_NYC"

IMAGE_EXTENSIONS = {
    "BMP": ".bmp",
    "IRIS": ".rgb",
    "PNG": ".png",
    "JPEG": ".jpg",
    "JPEG2000": ".jp2",
    "TARGA": ".tga",
    "TARGA_RAW": ".tga",
    "CINEON": ".cin",
    "DPX": ".dpx",
    "OPEN_EXR_MULTILAYER": ".exr",
    "OPEN_EXR": ".exr",
    "HDR": ".hdr",
    "TIFF": ".tif",
    "WEBP": ".webp",
}


_TEST_RENDER_DISPLAY_RESTORE = {}


def restore_test_render_display(scene, *_args):
    """Restore display mode after an asynchronously invoked test render."""
    original = _TEST_RENDER_DISPLAY_RESTORE.pop(scene.as_pointer(), None)
    if original is not None:
        bpy.context.preferences.view.render_display_type = original


def camera_poll(_self, obj):
    return obj is not None and obj.type == "CAMERA"


def active_camera_changed(settings, context):
    """Preview the newly selected list camera when changed from a 3D View."""
    scene = getattr(context, "scene", None)
    area = getattr(context, "area", None)
    space = getattr(context, "space_data", None)
    if scene is None or not hasattr(scene, "bcr_cameras"):
        return
    if not (0 <= settings.active_index < len(scene.bcr_cameras)):
        return
    camera = scene.bcr_cameras[settings.active_index].camera
    if not camera or camera.type != "CAMERA":
        return

    scene.camera = camera
    if area is not None and area.type == "VIEW_3D" and space is not None:
        space.region_3d.view_perspective = "CAMERA"


def safe_filename(name):
    """Return a Windows-safe filename while retaining readable Unicode."""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip().rstrip(".")
    return cleaned or "Camera"


def resolve_output_directory(scene):
    raw_path = scene.render.filepath or "//"
    resolved = Path(bpy.path.abspath(raw_path))
    # The add-on deliberately treats the native Output field as a directory.
    return resolved


def output_stem(camera_name, render_mode):
    suffix = "_view" if render_mode == "VIEWPORT" else "_Final"
    return f"{camera_name}{suffix}"


def unique_output_path(directory, camera_name, extension, overwrite, reserved):
    base = safe_filename(camera_name)
    candidate = directory / f"{base}{extension}"
    key = os.path.normcase(str(candidate))

    if overwrite and key not in reserved:
        reserved.add(key)
        return candidate

    if candidate.exists() and not overwrite:
        return None

    if key not in reserved:
        reserved.add(key)
        return candidate

    number = 2
    while True:
        candidate = directory / f"{base}_{number:03d}{extension}"
        key = os.path.normcase(str(candidate))
        if not candidate.exists() and key not in reserved:
            reserved.add(key)
            return candidate
        number += 1


class BCR_CameraItem(PropertyGroup):
    camera: PointerProperty(
        name="Camera",
        type=bpy.types.Object,
        poll=camera_poll,
    )


class BCR_Settings(PropertyGroup):
    render_mode: EnumProperty(
        name="Render Mode",
        items=(
            ("VIEWPORT", "Viewport Render", "Use the current 3D Viewport appearance"),
            ("FINAL", "Final Render", "Use the current render engine and render settings"),
        ),
        default="FINAL",
    )
    overwrite: BoolProperty(
        name="Overwrite Existing Images",
        description="Replace an existing image with the same camera name",
        default=False,
    )
    show_output: BoolProperty(
        name="Output",
        description="Show or hide output settings",
        default=True,
    )
    show_resolution: BoolProperty(
        name="Resolution",
        description="Show or hide resolution settings",
        default=True,
    )
    active_index: IntProperty(default=0, min=0, update=active_camera_changed)
    progress_current: IntProperty(default=0, min=0)
    progress_total: IntProperty(default=0, min=0)
    is_rendering: BoolProperty(default=False)
    cancel_requested: BoolProperty(default=False)


class BCR_UL_cameras(UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index=0):
        camera = item.camera
        if camera and camera.type == "CAMERA":
            # Binding the row to Object.name keeps it synchronized and makes
            # the name editable inline (double-click, then type).
            layout.prop(camera, "name", text="", emboss=False, icon="CAMERA_DATA")
        else:
            layout.label(text="Missing Camera", icon="ERROR")


class BCR_OT_add_selected(Operator):
    bl_idname = "bcr.add_selected"
    bl_label = "Add Selected Cameras"
    bl_description = "Add all selected camera objects to the render list"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        existing = {item.camera for item in scene.bcr_cameras if item.camera}
        cameras = [obj for obj in context.selected_objects if obj.type == "CAMERA"]
        added = 0
        for camera in cameras:
            if camera in existing:
                continue
            item = scene.bcr_cameras.add()
            item.camera = camera
            existing.add(camera)
            added += 1

        if added:
            scene.bcr_settings.active_index = len(scene.bcr_cameras) - 1
            self.report({"INFO"}, f"Added {added} camera(s)")
            return {"FINISHED"}

        self.report({"WARNING"}, "No new selected cameras to add")
        return {"CANCELLED"}


class BCR_OT_remove_camera(Operator):
    bl_idname = "bcr.remove_camera"
    bl_label = "Remove Camera"
    bl_description = "Remove the active entry without deleting the camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cameras = context.scene.bcr_cameras
        settings = context.scene.bcr_settings
        if not cameras:
            return {"CANCELLED"}
        index = min(settings.active_index, len(cameras) - 1)
        cameras.remove(index)
        settings.active_index = min(index, max(0, len(cameras) - 1))
        return {"FINISHED"}


class BCR_OT_move_camera(Operator):
    bl_idname = "bcr.move_camera"
    bl_label = "Move Camera"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    def execute(self, context):
        cameras = context.scene.bcr_cameras
        settings = context.scene.bcr_settings
        index = settings.active_index
        target = index - 1 if self.direction == "UP" else index + 1
        if 0 <= index < len(cameras) and 0 <= target < len(cameras):
            cameras.move(index, target)
            settings.active_index = target
        return {"FINISHED"}


class BCR_OT_clear_cameras(Operator):
    bl_idname = "bcr.clear_cameras"
    bl_label = "Clear Camera List"
    bl_description = "Remove all entries without deleting camera objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.bcr_cameras.clear()
        context.scene.bcr_settings.active_index = 0
        return {"FINISHED"}


class BCR_OT_select_camera(Operator):
    bl_idname = "bcr.select_camera"
    bl_label = "Select Active Camera"
    bl_description = "Select the active list camera in the scene"

    def execute(self, context):
        scene = context.scene
        index = scene.bcr_settings.active_index
        if not (0 <= index < len(scene.bcr_cameras)):
            return {"CANCELLED"}
        camera = scene.bcr_cameras[index].camera
        if not camera:
            self.report({"ERROR"}, "The camera no longer exists")
            return {"CANCELLED"}
        for obj in context.selected_objects:
            obj.select_set(False)
        camera.select_set(True)
        context.view_layer.objects.active = camera
        return {"FINISHED"}


class BCR_OT_view_camera(Operator):
    bl_idname = "bcr.view_camera"
    bl_label = "Toggle Camera View"
    bl_description = "Enter the active camera view or return to Perspective View"

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == "VIEW_3D"

    def execute(self, context):
        scene = context.scene
        region_3d = context.space_data.region_3d
        if region_3d.view_perspective == "CAMERA":
            region_3d.view_perspective = "PERSP"
            return {"FINISHED"}

        index = scene.bcr_settings.active_index
        if not (0 <= index < len(scene.bcr_cameras)):
            self.report({"ERROR"}, "Select a camera in the list")
            return {"CANCELLED"}
        camera = scene.bcr_cameras[index].camera
        if not camera or camera.type != "CAMERA":
            self.report({"ERROR"}, "The camera no longer exists")
            return {"CANCELLED"}

        scene.camera = camera
        for obj in context.selected_objects:
            obj.select_set(False)
        camera.select_set(True)
        context.view_layer.objects.active = camera
        region_3d.view_perspective = "CAMERA"
        return {"FINISHED"}


class BCR_OT_cancel_render(Operator):
    bl_idname = "bcr.cancel_render"
    bl_label = "Cancel After Current Camera"
    bl_description = "Stop the batch after the current camera finishes"

    def execute(self, context):
        context.scene.bcr_settings.cancel_requested = True
        self.report({"INFO"}, "The batch will stop after the current camera")
        return {"FINISHED"}


class BCR_OT_render_active_camera(Operator):
    bl_idname = "bcr.render_active_camera"
    bl_label = "Render Active Camera"
    bl_description = "Run one Final Render from the active camera in the list without saving it"

    @classmethod
    def poll(cls, context):
        return not context.scene.bcr_settings.is_rendering

    def execute(self, context):
        scene = context.scene
        index = scene.bcr_settings.active_index
        if not (0 <= index < len(scene.bcr_cameras)):
            self.report({"ERROR"}, "Select a camera in the list")
            return {"CANCELLED"}
        camera = scene.bcr_cameras[index].camera
        if not camera or camera.type != "CAMERA":
            self.report({"ERROR"}, "The camera no longer exists")
            return {"CANCELLED"}

        scene.camera = camera
        if scene.render.engine == "CYCLES":
            key = scene.as_pointer()
            render_view = context.preferences.view
            _TEST_RENDER_DISPLAY_RESTORE.setdefault(key, render_view.render_display_type)
            render_view.render_display_type = "WINDOW"
        result = bpy.ops.render.render("INVOKE_DEFAULT")
        if "CANCELLED" in result:
            restore_test_render_display(scene)
            self.report({"ERROR"}, "The test render could not be started")
            return {"CANCELLED"}
        return {"FINISHED"}


class BCR_OT_batch_render(Operator):
    bl_idname = "bcr.batch_render"
    bl_label = "Start Batch Render"
    bl_description = "Render one still image from every camera in the list"

    _timer = None
    _cameras = None
    _index = 0
    _reserved_paths = None
    _original_camera = None
    _original_filepath = None
    _original_use_extension = None
    _original_display_mode = None
    _output_directory = None
    _extension = None
    _started_at = 0.0
    _failures = None
    _viewport_area = None
    _viewport_region = None
    _viewport_space = None
    _original_view_perspective = None
    _collision_names = None
    _waiting_for_render = False
    _render_job_seen = False
    _render_invoked_at = 0.0

    overwrite_existing: BoolProperty(
        name="Overwrite existing images",
        description="Replace the existing images listed above; when disabled they are skipped",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return not context.scene.bcr_settings.is_rendering

    @staticmethod
    def _valid_cameras(scene):
        cameras = []
        seen = set()
        for item in scene.bcr_cameras:
            camera = item.camera
            if camera and camera.type == "CAMERA" and camera.as_pointer() not in seen:
                cameras.append(camera)
                seen.add(camera.as_pointer())
        return cameras

    def invoke(self, context, _event):
        scene = context.scene
        settings = scene.bcr_settings
        cameras = self._valid_cameras(scene)
        extension = IMAGE_EXTENSIONS.get(scene.render.image_settings.file_format)
        if cameras and extension:
            directory = resolve_output_directory(scene)
            collisions = []
            names_seen = set()
            for camera in cameras:
                stem = output_stem(camera.name, settings.render_mode)
                output_name = f"{safe_filename(stem)}{extension}"
                key = os.path.normcase(output_name)
                if (directory / output_name).exists() or key in names_seen:
                    collisions.append(output_name)
                names_seen.add(key)
            if collisions:
                self._collision_names = collisions
                self.overwrite_existing = settings.overwrite
                return context.window_manager.invoke_props_dialog(self, width=440)
        return self._start(context)

    def draw(self, _context):
        layout = self.layout
        layout.label(text="Existing or duplicate output names were detected:", icon="ERROR")
        names = self._collision_names or []
        for name in names[:8]:
            layout.label(text=name, icon="IMAGE_DATA")
        if len(names) > 8:
            layout.label(text=f"...and {len(names) - 8} more")
        layout.separator()
        layout.prop(self, "overwrite_existing")
        layout.label(text="Unchecked files will be skipped.", icon="INFO")

    def execute(self, context):
        context.scene.bcr_settings.overwrite = self.overwrite_existing
        return self._start(context)

    def _start(self, context):
        scene = context.scene
        settings = scene.bcr_settings
        cameras = self._valid_cameras(scene)

        if not cameras:
            self.report({"ERROR"}, "Add at least one valid camera to the list")
            return {"CANCELLED"}

        file_format = scene.render.image_settings.file_format
        extension = IMAGE_EXTENSIONS.get(file_format)
        if not extension:
            self.report({"ERROR"}, f"{file_format} is not supported for still-image batches")
            return {"CANCELLED"}

        if settings.render_mode == "VIEWPORT":
            if context.area is None or context.area.type != "VIEW_3D":
                self.report({"ERROR"}, "Start Viewport Render from the CamBatch panel in a 3D Viewport")
                return {"CANCELLED"}
            self._viewport_area = context.area
            self._viewport_space = context.space_data
            self._viewport_region = next((region for region in context.area.regions if region.type == "WINDOW"), None)
            if not self._viewport_region:
                self.report({"ERROR"}, "No usable 3D Viewport region was found")
                return {"CANCELLED"}
            self._original_view_perspective = self._viewport_space.region_3d.view_perspective

        try:
            output_directory = resolve_output_directory(scene)
            output_directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.report({"ERROR"}, f"Cannot create output folder: {exc}")
            return {"CANCELLED"}

        self._cameras = cameras
        self._index = 0
        self._reserved_paths = set()
        self._original_camera = scene.camera
        self._original_filepath = scene.render.filepath
        self._original_use_extension = scene.render.use_file_extension
        self._original_display_mode = context.preferences.view.render_display_type
        self._output_directory = output_directory
        self._extension = extension
        self._started_at = time.monotonic()
        self._failures = []
        self._waiting_for_render = False
        self._render_job_seen = False
        self._render_invoked_at = 0.0

        settings.progress_current = 0
        settings.progress_total = len(cameras)
        settings.cancel_requested = False
        settings.is_rendering = True

        # Cycles progressively updates this temporary render window so the
        # user can inspect convergence while the batch is running.
        if settings.render_mode == "FINAL" and scene.render.engine == "CYCLES":
            context.preferences.view.render_display_type = "WINDOW"

        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC":
            context.scene.bcr_settings.cancel_requested = True

        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        settings = context.scene.bcr_settings

        # Final renders are invoked asynchronously so Blender can create and
        # continuously update its Render Result window. Wait for that job to
        # finish before advancing to the next camera.
        if self._waiting_for_render:
            if bpy.app.is_job_running("RENDER"):
                self._render_job_seen = True
                return {"RUNNING_MODAL"}
            if not self._render_job_seen and time.monotonic() - self._render_invoked_at < 1.0:
                return {"RUNNING_MODAL"}
            self._waiting_for_render = False
            self._render_job_seen = False
            self._advance(context)
            return {"RUNNING_MODAL"}

        if settings.cancel_requested or self._index >= len(self._cameras):
            cancelled = settings.cancel_requested
            self._finish(context)
            if cancelled:
                self.report({"WARNING"}, f"Batch cancelled after {self._index} image(s)")
            else:
                elapsed = time.monotonic() - self._started_at
                if self._failures:
                    self.report({"WARNING"}, f"Finished with {len(self._failures)} failure(s) in {elapsed:.1f}s")
                else:
                    self.report({"INFO"}, f"Rendered {self._index} image(s) in {elapsed:.1f}s")
            return {"FINISHED"}

        camera = self._cameras[self._index]
        try:
            completed_now = self._render_camera(context, camera)
        except Exception as exc:  # Keep the remaining cameras renderable.
            self._failures.append((camera.name, str(exc)))
            print(f"CamBatch: failed {camera.name}: {exc}")
            completed_now = True

        if completed_now:
            self._advance(context)
        return {"RUNNING_MODAL"}

    def _advance(self, context):
        self._index += 1
        context.scene.bcr_settings.progress_current = self._index
        if context.area:
            context.area.tag_redraw()

    def _render_camera(self, context, camera):
        scene = context.scene
        settings = scene.bcr_settings
        output_path = unique_output_path(
            self._output_directory,
            output_stem(camera.name, settings.render_mode),
            self._extension,
            settings.overwrite,
            self._reserved_paths,
        )
        if output_path is None:
            print(f"CamBatch: skipped existing image for {camera.name}")
            return True
        scene.camera = camera
        scene.render.filepath = str(output_path.with_suffix(""))
        scene.render.use_file_extension = True

        if settings.render_mode == "FINAL":
            result = bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
            if "CANCELLED" in result:
                raise RuntimeError("Blender could not start the render job")
            self._waiting_for_render = True
            self._render_job_seen = bpy.app.is_job_running("RENDER")
            self._render_invoked_at = time.monotonic()
            return False

        self._viewport_space.region_3d.view_perspective = "CAMERA"
        with context.temp_override(
            area=self._viewport_area,
            region=self._viewport_region,
            space_data=self._viewport_space,
        ):
            bpy.ops.render.opengl(write_still=True, view_context=True)
        return True

    def _finish(self, context):
        scene = context.scene
        settings = scene.bcr_settings
        scene.camera = self._original_camera
        scene.render.filepath = self._original_filepath
        scene.render.use_file_extension = self._original_use_extension
        if self._original_display_mode is not None:
            context.preferences.view.render_display_type = self._original_display_mode
        if self._viewport_space and self._original_view_perspective:
            self._viewport_space.region_3d.view_perspective = self._original_view_perspective
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        settings.is_rendering = False
        settings.cancel_requested = False

    def cancel(self, context):
        self._finish(context)


class BCR_PT_main(Panel):
    bl_label = "CamBatch"
    bl_idname = "BCR_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Batch Render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.bcr_settings

        row = layout.row()
        row.template_list(
            "BCR_UL_cameras",
            "",
            scene,
            "bcr_cameras",
            settings,
            "active_index",
            rows=4,
        )
        buttons = row.column(align=True)
        buttons.operator("bcr.add_selected", text="", icon="ADD")
        buttons.operator("bcr.remove_camera", text="", icon="REMOVE")
        buttons.separator()
        up = buttons.operator("bcr.move_camera", text="", icon="TRIA_UP")
        up.direction = "UP"
        down = buttons.operator("bcr.move_camera", text="", icon="TRIA_DOWN")
        down.direction = "DOWN"

        row = layout.row(align=True)
        row.operator("bcr.add_selected", icon="CAMERA_DATA")
        row.operator("bcr.select_camera", text="Select Active")
        in_camera_view = (
            context.area is not None
            and context.area.type == "VIEW_3D"
            and context.space_data.region_3d.view_perspective == "CAMERA"
        )
        if in_camera_view:
            layout.operator("bcr.view_camera", text="Exit Camera View", icon="LOOP_BACK")
        else:
            layout.operator("bcr.view_camera", text="View From Camera", icon="HIDE_OFF")
        layout.operator("bcr.clear_cameras", icon="TRASH")

        layout.separator()
        layout.prop(settings, "render_mode", expand=True)

        output = layout.box()
        header = output.row()
        header.prop(
            settings,
            "show_output",
            text="Output",
            icon="TRIA_DOWN" if settings.show_output else "TRIA_RIGHT",
            emboss=False,
        )
        if settings.show_output:
            output.prop(scene.render, "filepath", text="Folder")
            output.prop(scene.render.image_settings, "file_format", text="Format")
            self._draw_format_options(output, scene.render.image_settings)
            output.prop(scene.render, "film_transparent", text="Transparent Background")
            output.prop(settings, "overwrite")

        resolution = layout.box()
        header = resolution.row()
        header.prop(
            settings,
            "show_resolution",
            text="Resolution",
            icon="TRIA_DOWN" if settings.show_resolution else "TRIA_RIGHT",
            emboss=False,
        )
        if settings.show_resolution:
            row = resolution.row(align=True)
            row.prop(scene.render, "resolution_x", text="X")
            row.prop(scene.render, "resolution_y", text="Y")
            resolution.prop(scene.render, "resolution_percentage", text="Scale")

        layout.separator()
        if settings.is_rendering:
            current = min(settings.progress_current, settings.progress_total)
            factor = current / settings.progress_total if settings.progress_total else 0.0
            layout.progress(factor=factor, type="BAR", text=f"Rendering {current} / {settings.progress_total}")
            layout.operator("bcr.cancel_render", icon="CANCEL")
        else:
            button_text = "Start Viewport Batch" if settings.render_mode == "VIEWPORT" else "Start Final Batch"
            if settings.render_mode == "FINAL":
                layout.operator("bcr.render_active_camera", text="Render Active Camera", icon="RENDER_STILL")
            layout.operator("bcr.batch_render", text=button_text, icon="RENDER_STILL")

        layout.separator()
        footer = layout.row()
        footer.alignment = "CENTER"
        footer.scale_y = 0.8
        footer.label(text=f"Developed by {DEVELOPER_NAME}  •  v{ADDON_VERSION}")

    @staticmethod
    def _draw_format_options(layout, image_settings):
        file_format = image_settings.file_format
        if file_format in {"PNG", "JPEG", "JPEG2000", "TARGA", "TARGA_RAW", "TIFF", "OPEN_EXR", "OPEN_EXR_MULTILAYER", "WEBP"}:
            layout.prop(image_settings, "color_mode", text="Color")
        if file_format in {"PNG", "TIFF", "OPEN_EXR", "OPEN_EXR_MULTILAYER"}:
            layout.prop(image_settings, "color_depth", text="Depth")
        if file_format == "PNG":
            layout.prop(image_settings, "compression")
        elif file_format == "JPEG":
            layout.prop(image_settings, "quality")
        elif file_format == "WEBP":
            layout.prop(image_settings, "quality")
        elif file_format in {"OPEN_EXR", "OPEN_EXR_MULTILAYER"}:
            layout.prop(image_settings, "exr_codec", text="Codec")
        elif file_format == "TIFF":
            layout.prop(image_settings, "tiff_codec", text="Compression")


CLASSES = (
    BCR_CameraItem,
    BCR_Settings,
    BCR_UL_cameras,
    BCR_OT_add_selected,
    BCR_OT_remove_camera,
    BCR_OT_move_camera,
    BCR_OT_clear_cameras,
    BCR_OT_select_camera,
    BCR_OT_view_camera,
    BCR_OT_cancel_render,
    BCR_OT_render_active_camera,
    BCR_OT_batch_render,
    BCR_PT_main,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bcr_cameras = CollectionProperty(type=BCR_CameraItem)
    bpy.types.Scene.bcr_settings = PointerProperty(type=BCR_Settings)
    if restore_test_render_display not in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.append(restore_test_render_display)
    if restore_test_render_display not in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.append(restore_test_render_display)


def unregister():
    if restore_test_render_display in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(restore_test_render_display)
    if restore_test_render_display in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(restore_test_render_display)
    _TEST_RENDER_DISPLAY_RESTORE.clear()
    del bpy.types.Scene.bcr_settings
    del bpy.types.Scene.bcr_cameras
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
