import os
import logging

from bilibili_api import login

logger = logging.getLogger(__name__)


def login_checked():
    if os.environ.get("BSR_TERM_LOGIN", "0") == "1":
        credential = login.login_with_qrcode_term()
    else:
        credential = login.login_with_qrcode()

    try:
        credential.raise_for_no_bili_jct()
        credential.raise_for_no_sessdata()
    except Exception as e:
        logging.error(f"Login failed, {e.__class__.__name__}: {e.__cause__}")
        return None

    return credential
