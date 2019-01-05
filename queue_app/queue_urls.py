from django.urls import path, include
from queue_app import views
from django.conf import settings
from django.conf.urls.static import static

app_name='queue'


manager_patterns = [
    path(
        '',
        views.ManagerDisplayView.as_view(),
        name='index'
    ),
    path(
        'queues/<uuid:pk>/call/',
        views.CallQueueView.as_view(),
        name='call'
    ),
    path(
        'queues/add-booking/',
        views.AddBookingQueueView.as_view(),
        name='add_booking'
    ),
    path(
        'queues/service/<uuid:pk>/',
        views.QueuePerServiceView.as_view(),
        name='service_queues'
    ),
    path(
        'users/',
        views.UserLookupView.as_view(),
        name='user_autocomplete'
    ),
    path(
        'services/',
        views.ServiceLookupView.as_view(),
        name='service_autocomplete'
    ),
    path(
        'organization/lookup/',
        views.OrganizationLookupView.as_view(),
        name='organization_autocomplete'
    ),
    path(
        'customer/add/',
        views.AddCustomerView.as_view(),
        name='add_customer'
    ),
    path(
        'booths/',
        views.ManagerBoothListView.as_view(),
        name='booth_list'
    ),
    path(
        'booths/<uuid:pk>/',
        views.BoothToSession.as_view(),
        name='session_booth'
    ),
    path(
        'organization/',
        views.OrganizationListView.as_view(),
        name='organization_list'
    ),
    path(
        'organization/<uuid:pk>/',
        views.OrganizationToSession.as_view(),
        name='session_org'
    ),
    path(
        'users/self/edit/',
        views.EditUserView.as_view(),
        name='edit_user'
    ),
    path(
        'users/self/password/',
        views.ChangePasswordView.as_view(),
        name='change_password'
    ),
    path(
        'queues/audio/',
        views.playAudioFile,
        name='audio'
    ),
    path(
        'lang/<str:lang_id>/',
        views.SetLanguageRedirect.as_view(),
        name='language'
    ),
]

machine_patterns =[
    path(
        '',
        views.MachineDisplayView.as_view(),
        name='index'
    ),
    path(
        'booking-list/',
        views.BookingQueueListView.as_view(),
        name='booking_list'
    ),
    path(
        'booking-list/<uuid:pk>/',
        views.BookingQueueListView.as_view(),
        name='booking_list_update'
    ),
    path(
        'print-ticket/<uuid:pk>/',
        views.PrintTicketView.as_view(),
        name='print'
    ),
]

board_patterns = [
    path(
        '',
        views.InfoBoardMainView.as_view(),
        name='index'
    ),
    path(
        'queues/',
        views.InfoBoardQueueListView.as_view(),
        name='queues'
    ),
    path(
        'queues/service/<uuid:pk>/',
        views.InfoBoardQueuePerService.as_view(),
        name='service_queues'
    ),
    path(
        'booths/<uuid:pk>/details/',
        views.InfoBoardBoothDetailView.as_view(),
        name='booth_detail'
    ),
]

urlpatterns = [
    path('machine/', include((machine_patterns,'machine'))),
    path('manager/', include((manager_patterns,'manager'))),
    path('infoboard/', include((board_patterns,'infoboard'))),
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='sign_up'
    ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
