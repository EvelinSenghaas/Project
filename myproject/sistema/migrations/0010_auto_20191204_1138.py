# Generated by Django 2.2.5 on 2019-12-04 14:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sistema', '0009_auto_20191204_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipo_telefono',
            name='empresa',
            field=models.CharField(blank=True, choices=[('Movistar', 'Movistar'), ('Otro', 'Otro'), ('Personal', 'Personal'), ('Tuenti', 'Tuenti'), ('Claro', 'Claro')], max_length=50, null=True, verbose_name='Empresa'),
        ),
        migrations.AlterField(
            model_name='tipo_telefono',
            name='tipo',
            field=models.CharField(blank=True, choices=[('Movil', 'Movil'), ('Fijo', 'Fijo')], max_length=50, null=True, verbose_name='Tipo'),
        ),
        migrations.CreateModel(
            name='HistoricalReunion',
            fields=[
                ('id_reunion', models.IntegerField(blank=True, db_index=True)),
                ('nombre', models.CharField(max_length=100, null=True, verbose_name='Nombre')),
                ('borrado', models.BooleanField(default=False, verbose_name='borrado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('domicilio', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Domicilio')),
                ('grupo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Grupo')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('horario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Horario_Disponible')),
                ('tipo_reunion', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Tipo_Reunion')),
            ],
            options={
                'verbose_name': 'historical reunion',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
