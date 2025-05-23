# Generated by Django 4.2.19 on 2025-02-28 19:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reportgen', '0003_alter_finding_nessus_scan_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='reporting_team',
            field=models.CharField(db_index=True, default=django.utils.timezone.now, max_length=190),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='client_contacts',
            field=models.ManyToManyField(help_text='A client contact has to be created before it can be selected.', to='reportgen.clientcontact'),
        ),
        migrations.AlterField(
            model_name='report',
            name='findings',
            field=models.ManyToManyField(help_text='Findings have to be created before the grouping can be selected.', to='reportgen.engagementfindinggroup'),
        ),
        migrations.AlterField(
            model_name='report',
            name='improvement_areas',
            field=models.ManyToManyField(help_text='An improvement area has to be created before it can be selected.', to='reportgen.improvement'),
        ),
        migrations.AlterField(
            model_name='report',
            name='score_overrides',
            field=models.ManyToManyField(blank=True, help_text='Scoring overrides have to be created before it can be selected.', to='reportgen.scoreoverride'),
        ),
        migrations.AlterField(
            model_name='report',
            name='solution_overrides',
            field=models.ManyToManyField(blank=True, help_text='Solution overrides have to be created before it can be selected.', to='reportgen.solutionoverride'),
        ),
        migrations.AlterField(
            model_name='report',
            name='strengths',
            field=models.ManyToManyField(help_text='A strength has to be created before it can be selected.', to='reportgen.strength'),
        ),
    ]
