from graphene_django.converter import convert_django_field
from graphene import String, List, Int, ObjectType
from taggit.managers import TaggableManager
from cloudinary.models import CloudinaryField


class BannerType(ObjectType):
    url = String()
    width = Int()
    height = Int()


@convert_django_field.register(TaggableManager)
def convert_taggable_manager(field, registry=None):
    return List(String, source='get_tags')


@convert_django_field.register(CloudinaryField)
def convert_cloudinary_field(field, registry=None):
    # Define the GraphQL type you want to use for the CloudinaryField
    # For example, you could use a String type for the image URL
    # return String()
    return BannerType()