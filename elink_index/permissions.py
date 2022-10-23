from rest_framework import permissions


class Permissons:
    """Выбираем permissons в зависимости от вызванной функции"""

    @staticmethod
    def choices_methods(obj_self_action: str) -> permissions:
        if obj_self_action == "create_link" or obj_self_action == "open_link_pass":
            permission_classes = [permissions.AllowAny]
        elif (
            obj_self_action == "delete_link"
            or obj_self_action == "update_descrip_or_pass_lnk"
        ):
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
