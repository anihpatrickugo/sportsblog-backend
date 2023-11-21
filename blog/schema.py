import graphene
from graphene_django import DjangoObjectType

# from taggit.models import Tag
from blog.models import Category, Post, Comment

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"
        # exclude = ("tags",)
class PostType(DjangoObjectType):
    comments = graphene.List(CommentType)

    class Meta:
        model = Post
        # fields = "__all__"
        exclude = ("tags",)

    def resolve_comments(self, info):
        comments = Comment.objects.filter(post=self.id)
        return  comments





class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, id=graphene.Int(required=True))

    all_categories = graphene.List(CategoryType)
    category_by_id = graphene.Field(CategoryType, id=graphene.Int(required=True))

    def resolve_all_posts(root, info):
        # We can easily optimize query count in the resolve method
        return Post.objects.all()

    def resolve_post_by_id(root, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_category_by_id(root, info, id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            return None

schema = graphene.Schema(query=Query)