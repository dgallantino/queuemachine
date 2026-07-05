from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import RequestFactory, TestCase

from queue_app.models import CounterBooth, Organization, Queue, Service, User
from queue_app.views import get_org_queue, get_session_booth, require_session_org
from queue_app.services import QueueService
from queue_app import constants as const


class OrgScopeTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.organization = Organization.objects.create(name='Org A')
        self.other_organization = Organization.objects.create(name='Org B')
        self.user = User.objects.create_user(username='staff', password='pass')
        self.user.organization.add(self.organization)
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.other_user.organization.add(self.other_organization)

        self.service = Service.objects.create(
            organization=self.organization,
            name='General',
            queue_char='A',
        )
        self.foreign_service = Service.objects.create(
            organization=self.other_organization,
            name='Foreign',
            queue_char='B',
        )
        self.queue = Queue.objects.create(service=self.service)
        QueueService.assign_ticket_number(self.queue)
        self.foreign_queue = Queue.objects.create(service=self.foreign_service)
        QueueService.assign_ticket_number(self.foreign_queue)

        self.booth = CounterBooth.objects.create(
            organization=self.organization,
            display_name='Booth 1',
            spoken_name='booth one',
        )
        self.foreign_booth = CounterBooth.objects.create(
            organization=self.other_organization,
            display_name='Foreign',
            spoken_name='foreign booth',
        )

    def _request(self, user, org):
        request = self.factory.get('/')
        request.user = user
        request.session = {
            const.IDX.ORG: org.to_flat_dict(),
            const.IDX.BOOTH: self.booth.to_flat_dict(),
        }
        return request

    def test_require_session_org_rejects_foreign_session_org(self):
        request = self._request(self.user, self.other_organization)
        self.assertIsNone(require_session_org(request))

    def test_get_org_queue_returns_only_org_queue(self):
        request = self._request(self.user, self.organization)
        queue = get_org_queue(request, self.queue.pk)
        self.assertEqual(queue.pk, self.queue.pk)

    def test_get_org_queue_hides_foreign_queue(self):
        request = self._request(self.user, self.organization)
        with self.assertRaises(Http404):
            get_org_queue(request, self.foreign_queue.pk)

    def test_get_session_booth_rejects_foreign_booth(self):
        request = self._request(self.user, self.organization)
        request.session[const.IDX.BOOTH] = self.foreign_booth.to_flat_dict()
        with self.assertRaises(Http404):
            get_session_booth(request)

    def test_queue_service_rejects_foreign_org(self):
        with self.assertRaises(ValidationError):
            QueueService.call_queue(
                self.queue,
                self.booth,
                organization_id=self.other_organization.id,
            )

    def test_queue_service_rejects_foreign_move_target(self):
        with self.assertRaises(ValidationError):
            QueueService.move_queue(
                self.queue,
                self.foreign_service,
                organization_id=self.organization.id,
            )
