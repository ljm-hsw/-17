import secrets

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Card, CardActivationCode
from apps.accounts.uid import digest_card_uid, mask_card_uid
from apps.iot.crypto import encrypt_device_secret, fingerprint_device_secret
from apps.iot.models import Device
from apps.scenes.models import PublishStatus, Route, RouteSpot, Scene, Spot

SPOTS = (
    ("jiang-an-library", "江安图书馆", "study", "0.32000", "0.26000"),
    ("mingyuan-lake", "明远湖", "landmark", "0.43000", "0.51000"),
    ("long-bridge", "长桥", "landmark", "0.39000", "0.43000"),
    ("knowledge-square", "知识广场", "landmark", "0.57000", "0.36000"),
    ("lakeside-greenway", "环湖绿道", "photo", "0.52000", "0.57000"),
    ("south-gate", "南门", "landmark", "0.35000", "0.78000"),
    ("arts-building", "艺术学院", "landmark", "0.70000", "0.42000"),
    ("sports-center", "体育中心", "service", "0.18000", "0.65000"),
)

ROUTES = (
    (
        "jiang-an-classic",
        "江安经典路线",
        150,
        ("south-gate", "long-bridge", "mingyuan-lake", "jiang-an-library"),
    ),
    (
        "jiang-an-discovery",
        "江安探索路线",
        120,
        ("knowledge-square", "arts-building", "lakeside-greenway", "sports-center"),
    ),
)

CARDS = (
    ("SCU-JA-0001", "04A1B2C3"),
    ("SCU-JA-0002", "04D4E5F6"),
    ("SCU-JA-0003", "04778899"),
)

GROUP_MODELS = {
    "content_operator": (
        "scenes.scene",
        "scenes.spot",
        "scenes.spotmedia",
        "scenes.route",
        "scenes.routespot",
    ),
    "device_operator": ("iot.device",),
    "data_administrator": (
        "accounts.card",
        "accounts.cardactivationcode",
        "accounts.cardbinding",
    ),
}


class Command(BaseCommand):
    help = "幂等创建游迹织梦江安校区 Demo 数据"

    def add_arguments(self, parser):
        parser.add_argument("--device-secret", default=None)

    @transaction.atomic
    def handle(self, *args, **options):
        del args
        scene = self._seed_scene_and_spots()
        self._seed_routes(scene)
        self._seed_cards()
        self._seed_device(scene, options["device_secret"])
        self._seed_groups()
        self.stdout.write(self.style.SUCCESS("江安校区 Demo 数据已就绪"))

    def _seed_scene_and_spots(self):
        scene, _ = Scene.objects.update_or_create(
            slug="jiang-an-campus",
            defaults={
                "name": "四川大学江安校区",
                "subtitle": "智慧景观导览",
                "timezone": "Asia/Shanghai",
                "status": PublishStatus.PUBLISHED,
            },
        )
        for slug, name, category, map_x, map_y in SPOTS:
            Spot.objects.update_or_create(
                scene=scene,
                slug=slug,
                defaults={
                    "name": name,
                    "category": category,
                    "summary": f"探索{name}的校园故事与特色景观。",
                    "description": f"{name}是江安校区推荐游览点位。",
                    "knowledge_content": f"关于{name}的校园文化与空间介绍。",
                    "map_x": map_x,
                    "map_y": map_y,
                    "tags": ["江安校区", "推荐点位"],
                    "suggested_stay_minutes": 30,
                    "is_checkin_enabled": True,
                    "is_photo_spot": category == "photo",
                    "status": PublishStatus.PUBLISHED,
                },
            )
        return scene

    def _seed_routes(self, scene):
        spots = {spot.slug: spot for spot in Spot.objects.filter(scene=scene)}
        for slug, name, minutes, stop_slugs in ROUTES:
            route, _ = Route.objects.update_or_create(
                scene=scene,
                slug=slug,
                defaults={
                    "name": name,
                    "summary": "适合初次探索江安校区的推荐路线。",
                    "estimated_minutes": minutes,
                    "status": PublishStatus.PUBLISHED,
                },
            )
            route.route_spots.all().delete()
            RouteSpot.objects.bulk_create(
                [
                    RouteSpot(route=route, spot=spots[stop_slug], order=index)
                    for index, stop_slug in enumerate(stop_slugs, start=1)
                ]
            )

    def _seed_cards(self):
        for serial_no, raw_uid in CARDS:
            card, _ = Card.objects.get_or_create(
                serial_no=serial_no,
                defaults={
                    "uid_hmac": digest_card_uid(raw_uid),
                    "uid_masked": mask_card_uid(raw_uid),
                    "status": Card.Status.AVAILABLE,
                },
            )
            if not card.activation_codes.filter(status=CardActivationCode.Status.UNUSED).exists():
                plaintext = secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8].upper()
                activation = CardActivationCode(card=card)
                activation.set_code(plaintext)
                activation.save()
                self.stdout.write(f"{serial_no} 激活码（仅显示一次）：{plaintext}")

    def _seed_device(self, scene, supplied_secret):
        spot = Spot.objects.get(scene=scene, slug="jiang-an-library")
        if Device.objects.filter(device_id="SCU-JA-DEMO-001").exists():
            Device.objects.filter(device_id="SCU-JA-DEMO-001").update(
                scene=scene,
                spot=spot,
                device_type=Device.DeviceType.RFID,
                status=Device.Status.ACTIVE,
            )
            return
        secret = supplied_secret or secrets.token_urlsafe(32)
        Device.objects.create(
            device_id="SCU-JA-DEMO-001",
            scene=scene,
            spot=spot,
            device_type=Device.DeviceType.RFID,
            secret_encrypted=encrypt_device_secret(secret),
            secret_fingerprint=fingerprint_device_secret(secret),
            status=Device.Status.ACTIVE,
        )
        self.stdout.write(f"设备密钥（仅显示一次）：{secret}")

    def _seed_groups(self):
        for group_name, model_labels in GROUP_MODELS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = Permission.objects.none()
            for model_label in model_labels:
                app_label, model = model_label.split(".")
                permissions = permissions | Permission.objects.filter(
                    content_type__app_label=app_label,
                    content_type__model=model,
                    codename__in=(f"view_{model}", f"add_{model}", f"change_{model}"),
                )
            group.permissions.set(permissions)
