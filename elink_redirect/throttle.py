from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class PassAnonymousThrottle(AnonRateThrottle):
    scope = "pass_open_anon"


class PassLinkUserThrottle(UserRateThrottle):
    scope = "pass_open_user"
