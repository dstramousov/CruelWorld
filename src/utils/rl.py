"""Rl module for shared utility functions and wrappers."""

from __future__ import annotations

from typing import Any

try:
    import raylib as _rl  # type: ignore
    _BACKEND = 'raylib'
except ImportError:  # pragma: no cover
    import pyray as _rl  # type: ignore
    _BACKEND = 'pyray'


def _get(py_name: str, c_name: str | None = None) -> Any:
    """Execute get.
    
    Args:
        py_name: Input value used by this operation.
        c_name: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if hasattr(_rl, py_name):
        return getattr(_rl, py_name)
    if c_name and hasattr(_rl, c_name):
        return getattr(_rl, c_name)
    raise AttributeError(f'raylib binding missing function: {py_name} / {c_name}')


def _normalize_color(value: Any) -> Any:
    """Execute normalize color.
    
    Args:
        value: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if isinstance(value, tuple | list):
        return Color(*value)
    return value


def Color(r: int, g: int, b: int, a: int) -> Any:
    """Execute Color.
    
    Args:
        r: Input value used by this operation.
        g: Input value used by this operation.
        b: Input value used by this operation.
        a: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if _BACKEND == 'pyray':
        return _rl.Color(r, g, b, a)
    return _rl.ffi.new('struct Color *', [r, g, b, a])[0]


def Rectangle(x: float, y: float, width: float, height: float) -> Any:
    """Execute Rectangle.
    
    Args:
        x: Input value used by this operation.
        y: Input value used by this operation.
        width: Input value used by this operation.
        height: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if _BACKEND == 'pyray':
        return _rl.Rectangle(x, y, width, height)
    return _rl.ffi.new('struct Rectangle *', [x, y, width, height])[0]


def Vector2(x: float, y: float) -> Any:
    """Execute Vector2.
    
    Args:
        x: Input value used by this operation.
        y: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if _BACKEND == 'pyray':
        return _rl.Vector2(x, y)
    return _rl.ffi.new('struct Vector2 *', [x, y])[0]


KEY_F1 = getattr(_rl, 'KEY_F1')
KEY_LEFT_SHIFT = getattr(_rl, 'KEY_LEFT_SHIFT')
KEY_RIGHT_SHIFT = getattr(_rl, 'KEY_RIGHT_SHIFT')
KEY_D = getattr(_rl, 'KEY_D')
KEY_Q = getattr(_rl, 'KEY_Q')
KEY_E = getattr(_rl, 'KEY_E')
KEY_A = getattr(_rl, 'KEY_A')
KEY_F = getattr(_rl, 'KEY_F')
KEY_LEFT = getattr(_rl, 'KEY_LEFT')
KEY_RIGHT = getattr(_rl, 'KEY_RIGHT')
KEY_SPACE = getattr(_rl, 'KEY_SPACE')
KEY_W = getattr(_rl, 'KEY_W')
KEY_UP = getattr(_rl, 'KEY_UP')
KEY_DOWN = getattr(_rl, 'KEY_DOWN')
KEY_S = getattr(_rl, 'KEY_S')
KEY_J = getattr(_rl, 'KEY_J')
KEY_L = getattr(_rl, 'KEY_L')
KEY_TAB = getattr(_rl, 'KEY_TAB')
KEY_ESCAPE = getattr(_rl, 'KEY_ESCAPE')
KEY_ENTER = getattr(_rl, 'KEY_ENTER')
KEY_BACKSPACE = getattr(_rl, 'KEY_BACKSPACE')
FLAG_VSYNC_HINT = getattr(_rl, 'FLAG_VSYNC_HINT', 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
FILTER_POINT = getattr(_rl, 'FILTER_POINT', getattr(_rl, 'TEXTURE_FILTER_POINT', 0))
FILTER_BILINEAR = getattr(_rl, 'FILTER_BILINEAR', getattr(_rl, 'TEXTURE_FILTER_BILINEAR', 1))


def set_config_flags(flags: int) -> None:
    """Execute set config flags.
    
    Args:
        flags: Input value used by this operation.
    """
    _get('set_config_flags', 'SetConfigFlags')(flags)


def init_window(width: int, height: int, title: str) -> None:
    """Execute init window.
    
    Args:
        width: Input value used by this operation.
        height: Input value used by this operation.
        title: Input value used by this operation.
    """
    if _BACKEND == 'pyray':
        _get('init_window', 'InitWindow')(width, height, title)
    else:
        _get('init_window', 'InitWindow')(width, height, title.encode('utf-8'))


def set_target_fps(fps: int) -> None:
    """Execute set target fps.
    
    Args:
        fps: Input value used by this operation.
    """
    _get('set_target_fps', 'SetTargetFPS')(fps)


def load_render_texture(width: int, height: int) -> Any:
    """Load render texture.
    
    Args:
        width: Input value used by this operation.
        height: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    return _get('load_render_texture', 'LoadRenderTexture')(width, height)


def window_should_close() -> bool:
    """Execute window should close.
    
    Returns:
        Result produced by this operation.
    """
    return bool(_get('window_should_close', 'WindowShouldClose')())


def is_window_focused() -> bool:
    """Return whether window focused is true.
    
    Returns:
        Result produced by this operation.
    """
    return bool(_get('is_window_focused', 'IsWindowFocused')())


def get_frame_time() -> float:
    """Return frame time.
    
    Returns:
        Result produced by this operation.
    """
    return float(_get('get_frame_time', 'GetFrameTime')())


def get_fps() -> int:
    """Return fps.
    
    Returns:
        Result produced by this operation.
    """
    return int(_get('get_fps', 'GetFPS')())


def begin_texture_mode(target: Any) -> None:
    """Execute begin texture mode.
    
    Args:
        target: Input value used by this operation.
    """
    _get('begin_texture_mode', 'BeginTextureMode')(target)


def end_texture_mode() -> None:
    """Execute end texture mode.
    """
    _get('end_texture_mode', 'EndTextureMode')()


def begin_drawing() -> None:
    """Execute begin drawing.
    """
    _get('begin_drawing', 'BeginDrawing')()


def clear_background(color: Any) -> None:
    """Execute clear background.
    
    Args:
        color: Input value used by this operation.
    """
    _get('clear_background', 'ClearBackground')(_normalize_color(color))


def draw_texture_pro(texture: Any, source: Any, destination: Any, origin: Any, rotation: float, tint: Any) -> None:
    """Draw draw texture pro.
    
    Args:
        texture: Input value used by this operation.
        source: Input value used by this operation.
        destination: Input value used by this operation.
        origin: Input value used by this operation.
        rotation: Input value used by this operation.
        tint: Input value used by this operation.
    """
    _get('draw_texture_pro', 'DrawTexturePro')(
        texture,
        source,
        destination,
        origin,
        rotation,
        _normalize_color(tint),
    )


def end_drawing() -> None:
    """Execute end drawing.
    """
    _get('end_drawing', 'EndDrawing')()


def unload_render_texture(target: Any) -> None:
    """Execute unload render texture.
    
    Args:
        target: Input value used by this operation.
    """
    _get('unload_render_texture', 'UnloadRenderTexture')(target)


def close_window() -> None:
    """Execute close window.
    """
    _get('close_window', 'CloseWindow')()


def is_key_pressed(key: int) -> bool:
    """Return whether key pressed is true.
    
    Args:
        key: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    return bool(_get('is_key_pressed', 'IsKeyPressed')(key))


def get_char_pressed() -> int:
    """Return the next UTF-32 character code pressed this frame.

    Returns:
        Pressed character code, or 0 when the queue is empty.
    """
    return int(_get('get_char_pressed', 'GetCharPressed')())


def is_key_down(key: int) -> bool:
    """Return whether key down is true.
    
    Args:
        key: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    return bool(_get('is_key_down', 'IsKeyDown')(key))


def draw_rectangle(x: int | float, y: int | float, width: int | float, height: int | float, color: Any) -> None:
    """Draw a filled rectangle using integer pixel coordinates.

    Raylib DrawRectangle requires integer coordinates. Some UI layout
    calculations may produce floats because text measurement can return
    sub-pixel widths, so this wrapper normalizes values defensively.
    """
    _get('draw_rectangle', 'DrawRectangle')(
        int(round(x)),
        int(round(y)),
        int(round(width)),
        int(round(height)),
        _normalize_color(color),
    )


def draw_text(text: str, x: int, y: int, size: int, color: Any) -> None:
    """Draw draw text.
    
    Args:
        text: Input value used by this operation.
        x: Input value used by this operation.
        y: Input value used by this operation.
        size: Input value used by this operation.
        color: Input value used by this operation.
    """
    payload = text if _BACKEND == 'pyray' else text.encode('utf-8')
    _get('draw_text', 'DrawText')(payload, x, y, size, _normalize_color(color))


def draw_line(start_x: int, start_y: int, end_x: int, end_y: int, color: Any) -> None:
    """Draw draw line.
    
    Args:
        start_x: Input value used by this operation.
        start_y: Input value used by this operation.
        end_x: Input value used by this operation.
        end_y: Input value used by this operation.
        color: Input value used by this operation.
    """
    _get('draw_line', 'DrawLine')(start_x, start_y, end_x, end_y, _normalize_color(color))


def draw_circle(center_x: int, center_y: int, radius: float, color: Any) -> None:
    """Draw draw circle.
    
    Args:
        center_x: Input value used by this operation.
        center_y: Input value used by this operation.
        radius: Input value used by this operation.
        color: Input value used by this operation.
    """
    _get('draw_circle', 'DrawCircle')(center_x, center_y, radius, _normalize_color(color))



def draw_triangle(
    x1: int | float,
    y1: int | float,
    x2: int | float,
    y2: int | float,
    x3: int | float,
    y3: int | float,
    color: Any,
) -> None:
    """Draw a filled triangle using Vector2 points.

    Args:
        x1: First point X coordinate.
        y1: First point Y coordinate.
        x2: Second point X coordinate.
        y2: Second point Y coordinate.
        x3: Third point X coordinate.
        y3: Third point Y coordinate.
        color: Fill color.
    """
    _get('draw_triangle', 'DrawTriangle')(
        Vector2(float(x1), float(y1)),
        Vector2(float(x2), float(y2)),
        Vector2(float(x3), float(y3)),
        _normalize_color(color),
    )

def load_font_ex(path: str, font_size: int, codepoints: list[int] | None = None) -> Any:
    """Load font ex.
    
    Args:
        path: Input value used by this operation.
        font_size: Input value used by this operation.
        codepoints: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if _BACKEND == 'raylib':
        encoded_path = path.encode('utf-8')
        if codepoints:
            codepoint_data = _rl.ffi.new('int[]', codepoints)
            return _get('load_font_ex', 'LoadFontEx')(encoded_path, font_size, codepoint_data, len(codepoints))
        return _get('load_font_ex', 'LoadFontEx')(encoded_path, font_size, _rl.ffi.NULL, 0)
    if codepoints:
        return _get('load_font_ex', 'LoadFontEx')(path, font_size, None, 0)
    return _get('load_font_ex', 'LoadFontEx')(path, font_size, None, 0)


def unload_font(font: Any) -> None:
    """Execute unload font.
    
    Args:
        font: Input value used by this operation.
    """
    _get('unload_font', 'UnloadFont')(font)


def draw_text_ex(font: Any, text: str, position: Any, font_size: float, spacing: float, tint: Any) -> None:
    """Draw draw text ex.
    
    Args:
        font: Input value used by this operation.
        text: Input value used by this operation.
        position: Input value used by this operation.
        font_size: Input value used by this operation.
        spacing: Input value used by this operation.
        tint: Input value used by this operation.
    """
    payload = text if _BACKEND == 'pyray' else text.encode('utf-8')
    _get('draw_text_ex', 'DrawTextEx')(font, payload, position, font_size, spacing, _normalize_color(tint))


def measure_text(text: str, size: int) -> int:
    """Execute measure text.
    
    Args:
        text: Input value used by this operation.
        size: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    payload = text if _BACKEND == 'pyray' else text.encode('utf-8')
    return int(_get('measure_text', 'MeasureText')(payload, size))


def measure_text_ex(font: Any, text: str, font_size: float, spacing: float) -> Any:
    """Execute measure text ex.
    
    Args:
        font: Input value used by this operation.
        text: Input value used by this operation.
        font_size: Input value used by this operation.
        spacing: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    payload = text if _BACKEND == 'pyray' else text.encode('utf-8')
    return _get('measure_text_ex', 'MeasureTextEx')(font, payload, font_size, spacing)


def load_texture(path: str) -> Any:
    """Load texture.
    
    Args:
        path: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    if _BACKEND == 'pyray':
        return _get('load_texture', 'LoadTexture')(path)
    return _get('load_texture', 'LoadTexture')(path.encode('utf-8'))


def unload_texture(texture: Any) -> None:
    """Execute unload texture.
    
    Args:
        texture: Input value used by this operation.
    """
    _get('unload_texture', 'UnloadTexture')(texture)


def set_texture_filter(texture: Any, filter_mode: int) -> None:
    """Execute set texture filter.
    
    Args:
        texture: Input value used by this operation.
        filter_mode: Input value used by this operation.
    """
    try:
        _get('set_texture_filter', 'SetTextureFilter')(texture, filter_mode)
    except AttributeError:
        return

MOUSE_BUTTON_LEFT = getattr(_rl, 'MOUSE_BUTTON_LEFT', getattr(_rl, 'MOUSE_LEFT_BUTTON', 0))


def set_exit_key(key: int) -> None:
    """Execute set exit key.
    
    Args:
        key: Input value used by this operation.
    """
    try:
        _get('set_exit_key', 'SetExitKey')(key)
    except AttributeError:
        return


def get_mouse_x() -> int:
    """Return mouse x.
    
    Returns:
        Result produced by this operation.
    """
    return int(_get('get_mouse_x', 'GetMouseX')())


def get_mouse_y() -> int:
    """Return mouse y.
    
    Returns:
        Result produced by this operation.
    """
    return int(_get('get_mouse_y', 'GetMouseY')())


def is_mouse_button_pressed(button: int) -> bool:
    """Return whether mouse button pressed is true.
    
    Args:
        button: Input value used by this operation.
    
    Returns:
        Result produced by this operation.
    """
    return bool(_get('is_mouse_button_pressed', 'IsMouseButtonPressed')(button))
