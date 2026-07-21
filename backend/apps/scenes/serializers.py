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
        )

    def get_media(self, obj):
        published_media = [item for item in obj.media.all() if item.status == "published"]
        return SpotMediaSerializer(published_media, many=True).data


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
