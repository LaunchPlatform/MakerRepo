import asyncio
import json
import pathlib

import pytest
import pytest_asyncio
import websockets
from click.testing import CliRunner
from pytest import MonkeyPatch

from .helper import switch_cwd
from mr.cmds.main import cli


DEFAULT_MOCK_CONFIG = {
    "ambient_intensity": 1.0,
    "angular_tolerance": 0.2,
    "axes": False,
    "axes0": False,
    "black_edges": False,
    "center_grid": False,
    "collapse": "R",
    "control": "trackball",
    "debug": False,
    "default_color": "#e8b024",
    "default_edgecolor": "#808080",
    "default_facecolor": "Violet",
    "default_opacity": 0.5,
    "default_thickedgecolor": "MediumOrchid",
    "default_vertexcolor": "MediumOrchid",
    "deviation": 0.1,
    "direct_intensity": 1.1,
    "explode": False,
    "grid": [False, False, False],
    "grid_font_size": 12,
    "metalness": 0.3,
    "modifier_keys": {
        "shift": "shiftKey",
        "ctrl": "ctrlKey",
        "meta": "metaKey",
        "alt": "altKey",
    },
    "new_tree_behavior": True,
    "glass": True,
    "tools": True,
    "pan_speed": 0.5,
    "ortho": True,
    "reset_camera": "RESET",
    "rotate_speed": 1.0,
    "roughness": 0.65,
    "theme": "browser",
    "ticks": 5,
    "transparent": False,
    "tree_width": 240,
    "up": "Z",
    "zoom_speed": 0.5,
    "_splash": True,
}
DEFAULT_MOCK_STATUS = {
    "ambient_intensity": 1,
    "states": {"/Group/Solid": [1, 1]},
    "direct_intensity": 1.1,
    "clip_slider_0": 40,
    "clip_slider_1": 40,
    "clip_slider_2": 40,
    "tab": "tree",
    "target": [10.4019, 0.4274, -24.7534],
    "target0": [10.4019, 0.4274, -24.7534],
    "position": [101.36996653681135, -93.26906574513457, -1.8075756537109555],
    "quaternion": [0.5963, 0.2408, 0.2863, 0.7099],
    "zoom": 0.9999999999999998,
}


class MockMsgHandler:
    def __init__(self, config: dict | None = None, status: dict | None = None):
        self.config = config or DEFAULT_MOCK_CONFIG
        self.status = status or DEFAULT_MOCK_STATUS
        self.data_msgs = []
        self.backend_msgs = []

    async def __call__(self, websocket: websockets.WebSocketServerProtocol, path: str):
        async for data in websocket:
            msg_type = data[:1]
            payload = data[2:]
            match msg_type:
                # command
                case b"C":
                    cmd = json.loads(payload)
                    match cmd:
                        case "status":
                            await websocket.send(json.dumps(self.status))
                        case "config":
                            await websocket.send(json.dumps(self.config))
                case b"D":
                    self.data_msgs.append(payload)
                case b"B":
                    self.backend_msgs.append(payload)


@pytest.fixture
def msg_handler() -> MockMsgHandler:
    return MockMsgHandler()


@pytest_asyncio.fixture
async def ws_server(msg_handler: MockMsgHandler, unused_tcp_port: int):
    server = await websockets.serve(msg_handler, "localhost", unused_tcp_port)
    try:
        yield server
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "module",
    [
        "examples/main.py",
        "examples.main",
    ],
)
async def test_view(
    monkeypatch: MonkeyPatch,
    cli_runner: CliRunner,
    fixtures_folder: pathlib.Path,
    module: str,
    unused_tcp_port: int,
    ws_server: websockets.WebSocketServer,
    msg_handler: MockMsgHandler,
):
    monkeypatch.syspath_prepend(fixtures_folder)

    def operate():
        with switch_cwd(fixtures_folder):
            result = cli_runner.invoke(
                cli,
                ["artifacts", "view", module, "main", "-p", unused_tcp_port],
                catch_exceptions=False,
            )
        assert result.exit_code == 0

    await asyncio.wait_for(asyncio.to_thread(operate), 10)
    assert len(msg_handler.data_msgs) == 1
    assert len(msg_handler.backend_msgs) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "module",
    [
        "examples/main.py",
        "examples.main",
    ],
)
async def test_snapshot(
    monkeypatch: MonkeyPatch,
    cli_runner: CliRunner,
    fixtures_folder: pathlib.Path,
    module: str,
    tmp_path: pathlib.Path,
):
    monkeypatch.syspath_prepend(fixtures_folder)

    def operate():
        output_file = tmp_path / "test_snapshot.png"
        with switch_cwd(fixtures_folder):
            result = cli_runner.invoke(
                cli,
                ["artifacts", "snapshot", module, "main", "-o", str(output_file)],
                catch_exceptions=False,
            )
        assert result.exit_code == 0
        # Verify output file was created
        assert output_file.exists()
        # Verify it's a valid PNG image (PNG magic bytes: 89 50 4E 47)
        screenshot_bytes = output_file.read_bytes()
        assert len(screenshot_bytes) > 0, "Screenshot should not be empty"
        assert screenshot_bytes.startswith(b"\x89PNG\r\n\x1a\n"), (
            "Screenshot should be a valid PNG image"
        )

    # Use real CADViewerService - increase timeout for browser launch
    await asyncio.wait_for(asyncio.to_thread(operate), 60)
