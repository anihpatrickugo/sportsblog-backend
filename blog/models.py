from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
import cloudinary
from cloudinary.models import CloudinaryField



# Create your models here.

Author = get_user_model()

class Category (models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name


class Post(models.Model):

    banner = CloudinaryField('banner')
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    tags = TaggableManager()

    # tags = ModelTagsManager()
    date = models.DateTimeField(auto_now=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def get_tags(self):
        return self.tags.all()



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=100000)
    blogger = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.message[0:30]