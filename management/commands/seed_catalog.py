from django.core.management.base import BaseCommand
from django.utils.text import slugify
from Catalogo.models import Category, Brand, Product
from usuarios.models import Usuario
from faker import Faker
import random

class Command(Base
