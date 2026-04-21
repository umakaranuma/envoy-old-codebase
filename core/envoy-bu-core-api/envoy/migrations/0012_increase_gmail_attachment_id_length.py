# Generated manually to fix gmail_attachment_id field length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('envoy', '0011_chatconversation_emailchatmessage_emailattachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailattachment',
            name='gmail_attachment_id',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
