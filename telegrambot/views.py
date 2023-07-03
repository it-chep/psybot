from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import F, ExpressionWrapper, FloatField, Case, When
import logging

from .decorators.web_decorators import Decorators
from .models import *
from django.views.generic import ListView
# django.contrib.auth.views.login
logger = logging.getLogger(__name__)


@method_decorator(Decorators.login_or_not, name='dispatch')
class Home(APIView):

    def get(self, request):
        return render(request, 'web_intarface/homepage.html')


@method_decorator(Decorators.login_or_not, name='dispatch')
class Raiting(ListView):
    model = Profile
    template_name = "web_intarface/raiting.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            rating=ExpressionWrapper(
                F('level') * Case(
                    When(quality=0, then=1),
                    default=F('quality'),
                    output_field=FloatField()
                )
                /
                Case(
                    When(expirience=0, then=1),
                    default=F('expirience'),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        ).filter(rating__gt=0).order_by('-rating')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['raiting_list'] = self.get_queryset()
        return context


class FeedBacks(APIView):
    template_name = 'web_intarface/feedbacks.html'

    def get(self, request):
        reviews = Feedback.objects.all()
        return render(request, self.template_name, {'reviews': reviews})

    def post(self, request):
        reviews = Feedback.objects.all()

        name = request.POST.get('name')
        date = request.POST.get('date')
        if name:
            reviews = Feedback.objects.order_by("name")
        if date:
            reviews = Feedback.objects.order_by("name")
        return render(request, self.template_name, {'reviews': reviews})


class FeedBacksTop(APIView):
    template_name = 'web_intarface/feedbacks.html'

    def get(self, request):
        reviews = Feedback.objects.all()
        return render(request, self.template_name, {'reviews': reviews})


class UnRegistered(APIView):
    template_name = 'web_intarface/unregistered.html'

    def get(self, request):

        return render(request, self.template_name)
