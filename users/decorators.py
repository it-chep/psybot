from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


class UserDecorator:

    @classmethod
    def validate(cls, function):
        decorated_funk = login_required(function)

        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:

                return redirect('login')
            return decorated_funk(request, *args, **kwargs)
        return wrapper
