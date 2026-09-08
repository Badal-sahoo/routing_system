import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agents', '0001_initial'),
        ('graph', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('in_progress', 'In progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_agent_fk', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='agents.agent')),
                ('destination_node_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_tasks', to='graph.node')),
                ('origin_node_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_tasks', to='graph.node')),
            ],
            options={
                'indexes': [models.Index(fields=['status', 'created_at'], name='tasks_task_status_8e5503_idx')],
            },
        ),
    ]
