import pytest
from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import RequestFactory

from queue_app import constants as const
from queue_app.models import CounterBooth, Organization, Queue, Service, User
from queue_app.services import QueueService
from queue_app.views import get_org_queue, get_session_booth, require_session_org


@pytest.fixture
def org_scope_setup(db):
    factory = RequestFactory()
    organization = Organization.objects.create(name='Org A')
    other_organization = Organization.objects.create(name='Org B')
    user = User.objects.create_user(username='staff', password='pass')
    user.organization.add(organization)
    other_user = User.objects.create_user(username='other', password='pass')
    other_user.organization.add(other_organization)

    service = Service.objects.create(
        organization=organization,
        name='General',
        queue_char='A',
    )
    foreign_service = Service.objects.create(
        organization=other_organization,
        name='Foreign',
        queue_char='B',
    )
    queue = Queue.objects.create(service=service)
    QueueService.assign_ticket_number(queue)
    foreign_queue = Queue.objects.create(service=foreign_service)
    QueueService.assign_ticket_number(foreign_queue)

    booth = CounterBooth.objects.create(
        organization=organization,
        display_name='Booth 1',
        spoken_name='booth one',
    )
    foreign_booth = CounterBooth.objects.create(
        organization=other_organization,
        display_name='Foreign',
        spoken_name='foreign booth',
    )

    def make_request(user, org):
        request = factory.get('/')
        request.user = user
        request.session = {
            const.IDX.ORG: org.to_flat_dict(),
            const.IDX.BOOTH: booth.to_flat_dict(),
        }
        return request

    return {
        'organization': organization,
        'other_organization': other_organization,
        'user': user,
        'service': service,
        'foreign_service': foreign_service,
        'queue': queue,
        'foreign_queue': foreign_queue,
        'booth': booth,
        'foreign_booth': foreign_booth,
        'make_request': make_request,
    }


@pytest.mark.django_db
def test_require_session_org_rejects_foreign_session_org(org_scope_setup):
    request = org_scope_setup['make_request'](
        org_scope_setup['user'],
        org_scope_setup['other_organization'],
    )
    assert require_session_org(request) is None


@pytest.mark.django_db
def test_get_org_queue_returns_only_org_queue(org_scope_setup):
    request = org_scope_setup['make_request'](
        org_scope_setup['user'],
        org_scope_setup['organization'],
    )
    queue = get_org_queue(request, org_scope_setup['queue'].pk)
    assert queue.pk == org_scope_setup['queue'].pk


@pytest.mark.django_db
def test_get_org_queue_hides_foreign_queue(org_scope_setup):
    request = org_scope_setup['make_request'](
        org_scope_setup['user'],
        org_scope_setup['organization'],
    )
    with pytest.raises(Http404):
        get_org_queue(request, org_scope_setup['foreign_queue'].pk)


@pytest.mark.django_db
def test_get_session_booth_rejects_foreign_booth(org_scope_setup):
    request = org_scope_setup['make_request'](
        org_scope_setup['user'],
        org_scope_setup['organization'],
    )
    request.session[const.IDX.BOOTH] = org_scope_setup['foreign_booth'].to_flat_dict()
    with pytest.raises(Http404):
        get_session_booth(request)


@pytest.mark.django_db
def test_queue_service_rejects_foreign_org(org_scope_setup):
    with pytest.raises(ValidationError):
        QueueService.call_queue(
            org_scope_setup['queue'],
            org_scope_setup['booth'],
            organization_id=org_scope_setup['other_organization'].id,
        )


@pytest.mark.django_db
def test_queue_service_rejects_foreign_move_target(org_scope_setup):
    with pytest.raises(ValidationError):
        QueueService.move_queue(
            org_scope_setup['queue'],
            org_scope_setup['foreign_service'],
            organization_id=org_scope_setup['organization'].id,
        )
