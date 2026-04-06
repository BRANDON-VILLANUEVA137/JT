from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from django.db import models
import os
from pathlib import Path
from cloudinary.uploader import upload

class Command(BaseCommand):
    help
