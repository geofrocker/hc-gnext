# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-19 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20171219_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='kind',
            field=models.CharField(choices=[('email', 'Email'), ('aft', 'AfricasTalking'), ('webhook', 'Webhook'), ('hipchat', 'HipChat'), ('slack', 'Slack'), ('pd', 'PagerDuty'), ('po', 'Pushover'), ('victorops', 'VictorOps')], max_length=20),
        ),
    ]
