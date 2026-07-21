import pytest
from django.apps import apps
from django.db import IntegrityError, transaction


def _models():
    return (
        apps.get_model("scenes", "Scene"),
        apps.get_model("scenes", "Spot"),
        apps.get_model("scenes", "Route"),
        apps.get_model("scenes", "RouteSpot"),
    )


@pytest.mark.django_db
def test_scene_spot_and_route_models_expose_required_constraints():
    Scene, Spot, Route, RouteSpot = _models()
    scene = Scene.objects.create(slug="jiang-an-campus", name="四川大学江安校区")
    spot = Spot.objects.create(
        scene=scene,
        slug="library",
        name="江安图书馆",
        category="study",
        map_x="0.25000",
        map_y="0.40000",
        status="published",
    )
    route = Route.objects.create(
        scene=scene,
        slug="classic",
        name="江安经典路线",
        estimated_minutes=150,
        status="published",
    )
    RouteSpot.objects.create(route=route, spot=spot, order=1)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            RouteSpot.objects.create(route=route, spot=spot, order=2)


@pytest.mark.django_db
def test_spot_list_returns_only_published_spots(client):
    Scene, Spot, _, _ = _models()
    scene = Scene.objects.create(
        slug="jiang-an-campus",
        name="四川大学江安校区",
        status="published",
    )
    Spot.objects.create(
        scene=scene,
        slug="library",
        name="江安图书馆",
        category="study",
        map_x="0.25000",
        map_y="0.40000",
        status="published",
    )
    Spot.objects.create(
        scene=scene,
        slug="draft-spot",
        name="待审核点位",
        category="landmark",
        map_x="0.50000",
        map_y="0.50000",
        status="draft",
    )

    response = client.get(f"/api/v1/scenes/{scene.slug}/spots")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["data"]["items"]] == ["江安图书馆"]


@pytest.mark.django_db
def test_unpublished_spot_is_not_publicly_readable(client):
    Scene, Spot, _, _ = _models()
    scene = Scene.objects.create(
        slug="jiang-an-campus",
        name="四川大学江安校区",
        status="published",
    )
    spot = Spot.objects.create(
        scene=scene,
        slug="draft-spot",
        name="待审核点位",
        category="landmark",
        map_x="0.50000",
        map_y="0.50000",
        status="draft",
    )

    response = client.get(f"/api/v1/spots/{spot.id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.django_db
def test_scene_detail_and_related_spots_are_public(client):
    Scene, Spot, _, _ = _models()
    scene = Scene.objects.create(
        slug="jiang-an-campus",
        name="四川大学江安校区",
        status="published",
    )
    source = Spot.objects.create(
        scene=scene,
        slug="lake",
        name="明远湖",
        category="landmark",
        map_x="0.40000",
        map_y="0.40000",
        status="published",
    )
    related = Spot.objects.create(
        scene=scene,
        slug="bridge",
        name="长桥",
        category="landmark",
        map_x="0.45000",
        map_y="0.45000",
        status="published",
    )

    scene_response = client.get(f"/api/v1/scenes/{scene.slug}")
    related_response = client.get(f"/api/v1/spots/{source.id}/related")

    assert scene_response.status_code == 200
    assert scene_response.json()["data"]["name"] == "四川大学江安校区"
    assert related_response.status_code == 200
    assert [item["id"] for item in related_response.json()["data"]["items"]] == [
        str(related.id)
    ]


@pytest.mark.django_db
def test_route_list_and_detail_return_ordered_published_stops(client):
    Scene, Spot, Route, RouteSpot = _models()
    SpotMedia = apps.get_model("scenes", "SpotMedia")
    scene = Scene.objects.create(
        slug="jiang-an-campus",
        name="四川大学江安校区",
        status="published",
    )
    first = Spot.objects.create(
        scene=scene,
        slug="library",
        name="江安图书馆",
        category="study",
        map_x="0.25000",
        map_y="0.40000",
        status="published",
    )
    second = Spot.objects.create(
        scene=scene,
        slug="lake",
        name="明远湖",
        category="landmark",
        map_x="0.40000",
        map_y="0.40000",
        status="published",
    )
    SpotMedia.objects.create(
        spot=first,
        url="https://example.com/library.jpg",
        status="published",
    )
    route = Route.objects.create(
        scene=scene,
        slug="classic",
        name="江安经典路线",
        estimated_minutes=150,
        status="published",
    )
    RouteSpot.objects.create(route=route, spot=second, order=2)
    RouteSpot.objects.create(route=route, spot=first, order=1)

    list_response = client.get(f"/api/v1/scenes/{scene.slug}/routes")
    detail_response = client.get(f"/api/v1/routes/{route.id}")

    assert list_response.status_code == 200
    assert list_response.json()["data"]["items"][0]["id"] == str(route.id)
    assert detail_response.status_code == 200
    stops = detail_response.json()["data"]["stops"]
    assert [stop["spot"]["name"] for stop in stops] == ["江安图书馆", "明远湖"]
    assert stops[0]["spot"]["media"][0]["url"] == "https://example.com/library.jpg"
