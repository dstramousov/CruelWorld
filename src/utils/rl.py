from __future__ import annotations

from typing import Any

try:
    import raylib as _rl  # type: ignore
    _BACKEND = 'raylib'
except ImportError:  # pragma: no cover
    import pyray as _rl  # type: ignore
    _BACKEND = 'pyray'


def _get(py_name: str, c_name: str | None = None) -> Any:
    if hasattr(_rl, py_name):
        return getattr(_rl, py_name)
    if c_name and hasattr(_rl, c_name):
        return getattr(_rl, c_name)
    raise AttributeError(f'raylib binding missing function: {py_name} / {c_name}')


def _normalize_color(value: Any) -> Any:
    if isinstance(value, tuple | list):
        return Color(*value)
    return value


def Color(r: int, g: int, b: int, a: int) -> Any:
    if _BACKEND == 'pyray':
        return _rl.Color(r, g, b, a)
    return _rl.ffi.new('struct Color *', [r, g, b, a])[0]


def Rectangle(x: float, y: float, width: float, height: float) -> Any:
    if _BACKEND == 'pyray':
        return _rl.Rectangle(x, y, width, height)
    return _rl.ffi.new('struct Rectangle *', [x, y, width, height])[0]


def Vector2(x: float, y: float) -> Any:
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
FLAG_VSYNC_HINT = getattr(_rl, 'FLAG_VSYNC_HINT', 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
FILTER_POINT = getattr(_rl, 'FILTER_POINT', getattr(_rl, 'TEXTURE_FILTER_POINT', 0))
FILTER_BILINEAR = getattr(_rl, 'FILTER_BILINEAR', getattr(_rl, 'TEXTURE_FILTER_BILINEAR', 1))


def set_config_flags(flags: int) -> None:
    _get('set_config_flags', 'SetConfigFlags')(flags)


def init_window(width: int, height: int, title: str) -> None:
    if _BACKEND == 'pyray':
        _get('init_window', 'InitWindow')(width, height, title)
    else:
        _get('init_window', 'InitWindow')(width, height, title.encode('utf-8'))


def set_target_fps(fps: int) -> None:
    _get('set_target_fps', 'SetTargetFPS')(fps)


def load_render_texture(width: int, height: int) -> Any:
    return _get('load_render_texture', 'LoadRenderTexture')(width, height)


def window_should_close() -> bool:
    return bool(_get('window_should_close', 'WindowShouldClose')())


def is_window_focused() -> bool:
    return bool(_get('is_window_focused', 'IsWindowFocused')())


def get_frame_time() -> float:
    return float(_get('get_frame_time', 'GetFrameTime')())


def begin_texture_mode(target: Any) -> None:
    _get('begin_texture_mode', 'BeginTextureMode')(target)


def end_texture_mode() -> None:
    _get('end_texture_mode', 'EndTextureMode')()


def begin_drawing() -> None:
    _get('begin_drawing', 'BeginDrawing')()


def clear_background(color: Any) -> None:
    _get('clear_background', 'ClearBackground')(_normalize_color(color))


def draw_texture_pro(texture: Any, source: Any, destination: Any, origin: Any, rotation: float, tint: Any) -> None:
    _get('draw_texture_pro', 'DrawTexturePro')(
        texture,
        source,
        destination,
        origin,
        rotation,
        _normalize_color(tint),
    )


def end_drawing() -> None:
    _get('end_drawing', 'EndDrawing')()


def unload_render_texture(target: Any) -> None:
    _get('unload_render_texture', 'UnloadRenderTexture')(target)


def close_window() -> None:
    _get('close_window', 'CloseWindow')()


def is_key_pressed(key: int) -> bool:
    return bool(_get('is_key_pressed', 'IsKeyPressed')(key))


def is_key_down(key: int) -> bool:
    return bool(_get('is_key_down', 'IsKeyDown')(key))


def draw_rectangle(x: int, y: int, width: int, height: int, color: Any) -> None:
    _get('draw_rectangle', 'DrawRectangle')(x, y, width, height, _normalize_color(color))


def draw_text(text: str, x: int, y: int, size: int, color: Any) -> None:
    payload = text if _BACKEND == 'pyray' else text.encode('utf-8')
    _get('draw_text', 'DrawText')(payload, x, y, size, _normalize_color(color))


def draw_line(start_x: int, start_y: int, end_x: int, end_y: int, color: Any) -> None:
    _get('draw_line', 'DrawLine')(start_x, start_y, end_x, end_y, _normalize_color(color))


def draw_circle(center_x: int, center_y: int, radius: float, color: Any) -> None:
    _get('draw_circle', 'DrawCircle')(center_x, center_y, radius, _normalize_color(color))


def load_font_ex(path: str, font_size: int, codepoints: list[int] | None = None) -> Any:
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
    _get('unload_font', 'UnloadFont')(font)


def draw_text_ex(font: Any, text: str, position: Any, font_size: float, spacing: float, tint: Any) -> None:
    payload = text if _BACKEND == 'pyray' else text.encode('utf-8')
    _get('draw_text_ex', 'DrawTextEx')(font, payload, position, font_size, spacing, _normalize_color(tint))


def load_texture(path: str) -> Any:
    if _BACKEND == 'pyray':
        return _get('load_texture', 'LoadTexture')(path)
    return _get('load_texture', 'LoadTexture')(path.encode('utf-8'))


def unload_texture(texture: Any) -> None:
    _get('unload_texture', 'UnloadTexture')(texture)


def set_texture_filter(texture: Any, filter_mode: int) -> None:
    try:
        _get('set_texture_filter', 'SetTextureFilter')(texture, filter_mode)
    except AttributeError:
        return
