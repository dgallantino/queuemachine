from django.test import SimpleTestCase

from queue_app.sounds.announcement import compose_call_fragment_keys, number_fragment_keys


class NumberFragmentKeysTests(SimpleTestCase):
    def test_teens(self):
        self.assertEqual(
            number_fragment_keys(13),
            ['numbers.ones.3', 'numbers.teens.belas'],
        )

    def test_tens_and_ones(self):
        self.assertEqual(
            number_fragment_keys(25),
            ['numbers.tens.20', 'numbers.ones.5'],
        )

    def test_ninety_nine(self):
        self.assertEqual(
            number_fragment_keys(99),
            ['numbers.tens.90', 'numbers.ones.9'],
        )

    def test_one_hundred(self):
        self.assertEqual(number_fragment_keys(100), ['numbers.special.100'])

    def test_one_hundred_fifteen(self):
        self.assertEqual(
            number_fragment_keys(115),
            ['numbers.special.100', 'numbers.ones.5', 'numbers.teens.belas'],
        )

    def test_one_hundred_twenty_five(self):
        self.assertEqual(
            number_fragment_keys(125),
            ['numbers.special.100', 'numbers.tens.20', 'numbers.ones.5'],
        )

    def test_two_hundred(self):
        self.assertEqual(
            number_fragment_keys(200),
            ['numbers.ones.2', 'numbers.hundreds.ratus'],
        )

    def test_two_hundred_fifty(self):
        self.assertEqual(
            number_fragment_keys(250),
            ['numbers.ones.2', 'numbers.hundreds.ratus', 'numbers.tens.50'],
        )

    def test_nine_hundred_ninety_nine(self):
        self.assertEqual(
            number_fragment_keys(999),
            [
                'numbers.ones.9',
                'numbers.hundreds.ratus',
                'numbers.tens.90',
                'numbers.ones.9',
            ],
        )

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            number_fragment_keys(1000)


class ComposeCallFragmentKeysTests(SimpleTestCase):
    def test_full_call_a25(self):
        self.assertEqual(
            compose_call_fragment_keys('A', 25, 'konter_farmasi'),
            [
                'phrases.queue_number',
                'letters.A',
                'numbers.tens.20',
                'numbers.ones.5',
                'phrases.please_go_to',
                'destinations.konter_farmasi',
            ],
        )
