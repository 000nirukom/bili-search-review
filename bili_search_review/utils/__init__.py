from bilibili_api import login


def login_with_qr():
    credential = login.login_with_qrcode()
    try:
        credential.raise_for_no_bili_jct()
        credential.raise_for_no_sessdata()
    except Exception:
        print("登陆失败。")
        raise

    return credential


def login_with_qr_term():
    credential = login.login_with_qrcode_term()
    try:
        credential.raise_for_no_bili_jct()
        credential.raise_for_no_sessdata()
    except Exception:
        print("登陆失败。")
        raise

    return credential
