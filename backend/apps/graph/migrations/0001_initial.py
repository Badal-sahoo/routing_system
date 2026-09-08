import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=255)),
                ('lat', models.DecimalField(decimal_places=8, max_digits=11)),
                ('lng', models.DecimalField(decimal_places=8, max_digits=11)),
            ],
            options={
                'indexes': [models.Index(fields=['lat', 'lng'], name='graph_node_lat_b98904_idx')],
            },
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('weight', models.IntegerField()),
                ('is_bidirectional', models.BooleanField(default=False)),
                ('from_node_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_edges', to='graph.node')),
                ('to_node_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_edges', to='graph.node')),
            ],
        ),
    ]
