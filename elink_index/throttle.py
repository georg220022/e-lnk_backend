from rest_framework.throttling import (UserRateThrottle,
                                       AnonRateThrottle)


class CreateLinkAnonymousThrottle(AnonRateThrottle):
    scope = 'create_link_anonym'

class CreateLinkUserThrottle(UserRateThrottle):
    scope = 'create_link_user'

class TryPasswordAnonymousThrottle(AnonRateThrottle):
    scope = 'anon_pass_try'

class TryPasswordUserThrottle(UserRateThrottle):
    scope = 'user_pass_try'

class RegistrationAnonymousThrottle(AnonRateThrottle):
    scope = 'anon_registration'

class Throttle_create_link:

    def choices_methods(obj_self):
        if obj_self.action == 'create_link':
            throttle_classes = [CreateLinkAnonymousThrottle,
                                CreateLinkUserThrottle]
        elif obj_self.action == 'open_link_pass':
                throttle_classes = [TryPasswordAnonymousThrottle,
                                    TryPasswordUserThrottle]
        else:
            throttle_classes = [UserRateThrottle, AnonRateThrottle]
        return [throttle() for throttle in throttle_classes]