import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PUBLISHED = "published", "已发布"
    DISABLED = "disabled", "已停用"


class SpotCategory(models.TextChoices):
    LANDMARK = "landmark", "标志景观"
    CHECKIN = "checkin", "普通打卡点"
    PHOTO = "photo", "拍照打卡点"
    STUDY = "study", "学习空间"
    SERVICE = "service", "生活服务"


class Scene(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=200, blank=True)
    timezone = models.CharField(max_length=64, default="Asia/Shanghai")
    map_image_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(
        max_length=16,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Spot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scene = models.ForeignKey(Scene, on_delete=models.PROTECT, related_name="spots")
    slug = models.SlugField(max_length=80)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=24, choices=SpotCategory.choices)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    knowledge_content = models.TextField(blank=True)
    map_x = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        validators=(MinValueValidator(0), MaxValueValidator(1)),
    )
    map_y = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        validators=(MinValueValidator(0), MaxValueValidator(1)),
    )
    tags = models.JSONField(default=list, blank=True)
    suggested_stay_minutes = models.PositiveSmallIntegerField(default=15)
    is_checkin_enabled = models.BooleanField(default=True)
    is_photo_spot = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("scene", "slug"),
                name="uniq_spot_slug_per_scene",
            ),
            models.CheckConstraint(
                condition=models.Q(map_x__gte=0, map_x__lte=1),
                name="spot_map_x_between_zero_and_one",
            ),
            models.CheckConstraint(
                condition=models.Q(map_y__gte=0, map_y__lte=1),
                name="spot_map_y_between_zero_and_one",
            ),
        )

    def __str__(self):
        return self.name


class SpotMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "图片"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spot = models.ForeignKey(Spot, on_delete=models.PROTECT, related_name="media")
    url = models.URLField(max_length=500, blank=True)
    storage_key = models.CharField(max_length=500, blank=True)
    media_type = models.CharField(
        max_length=16,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=16,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "created_at")


class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scene = models.ForeignKey(Scene, on_delete=models.PROTECT, related_name="routes")
    slug = models.SlugField(max_length=80)
    name = models.CharField(max_length=120)
    summary = models.CharField(max_length=300, blank=True)
    estimated_minutes = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=16,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("scene", "slug"),
                name="uniq_route_slug_per_scene",
            ),
        )

    def __str__(self):
        return self.name


class RouteSpot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="route_spots")
    spot = models.ForeignKey(Spot, on_delete=models.PROTECT, related_name="route_stops")
    order = models.PositiveSmallIntegerField()
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("order",)
        constraints = (
            models.UniqueConstraint(
                fields=("route", "order"),
                name="uniq_route_stop_order",
            ),
            models.UniqueConstraint(
                fields=("route", "spot"),
                name="uniq_spot_per_route",
            ),
        )
