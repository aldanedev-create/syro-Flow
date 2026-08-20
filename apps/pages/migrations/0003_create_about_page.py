from django.db import migrations


def create_about_page(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')
    PageSection = apps.get_model('pages', 'PageSection')

    page, created = Page.objects.get_or_create(
        slug='about',
        defaults={
            'title': 'About Us',
            'excerpt': 'Learn more about our mission and vision',
            'content': (
                "<p>Are you Holy or the devil? my Son if your the devil you die "
                "with your God if you don't repent</p>"
            ),
            'status': 'published',
            'seo_title': 'About Us',
            'seo_description': 'Learn more about our mission and vision',
        },
    )

    if not created:
        return

    sections = [
        (
            'What I Do',
            "<p><strong>Teachings &amp; Articles</strong> &mdash; I preach the "
            "truth i seek no riches i will tell you your a devil i will tell "
            "God will destroy your soul it you don't surrender. i will tell if "
            "you go to hell i will condem you</p>"
            "<p><strong>Community Building</strong> &mdash; Am not here to "
            "please men Many of you are of the world and only few a chosen I "
            "can't b have frendship with Satan if you devil like your father "
            "the Devil why should have frendship with fool.</p>"
            "<p><strong>Making a Difference</strong> &mdash; Through your "
            "support, we are able to reach more people and make a lasting "
            "impact.</p>",
            1,
        ),
        (
            'Our Vision',
            "<p>Faith without Work is Dead they speak the word of God but be "
            "the devil because a lie was spoken your Sakes am mine what am a "
            "false now now ask Papa Jesus and he tell you the truth satan "
            "this or Holy . Lead on God for understanding it is written</p>",
            2,
        ),
        (
            'Our Team',
            "<p><strong>Aldane Hutchinson</strong> &mdash; Founder &amp; Lead "
            "Writer</p><p>Faith without work is DEad I am nothing fool for God "
            "sakes</p>",
            3,
        ),
    ]

    for title, content, order in sections:
        PageSection.objects.get_or_create(
            page=page,
            title=title,
            defaults={'content': content, 'order': order},
        )


def remove_about_page(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')
    Page.objects.filter(slug='about').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_alter_page_status'),
    ]

    operations = [
        migrations.RunPython(create_about_page, remove_about_page),
    ]
