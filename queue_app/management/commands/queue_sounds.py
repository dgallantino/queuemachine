"""Management command for queue announcement sound assets."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from queue_app.sounds import compose, generate, init, paths


class Command(BaseCommand):
    help = (
        'Manage queue announcement sound assets: build the sound map (init), '
        'generate TTS fragments (generate), or compose playback files (compose).'
    )

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', required=True)

        init_parser = subparsers.add_parser(
            'init',
            help='Read the database and write the sound map JSON.',
        )
        init_parser.add_argument(
            '--lang',
            dest='lang_code',
            default=None,
            help='Language code for the map (default: settings.LANGUAGE_CODE).',
        )
        init_parser.add_argument(
            '--organization',
            dest='organization_id',
            default=None,
            help='Limit letters/destinations to one organization UUID.',
        )
        init_parser.add_argument(
            '--map-path',
            dest='map_path',
            default=None,
            help='Output path for sound_map.json (default: queue_app/static/queue_app/audio/sound_map.json).',
        )

        generate_parser = subparsers.add_parser(
            'generate',
            help='Generate WAV fragments from the sound map using a TTS provider.',
        )
        generate_parser.add_argument(
            '--map-path',
            dest='map_path',
            default=None,
            help='Path to sound_map.json.',
        )
        generate_parser.add_argument(
            '--audio-root',
            dest='audio_root',
            default=None,
            help='Root directory for fragment files (default: .../audio/).',
        )
        generate_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List fragment paths without calling TTS.',
        )

        compose_parser = subparsers.add_parser(
            'compose',
            help='Compose fragments into a temporary playable announcement file.',
        )
        compose_parser.add_argument(
            'fragments',
            nargs='*',
            help='Dotted map keys, e.g. phrases.queue_number letters.A numbers.ones.3',
        )
        compose_parser.add_argument(
            '--map-path',
            dest='map_path',
            default=None,
            help='Path to sound_map.json.',
        )
        compose_parser.add_argument(
            '--audio-root',
            dest='audio_root',
            default=None,
            help='Root directory for fragment files.',
        )
        compose_parser.add_argument(
            '--output',
            dest='output_path',
            default=None,
            help='Output file path (default: temporary file).',
        )

    def handle(self, *args, **options):
        subcommand = options['subcommand']

        if subcommand == 'init':
            self._handle_init(options)
        elif subcommand == 'generate':
            self._handle_generate(options)
        elif subcommand == 'compose':
            self._handle_compose(options)
        else:
            raise CommandError(f'Unknown subcommand: {subcommand}')

    def _handle_init(self, options):
        map_path = Path(options['map_path']) if options['map_path'] else None
        written = init.write_sound_map(
            map_path=map_path,
            lang_code=options['lang_code'],
            organization_id=options['organization_id'],
        )
        self.stdout.write(self.style.SUCCESS(f'Sound map written to {written}'))

    def _handle_generate(self, options):
        map_path = Path(options['map_path']) if options['map_path'] else None
        audio_root = Path(options['audio_root']) if options['audio_root'] else None
        root = audio_root or paths.default_audio_root()

        def on_progress(label, dest, index, total, phase):
            try:
                display_path = dest.relative_to(root)
            except ValueError:
                display_path = dest
            if phase == 'start':
                self.stdout.write(f'[{index}/{total}] Generating {label} -> {display_path}')
            else:
                self.stdout.write(self.style.SUCCESS(f'[{index}/{total}] Generated {display_path}'))

        written = generate.generate_fragments(
            map_path=map_path,
            audio_root=audio_root,
            dry_run=options['dry_run'],
            on_progress=on_progress,
        )
        verb = 'Would generate' if options['dry_run'] else 'Generated'
        self.stdout.write(f'{verb} {len(written)} fragment(s).')

    def _handle_compose(self, options):
        if not options['fragments']:
            raise CommandError(
                'Provide at least one fragment key, e.g. '
                'queue_sounds compose phrases.queue_number letters.A'
            )

        map_path = Path(options['map_path']) if options['map_path'] else None
        audio_root = Path(options['audio_root']) if options['audio_root'] else None
        output_path = Path(options['output_path']) if options['output_path'] else None

        output_path, recipe = compose.compose_announcement(
            options['fragments'],
            map_path=map_path,
            audio_root=audio_root,
            output_path=output_path,
        )
        self.stdout.write(self.style.SUCCESS(f'Composed announcement: {output_path}'))
        self.stdout.write('Recipe:')
        self.stdout.write(json.dumps(recipe.to_dict(), indent=2, ensure_ascii=False))
