from django.urls import path
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.IndexView.as_view(), name='index'),
    path('<int:service_id>/printticket',views.print_ticket, name='printticket'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
