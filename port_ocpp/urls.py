"""port_ocpp URL Configuration"""

from django.conf.urls import include
from django.contrib import admin
from django.urls import path


from Controller.views import Charger_ClientViewSet, Transaction_ViewSet
from rest_framework import routers


#Endpoints de la APi
router = routers.DefaultRouter()
router.register('charger', Charger_ClientViewSet)
#router.register('transaction', Transaction_ViewSet)

urlpatterns = [
    path('chat/', include("Controller.urls")),
    path('admin/', admin.site.urls),
    path('pedir/', include("Controller.urls")),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_auth.urls')),
    path('api/v1/auth/registration/', include('rest_auth.registration.urls')),
    path('api/v1/transaction/', Transaction_ViewSet.as_view()),
]

