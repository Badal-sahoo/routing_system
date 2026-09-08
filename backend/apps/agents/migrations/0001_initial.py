import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('graph', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('available', 'Available'), ('busy', 'Busy'), ('offline', 'Offline')], default='offline', max_length=20)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('current_node_fk', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agents', to='graph.node')),
            ],
            options={
                'indexes': [models.Index(condition=models.Q(('status', 'available')), fields=['status'], name='active_idx')],
            },
        ),
    ]
