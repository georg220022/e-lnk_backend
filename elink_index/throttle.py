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

class Throttle_create_link:

    def choices_throttle_methods(obj_self):
        if obj_self.action == 'create_link':
            #if obj_self.request.user.is_anonymous:
            throttle_classes = [CreateLinkAnonymousThrottle,
                                CreateLinkUserThrottle]
            #else:
            #    throttle_classes = [,]
        elif obj_self.action == 'open_link_pass':
            #if obj_self.request.user.is_anonymous:
                throttle_classes = [TryPasswordAnonymousThrottle,
                                    TryPasswordUserThrottle]
            #else:
            #    throttle_classes = [TryPasswordUserThrottle,]
        else:
            throttle_classes = [UserRateThrottle, AnonRateThrottle]
        return [throttle() for throttle in throttle_classes]