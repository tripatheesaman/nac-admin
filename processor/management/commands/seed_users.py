from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with default users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing users before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing users...')
            User.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all users')
            )

        with transaction.atomic():
                        # Create superadmin user
                        if not User.objects.filter(username='superadmin').exists():
                            superadmin = User.objects.create_user(
                                username='superadmin',
                                email='superadmin@nac.com',
                                first_name='Super',
                                last_name='Admin',
                                password='superadmin123',
                                is_staff=True,
                                is_superuser=True,
                                is_active=True
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Successfully created superadmin user: {superadmin.username}'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING('Superadmin user already exists')
                            )

                        # Create additional test users
                        test_users = [
                            {
                                'username': 'admin',
                                'email': 'admin@nac.com.np',
                                'first_name': 'Admin',
                                'last_name': 'User',
                                'password': 'admin123',
                                'is_staff': True,
                                'is_superuser': False
                            },
                            {
                                'username': 'manager',
                                'email': 'manager@nac.com',
                                'first_name': 'Manager',
                                'last_name': 'User',
                                'password': 'manager123',
                                'is_staff': False,
                                'is_superuser': False
                            },
                            {
                                'username': 'user',
                                'email': 'user@nac.com',
                                'first_name': 'Regular',
                                'last_name': 'User',
                                'password': 'user123',
                                'is_staff': False,
                                'is_superuser': False
                            }
                        ]

                        for user_data in test_users:
                            if not User.objects.filter(username=user_data['username']).exists():
                                user = User.objects.create_user(
                                    username=user_data['username'],
                                    email=user_data['email'],
                                    first_name=user_data['first_name'],
                                    last_name=user_data['last_name'],
                                    password=user_data['password'],
                                    is_staff=user_data['is_staff'],
                                    is_superuser=user_data['is_superuser'],
                                    is_active=True
                                )
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'Successfully created user: {user.username}'
                                    )
                                )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'User {user_data["username"]} already exists')
                                )

        self.stdout.write(
            self.style.SUCCESS(
                '\nUser seeding completed successfully!\n'
                'Default login credentials:\n'
                'Superadmin: superadmin / superadmin123\n'
                'Admin: admin / admin123\n'
                'Manager: manager / manager123\n'
                'User: user / user123'
            )
        ) 