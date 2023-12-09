from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

import graphene


from graphql import GraphQLError

from graphene_django import DjangoObjectType
from graphene_django import DjangoListField
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations

import graphql_social_auth

from taggit.managers import TaggableManager
# from tag_fields.models import ModelTag

from blog.models import Category, Post, Comment
from blog.converters import convert_taggable_manager
User = get_user_model()


class BloggerType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class CommentType(DjangoObjectType):
    blogger = graphene.Field(BloggerType)

    class Meta:
        model = Comment
        fields = "__all__"

    def resolve_blogger(self, info):
        comment = Comment.objects.get(id=self.id)
        blogger = comment.blogger
        return  blogger




class PostType(DjangoObjectType):
    comments = graphene.List(CommentType)
    tags = TaggableManager()
    # tags = graphene.List(convert_taggable_manager(field=None))

    class Meta:
        model = Post
        # fields = "__all__"
        # exclude = ['tags']

    def resolve_comments(self, info):
        comments = Comment.objects.filter(post=self.id).reverse()
        return  comments

class Query(UserQuery, MeQuery, graphene.ObjectType):
    popular_posts = graphene.List(PostType)
    top_stories = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, id=graphene.Int(required=True))

    all_categories = graphene.List(CategoryType)
    category_by_id = graphene.Field(CategoryType, id=graphene.Int(required=True))

    def resolve_popular_posts(root, info):
        # We can easily optimize query count in the resolve method
        return Post.objects.all().order_by('-id')[0:6]


    def resolve_top_stories(root, info):
        # We can easily optimize query count in the resolve method
        return Post.objects.extra(select={'length':'Length(title)'}).order_by('length')[0:8]

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


class CommentMutation(graphene.Mutation):

    class Arguments:
        # The input arguments for this mutation
        username = graphene.String(required=True)
        post_id = graphene.Int(required=True)
        message = graphene.String(required=True)


    # The class attributes define the response of the mutation
    comment = graphene.Field(CommentType)

    @classmethod
    def mutate(cls, root, info, username, post_id, message):
        post = Post.objects.get(id=post_id)

        try:
            blogger = get_object_or_404(User, username=username)

        except :
            raise  GraphQLError("User does not exist")

        comment = Comment.objects.create(post=post, message=message, blogger=blogger)
        comment.save()
        # Notice we return an instance of this mutation
        return CommentMutation(comment=comment)









class AuthMutation(graphene.ObjectType):

    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_set = mutations.PasswordSet.Field() # For passwordless registration
    password_change = mutations.PasswordChange.Field()
    update_account = mutations.UpdateAccount.Field()
    archive_account = mutations.ArchiveAccount.Field()
    delete_account = mutations.DeleteAccount.Field()
    send_secondary_email_activation =  mutations.SendSecondaryEmailActivation.Field()
    verify_secondary_email = mutations.VerifySecondaryEmail.Field()
    swap_emails = mutations.SwapEmails.Field()
    remove_secondary_email = mutations.RemoveSecondaryEmail.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()



class Mutation(AuthMutation, graphene.ObjectType):
    make_comment = CommentMutation.Field()
    social_auth = graphql_social_auth.SocialAuthJWT.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)