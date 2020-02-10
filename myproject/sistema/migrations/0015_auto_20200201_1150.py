# Generated by Django 2.2.5 on 2020-02-01 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0014_auto_20200131_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipo_telefono',
            name='empresa',
            field=models.CharField(blank=True, choices=[('Tuenti', 'Tuenti'), ('Claro', 'Claro'), ('Personal', 'Personal'), ('Movistar', 'Movistar'), ('Otro', 'Otro')], max_length=50, null=True, verbose_name='Empresa'),
        ),
        migrations.CreateModel(
            name='Estado_Reunion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(max_length=50)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('reunion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sistema.Reunion')),
            ],
        ),
    ]