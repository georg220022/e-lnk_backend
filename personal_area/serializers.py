import base64
from elink_index.generator_code import GeneratorShortCode
from elink_index.qr_generator import QrGenerator
from elink_index.models import LinkRegUser
from django.db import IntegrityError
from users.models import User
from django.utils import timezone
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from elink.settings import SITE_NAME

class LinkAuthSerializer(serializers.ModelSerializer):