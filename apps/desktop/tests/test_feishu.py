from tailclose_desktop.models import ScreenResult
from tailclose_desktop.notify.feishu import format_feishu_message, send_feishu_text


def make_result(**overrides):
    data = {
        "code": "600000",
        "name": "浦发银行",
        "latest_price": 10.25,
        "change_percent": 2.34,
        "volume_ratio": 1.56,
        "reasons": ["涨幅在 0% 到 6%", "量比大于 1.2"],
        "score": 88.8,
    }
    data.update(overrides)
    return ScreenResult(**data)


def test_format_feishu_message_includes_strategy_results_and_disclaimer():
    message = format_feishu_message("尾盘策略", [make_result()])

    assert "尾盘策略" in message
    assert "600000" in message
    assert "浦发银行" in message
    assert "10.25" in message
    assert "2.34%" in message
    assert "1.56" in message
    assert "涨幅在 0% 到 6%；量比大于 1.2" in message
    assert "88.8" in message
    assert "仅供策略筛选和观察，不构成投资建议。" in message


def test_format_feishu_message_does_not_leak_webhook_secret():
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/secret-token"

    message = format_feishu_message("尾盘策略", [make_result()], webhook_url=webhook_url)

    assert "secret-token" not in message
    assert webhook_url not in message


def test_format_feishu_message_handles_empty_results():
    message = format_feishu_message("尾盘策略", [])

    assert "尾盘策略" in message
    assert "当前没有符合条件的股票。" in message
    assert "仅供策略筛选和观察，不构成投资建议。" in message


def test_send_feishu_text_posts_text_message_and_raises(monkeypatch):
    calls = []

    class Response:
        def raise_for_status(self):
            calls.append(("raise_for_status",))

    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
        return Response()

    monkeypatch.setattr("tailclose_desktop.notify.feishu.requests.post", fake_post)

    response = send_feishu_text("https://example.test/webhook", "hello", timeout=1.5)

    assert isinstance(response, Response)
    assert calls == [
        (
            "https://example.test/webhook",
            {"msg_type": "text", "content": {"text": "hello"}},
            1.5,
        ),
        ("raise_for_status",),
    ]
