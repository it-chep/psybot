from django.shortcuts import render, get_object_or_404
from .models import Mood


def mood_list(request, user_id):
    user_moods = Mood.objects.filter(user__id=user_id)
    return render(request, 'mood/moods.html', {'user_moods': user_moods})

