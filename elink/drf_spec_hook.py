def exclude_path_format(endpoints, **kwargs):
    """Убираем лишние эндпоинты из документации swagger"""
    new_endpoint = []
    white_list = ["/api/v1/login", "/api/v1/panel", "/api/v1/links", "POST", "GET"]
    for obj_endpoint in endpoints:
        if obj_endpoint[0] in white_list:
            if obj_endpoint[2] in white_list:
                new_endpoint.append(obj_endpoint)
    endpoints = new_endpoint
    return endpoints
