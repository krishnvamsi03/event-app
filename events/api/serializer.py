from rest_framework import serializers
from .models import Events, EventsMeta


class EventsMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsMeta
        fields = "__all__"
        extra_kwargs = {
            'event_meta_id': {"required": False}
        }

    def update(self, instance, validated_data):
        instance["Event Duration"] = validated_data.get(
            "Event Duration", instance["Event Duration"])
        instance["Booking start time"] = validated_data.get(
            "Booking start time", instance["Booking start time"])
        instance["Booking end time"] = validated_data.get(
            "Booking end time", instance["Booking end time"])
        instance["Event capacity"] = validated_data.get(
            "Event capacity", instance["Event capacity"])
        instance["Event availability"] = validated_data.get(
            "Event availability", instance["Event availability"])
        instance.save()
        return instance


class EventsSerializer(serializers.ModelSerializer):
    event_meta = EventsMetaSerializer(read_only=True)

    class Meta:
        model = Events
        fields = "__all__"
        extra_kwargs = {
            'Event ID': {"required": False}
        }

    # def create(self, validated_data):
    #     event_meta = EventsMetaSerializer.create(
    #         EventsMetaSerializer(), validated_data)
    #     event, created = Events.objects.create(event_meta=event_meta)
    #     return event

    def update(self, instance, validated_data):
        instance.eventMeta = EventsMetaSerializer.update(
            EventsMetaSerializer(), instance.event_meta, validated_data)
        instance["Event Name"] = validated_data.get(
            "Event Name", instance["Event Name"])
        instance["Event Summary"] = validated_data.get(
            "Event Summary", instance["Event Summary"])
        instance["Event Date Time"] = validated_data.get(
            "Event Date Time", instance["Event Date Time"])
        instance["Event Price"] = validated_data.get(
            "Event Price", instance["Event Price"])
        instance.save()
        return instance
