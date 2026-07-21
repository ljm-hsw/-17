from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from apps.common.api import api_response
from apps.common.management import list_response

from .models import Card, CardBinding, User


def user_data(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "is_demo": user.is_demo,
        "is_active": user.is_active,
        "active_card_count": sum(
            binding.unbound_at is None for binding in user.card_bindings.all()
        ),
    }


def card_data(card):
    return {
        "id": str(card.id),
        "serial_no": card.serial_no,
        "uid_masked": card.uid_masked,
        "status": card.status,
        "issued_at": card.issued_at,
        "last_used_at": card.last_used_at,
    }


def binding_data(binding):
    return {
        "id": str(binding.id),
        "user_id": str(binding.user_id),
        "card_id": str(binding.card_id),
        "alias": binding.alias,
        "is_primary": binding.is_primary,
        "bind_method": binding.bind_method,
        "bound_at": binding.bound_at,
        "unbound_at": binding.unbound_at,
    }


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.prefetch_related("card_bindings").order_by("date_joined")
        return list_response(request, users, user_data)


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        user = get_object_or_404(User.objects.prefetch_related("card_bindings"), id=user_id)
        return api_response(request, user_data(user))


class UserCardListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        get_object_or_404(User, id=user_id)
        bindings = CardBinding.objects.filter(user_id=user_id).select_related("card", "user")
        return list_response(
            request,
            bindings,
            lambda item: {**binding_data(item), "card": card_data(item.card)},
        )


class CardListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return list_response(request, Card.objects.order_by("serial_no"), card_data)


class CardDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, card_id):
        return api_response(request, card_data(get_object_or_404(Card, id=card_id)))


class CardBindingListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, card_id):
        get_object_or_404(Card, id=card_id)
        bindings = CardBinding.objects.filter(card_id=card_id).select_related("user", "card")
        return list_response(request, bindings, binding_data)
