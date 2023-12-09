from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager
from graphene import String, List

@convert_django_field.register(TaggableManager)
def convert_taggable_manager(field, registry=None):
    return List(String, source='get_tags')