from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            if request.user.role == 3:
                return True
            else:
                return False
        except:
            return False
    
class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            if request.user.role >= 2:
                return True
            else:
                return False
        except:
            return False