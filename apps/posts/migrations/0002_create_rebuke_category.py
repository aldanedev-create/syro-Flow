from django.db import migrations


def create_rebuke_category(apps, schema_editor):
    Category = apps.get_model('posts', 'Category')
    Category.objects.get_or_create(
        slug='rebuke',
        defaults={
            'name': 'Rebuke',
            'description': (
                'Bold teachings and corrections for spiritual growth and '
                'accountability. Posts in this category appear under /rebuke/ '
                'with their own styling.'
            ),
        },
    )


def remove_rebuke_category(apps, schema_editor):
    Category = apps.get_model('posts', 'Category')
    Category.objects.filter(slug='rebuke').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_rebuke_category, remove_rebuke_category),
    ]
