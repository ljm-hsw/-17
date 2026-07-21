from .models import CardBinding


def list_user_bindings(user, include_history=False):
    queryset = CardBinding.objects.filter(user=user).select_related("card")
    if not include_history:
        queryset = queryset.filter(unbound_at__isnull=True)
    return queryset.order_by("-is_primary", "-bound_at")
