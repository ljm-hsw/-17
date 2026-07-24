from rest_framework import serializers

from .models import Route, RouteSpot, Scene, Spot, SpotMedia


class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = ("id", "slug", "name", "subtitle", "timezone", "map_image_url")


class SpotMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotMedia
        fields = ("id", "url", "media_type", "caption", "sort_order")


class SpotSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    is_checked_in = serializers.SerializerMethodField()
    first_checked_in_at = serializers.SerializerMethodField()
    distance_basis = serializers.SerializerMethodField()

    class Meta:
        model = Spot
        fields = (
            "id",
            "scene_id",
            "slug",
            "name",
            "category",
            "summary",
            "description",
            "map_x",
            "map_y",
            "tags",
            "suggested_stay_minutes",
            "is_checkin_enabled",
            "is_photo_spot",
            "media",
            "is_checked_in",
            "first_checked_in_at",
            "distance_basis",
        )

    def get_media(self, obj):
        published_media = [item for item in obj.media.all() if item.status == "published"]
        return SpotMediaSerializer(published_media, many=True).data

    def _personal_event(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return None
        from apps.visits.models import CheckinEvent

        return (
            CheckinEvent.objects.filter(
                user=request.user,
                spot=obj,
                status=CheckinEvent.Status.ACCEPTED,
            )
            .order_by("received_at", "id")
            .first()
        )

    def get_is_checked_in(self, obj):
        return self._personal_event(obj) is not None

    def get_first_checked_in_at(self, obj):
        event = self._personal_event(obj)
        return serializers.DateTimeField().to_representation(event.received_at) if event else None

    def get_distance_basis(self, obj):
        del obj
        return "scene_map_coordinates"


class RouteStopSerializer(serializers.ModelSerializer):
    spot = SpotSerializer(read_only=True)

    class Meta:
        model = RouteSpot
        fields = ("id", "order", "note", "spot")


class RouteSerializer(serializers.ModelSerializer):
    stops = RouteStopSerializer(source="route_spots", many=True, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "scene_id", "slug", "name", "summary", "estimated_minutes", "stops")
