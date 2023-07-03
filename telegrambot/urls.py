from django.urls import include, path
from django.views.decorators.cache import cache_page

from .views import *
from .admin import *
from .handlers.handlers import telegram_webhook

urlpatterns = [
    path('raiting/', Raiting.as_view(), name='raiting'),

    path('reviews/', FeedBacks.as_view(), name='feedback'),
    # path('reviews/name', FeedBacks.as_view(), name='name_feedback'),
    # path('reviews/date', FeedBacks.as_view(), name='date_feedback'),
    # path('reviews/fullfilter', FeedBacks.as_view(), name='full_feedback'),
    # path('reviews/top_name', FeedBacks.as_view(), name='top_name_feedback'),
    path(f'{settings.BOT_TOKEN}/', telegram_webhook, name='bot'),
    # path('6084181152:AAEjV1FR6SyuZx-FOyWVdGc3xJJSIwdisB0/', telegram_webhook, name='test'),

    path('unregistered/', UnRegistered.as_view(), name='unregistered'),
    path('', Home.as_view(), name='homepage')
]
