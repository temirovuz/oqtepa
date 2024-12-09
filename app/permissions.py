from rest_framework.permissions import BasePermission, SAFE_METHODS


# class IsAdminOrWaiter(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return getattr(request.user, 'role', None) in ['admin', 'waiter']

class IsAdminOrWaiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                    request.user.is_staff or request.user.groups.filter(name='Waiter').exists())
