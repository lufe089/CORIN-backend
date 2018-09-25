"""CORIN URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework import routers
from Apps.encuestador import views

router = routers.DefaultRouter()

#router.register(r'company', views.CompanyViewSet)
#router.register(r'responseFormats', views.ResponseFormatViewSet)
#router.register(r'items', views.ItemsViewSet)
#router.register(r'simpleActiveCategories', views.SimpleActiveCategoriesViewSet)
#router.register(r'components', views.CategoriesViewSet)
#router.register(r'dimensions', views.DimensionsViewSet)
#router.register(r'activeItems', views.OnlyActiveItems)
#router.register(r'instructionsSpanish', views.InstructionsSpanishViewSet)
#router.register(r'activeItemsSpanish', views.SpanishActiveItemsViewSet)
#router.register(r'participantsResponse', views.ParticipantResponseViewSet)
#router.register(r'surveysByClient', views.SurveysByClientViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    path('admin/', admin.site.urls),
    url(r'^api/', include((router.urls, 'encuestador'))),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]


