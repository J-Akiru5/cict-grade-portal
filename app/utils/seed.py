import os
import click
import logging


def _get_admin_supabase():
    """Return a Supabase admin client using the service role key."""
    from supabase import create_client
    url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    if not url or not service_key:
        raise RuntimeError('SUPABASE_URL and SUPABASE_SERVICE_KEY must be set.')
    return create_client(url, service_key)


def create_admin(email: str, password: str) -> None:
    """
    Bootstrap an admin user in both Supabase Auth and the local DB.
    Safe to run multiple times — skips if the user already exists.
    """
    from app.extensions import db
    from app.models.user import User

    # Check if already exists locally
    existing = User.query.filter_by(email=email).first()
    if existing:
        click.echo(f'User {email} already exists with role "{existing.role}". Skipping.')
        return

    client = _get_admin_supabase()

    try:
        response = client.auth.admin.create_user({
            'email': email,
            'password': password,
            'email_confirm': True,
            'user_metadata': {'role': 'admin'},
        })
        sb_user = response.user
    except Exception as e:
        # If the user already exists in Supabase but not locally, still sync
        if 'already registered' in str(e).lower() or 'already been registered' in str(e).lower():
            click.echo(f'Supabase user {email} already exists. Syncing local record...')
            try:
                users_response = client.auth.admin.list_users()
                sb_user = next(
                    (u for u in users_response if u.email == email), None
                )
                if not sb_user:
                    raise RuntimeError(f'Could not find {email} in Supabase.')
            except Exception as inner_e:
                raise RuntimeError(f'Failed to retrieve existing Supabase user: {inner_e}')
        else:
            raise RuntimeError(f'Supabase error: {e}')

    user = User(
        id=str(sb_user.id),
        email=email,
        role='admin',
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    click.echo(f'✅  Admin user {email} created successfully (id={sb_user.id}).')


def register_cli(app):
    """Register all seed CLI commands on the Flask app."""

    @app.cli.command('seed-admin')
    @click.option('--email', default='admin@isufst.edu.ph', show_default=True,
                  help='Admin email address.')
    @click.password_option(help='Admin password (prompted if not given).')
    def seed_admin_cmd(email, password):
        """Bootstrap the first admin account."""
        create_admin(email, password)

    @app.cli.command('seed-curriculum')
    def seed_curriculum_cmd():
        """Seed curriculum subjects, students, enrollments & mock grades."""
        from app.utils.seed_curriculum import seed_all
        seed_all()

    @app.cli.command('seed-sections')
    def seed_sections_cmd():
        """Seed missing academic sections (BSIT-1A, BSIT-2C-NT, etc.)."""
        from seed_sections import seed_missing_sections
        seed_missing_sections()

    @app.cli.command('seed-schedules-official')
    @click.option('--academic-year', default='2025-2026', show_default=True,
                  help='Academic year for schedules.')
    @click.option('--semester', default='2nd',
                  type=click.Choice(['1st', '2nd', 'Summer']),
                  show_default=True, help='Semester for schedules.')
    def seed_schedules_official_cmd(academic_year, semester):
        """Seed OFFICIAL class schedules from ISUFST CICT schedule documents."""
        from seed_official_schedules_2025_2026 import seed_official_schedules, create_schedule_entry
        from app.extensions import db

        click.echo(f"🚀 Seeding OFFICIAL schedules for {semester} Semester, A.Y. {academic_year}")
        click.echo("📋 Source: Official ISUFST CICT Schedule Documents")

        try:
            # First ensure all sections exist
            from seed_sections import seed_missing_sections
            section_count = seed_missing_sections()

            # Get all OFFICIAL schedule data
            schedules = seed_official_schedules()

            # Create all schedule entries
            created_count = 0
            for schedule_data in schedules:
                result = create_schedule_entry(*schedule_data)
                if result:
                    created_count += 1

            # Commit all changes
            db.session.commit()

            click.echo(f"✅ Successfully created {created_count} OFFICIAL schedule entries")
            if section_count > 0:
                click.echo(f"✅ Created {section_count} missing sections")
            click.echo("🎓 OFFICIAL schedule seeding completed!")

        except Exception as e:
            db.session.rollback()
            click.echo(f"❌ Error during seeding: {e}")
            raise

