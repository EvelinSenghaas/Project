# Generated by Django 2.2.5 on 2019-12-26 22:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sistema', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreunion',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalreunion',
            name='horario',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Horario_Disponible'),
        ),
        migrations.AddField(
            model_name='historicalreunion',
            name='tipo_reunion',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Tipo_Reunion'),
        ),
        migrations.AddField(
            model_name='historicalmiembro',
            name='domicilio',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Domicilio'),
        ),
        migrations.AddField(
            model_name='historicalmiembro',
            name='estado_civil',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Estado_Civil'),
        ),
        migrations.AddField(
            model_name='historicalmiembro',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmiembro',
            name='horario_disponible',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Horario_Disponible'),
        ),
        migrations.AddField(
            model_name='historicalmiembro',
            name='telefono',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sistema.Telefono'),
        ),
        migrations.AddField(
            model_name='grupo',
            name='miembro',
            field=models.ManyToManyField(to='sistema.Miembro'),
        ),
        migrations.AddField(
            model_name='encuesta',
            name='miembro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sistema.Miembro'),
        ),
        migrations.AddField(
            model_name='domicilio',
            name='barrio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sistema.Barrio'),
        ),
        migrations.AddField(
            model_name='barrio',
            name='localidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sistema.Localidad'),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='miembro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sistema.Miembro'),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='reunion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sistema.Reunion'),
        ),
    ]