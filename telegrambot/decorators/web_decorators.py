from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator


class Decorators:

    @classmethod
    def login_or_not(cls, function):
        decorated_view_func = login_required(function)

        def wrap(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.verified_email:
                # Возвращаем страницу с ошибкой или редиректим на страницу логина
                return redirect('unregistered')

            return decorated_view_func(request, *args, **kwargs)

        return wrap

