from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='delivery_eta_minutes',
            field=models.PositiveIntegerField(blank=True, help_text='Pickup point -> destination.', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='pickup_eta_minutes',
            field=models.PositiveIntegerField(blank=True, help_text="Rider's current node -> pickup point.", null=True),
        ),
    ]
