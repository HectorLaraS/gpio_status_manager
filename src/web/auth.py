from functools import wraps

from flask import redirect, request, session


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(f"/login?next={request.path}")

        return view_func(*args, **kwargs)

    return wrapper


def roles_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(f"/login?next={request.path}")

            role_name = session.get("role_name")

            if role_name not in allowed_roles:
                return redirect("/")

            return view_func(*args, **kwargs)

        return wrapper

    return decorator