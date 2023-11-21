from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget

from blog.models import Category, Post, Comment

class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        model = Category
        filter = ["name"]


class CommentAdmin(admin.ModelAdmin):
    class Meta:
        model = Comment
        filter = ["date"]


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Post
        fields = '__all__'



class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)