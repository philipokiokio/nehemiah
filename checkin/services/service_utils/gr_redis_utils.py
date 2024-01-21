from checkin.root.redis_manager import gr_redis


FORGET_PASSWORD_EXPIRE = 120


def forget_admin_key_generator(token: int):
    return f"Forget-Admin-Key-{token}"


def add_forget_admin_token(token: int, email: str):
    key = forget_admin_key_generator(token=token)

    return gr_redis.set(name=key, value=email, ex=FORGET_PASSWORD_EXPIRE)


def get_forget_admin_token(token: int):
    key = forget_admin_key_generator(token=token)

    return gr_redis.get(name=key)


def delete_forget_admin_token(token: int):
    key = forget_admin_key_generator(token=token)
    return gr_redis.delete(key)


def black_list_bearer_tokens(access_token: str):
    return f"black-list-token-{access_token}"


def add_token_blacklist(access_token: str, refresh_token: str):
    for token in [access_token, refresh_token]:
        key = black_list_bearer_tokens(access_token=token)
        gr_redis.set(name=key, value=token, ex=60 * 60 * 24)


def get_token_blacklist(token: str):
    key = black_list_bearer_tokens(access_token=token)
    return gr_redis.get(name=key)
