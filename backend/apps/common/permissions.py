from rest_framework.permissions import SAFE_METHODS, BasePermission


class HasManagementModelPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_staff:
            return False
        if request.method in SAFE_METHODS:
            return True
        model = getattr(view, "management_model", None)
        permission_action = getattr(view, "permission_action", None)
        if model is None:
            return False
        if permission_action is None:
            permission_action = "add" if request.method == "POST" else "change"
        permission = f"{model._meta.app_label}.{permission_action}_{model._meta.model_name}"
        return user.has_perm(permission)
