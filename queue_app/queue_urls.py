from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('machine/',views.MachineDisplay.as_view(), name='index'),
    path('printticket/<int:pk>/', views.PrintTicketView.as_view(), name='printticket'),
    path('test/<int:pk>/', views.PrintTicketApi.as_view(), name='test_print'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
