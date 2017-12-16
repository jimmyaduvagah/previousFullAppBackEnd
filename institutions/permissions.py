from rest_framework import permissions

class IsAllowedOrSuperuser(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser or request.user.is_staff:
            return True

        if obj.created_by == request.user.id:
            return True
        else:
            return False


