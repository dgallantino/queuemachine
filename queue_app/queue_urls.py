from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('machine/',views.MachineDisplay.as_view(), name='machine_url'),
    path('printticket/', views.PrintTicketApi.as_view(), name='printticket'),
    path('manager/',views.ManagerDisplay.as_view(), name='manager_url'),
    path('test/<int:pk>/', views.QueueRetriveUpdateAPI.as_view()),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
