# Generated by Django 4.0.2 on 2022-02-22 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('Event ID', models.IntegerField(auto_created=True, db_index=True, primary_key=True, serialize=False, unique=True, verbose_name='Event ID')),
                ('Event Name', models.CharField(db_index=True, max_length=20, verbose_name='Event Name')),
                ('Event Summary', models.CharField(max_length=255, verbose_name='Event Summary')),
                ('Event Date Time', models.DateTimeField(verbose_name='Event Date Time')),
                ('Event Price', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Event Price')),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('Place ID', models.IntegerField(auto_created=True, db_index=True, primary_key=True, serialize=False, unique=True, verbose_name='Place ID')),
                ('Event building', models.CharField(max_length=20, verbose_name='Event place')),
                ('Street', models.CharField(max_length=100, verbose_name='Building street')),
                ('Event city', models.CharField(max_length=20, verbose_name='Event city')),
                ('Pincode', models.IntegerField(verbose_name='pincode')),
            ],
        ),
        migrations.CreateModel(
            name='EventsMeta',
            fields=[
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='api.events')),
                ('Event Duration', models.IntegerField(verbose_name='Event duration (secs)')),
                ('Booking start time', models.DateTimeField(null=True, verbose_name='Event booking start Date and time')),
                ('Booking end time', models.DateTimeField(null=True, verbose_name='Event booking end date')),
                ('Event capacity', models.IntegerField(default=0, verbose_name='Event max capacity')),
                ('Event availability', models.IntegerField(verbose_name='current availability')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('Auditorium ID', models.IntegerField(auto_created=True, db_index=True, primary_key=True, serialize=False, unique=True, verbose_name='Auditorium ID')),
                ('Ticket no', models.CharField(max_length=10, unique=True)),
                ('Payment method', models.CharField(max_length=10, verbose_name='Mode of payment')),
                ('Ticket price', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Amount payable')),
                ('events', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.events')),
            ],
        ),
        migrations.CreateModel(
            name='Auditorium',
            fields=[
                ('Auditorium ID', models.IntegerField(auto_created=True, db_index=True, primary_key=True, serialize=False, unique=True, verbose_name='Auditorium ID')),
                ('Auditorium name', models.CharField(db_index=True, max_length=20, verbose_name='Auditorium name')),
                ('Capacity', models.IntegerField(verbose_name='Max capacity of auditorium')),
                ('Place', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.place', verbose_name='lookup to Auditorium')),
            ],
        ),
    ]
