import pytest

from jmcomic.jm_client_interface import JmApiResp
from jmcomic.jm_exception import JmcomicException
from jmcomic.jm_toolkit import JmcomicText, JmImageTool


def test_api_missing_envelope_is_typed_error():
    class Resp:
        status_code = 200
        content = b"{}"
        text = "{}"
        url = "https://example.test"

        def json(self):
            return {}

    with pytest.raises(JmcomicException):
        JmApiResp(Resp(), "1").require_success()


def test_json_parser_handles_nested_object():
    payload = 'prefix {"code":200,"data":{"nested":{"value":1}}} suffix'
    assert JmcomicText.try_parse_json_object(payload)["data"]["nested"]["value"] == 1


def test_invalid_image_cache_is_not_accepted(tmp_path):
    path = tmp_path / "cached.jpg"
    path.write_bytes(b"")
    assert JmImageTool.is_valid_image_file(str(path)) is False
