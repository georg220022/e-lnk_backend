from rest_framework import permissions


class Permissons:

    def choices_methods(obj_self):
        if (obj_self.action == 'create_link' or
                obj_self.action == 'open_link_pass'):
            permission_classes = [permissions.AllowAny]
        elif (obj_self.action == 'delete_link' or
                obj_self.action == 'update_description'):
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
