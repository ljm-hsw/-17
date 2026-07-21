import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings

from apps.common.errors import ApiError

WECHAT_SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


def exchange_wechat_code(code):
    if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
        raise ApiError("SERVICE_UNAVAILABLE", "微信登录服务尚未配置", 503)
    query = urlencode(
        {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    try:
        with urlopen(f"{WECHAT_SESSION_URL}?{query}", timeout=5) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as exc:
        raise ApiError("WECHAT_LOGIN_FAILED", "微信登录暂时不可用", 503) from exc
    openid = payload.get("openid")
    if not openid:
        raise ApiError("WECHAT_LOGIN_FAILED", "微信登录凭证无效", 400)
    return openid
