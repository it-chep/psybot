from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Subquery, OuterRef
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, path
from django.utils.html import format_html_join, format_html

from .admin_views import mood_list
from .models import *


# Register your models here.


class MoodInline(admin.TabularInline):
    model = Mood
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'name', 'username', 'level', 'expirience', 'quality')
    # inlines = [MoodInline]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('moods/<int:user_id>/', self.admin_site.admin_view(mood_list), name='mood_list'),
        ]
        return my_urls + urls

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(last_three=Subquery(
            Mood.objects.filter(user=OuterRef('pk')).order_by('-date')[:3].values('pk')))

        return qs

    def show_last_three(self, obj):
        moods = obj.mood_set.order_by('-date')[:5]
        return '\n'.join([str(mood) for mood in moods])
    show_last_three.short_description = 'Настроение за последние 5 дней'

    def show_all_moods(self, obj):
        url = reverse('admin:mood_list', args=[obj.pk])
        return format_html(f'<a href="{url}" target="_blank">Показать все</a>')
        # return format_html(f'<a href="/admin/mood/?user__id__exact={obj.pk}" target="_blank">Показать все</a>')

    show_all_moods.short_description = 'Все настроения'

    readonly_fields = ['show_last_three', 'show_all_moods']
    # readonly_fields = ['show_last_three',]


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('date', 'grade')


@admin.register(Feedback)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_added', 'text')


@admin.register(Messages)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'message_text', 'sending_time')


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(PhotoForCards)
class PhotoCardsAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Workers)
class WorkersAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'job_place', 'job_title',)
