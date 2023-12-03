from django.contrib.auth.mixins import LoginRequiredMixin

import graphene

from graphql import GraphQLError

from graphene_django import DjangoObjectType
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations

import graphql_social_auth

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




class PostType(DjangoObjectType):
    comments = graphene.List(CommentType)

    class Meta:
        model = Post
        # fields = "__all__"

    def resolve_comments(self, info):
        comments = Comment.objects.filter(post=self.id)
        return  comments





class Query(UserQuery, MeQuery, graphene.ObjectType):
    popular_posts = graphene.List(PostType)
    top_stories = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, id=graphene.Int(required=True))

    all_categories = graphene.List(CategoryType)
    category_by_id = graphene.Field(CategoryType, id=graphene.Int(required=True))

    def resolve_popular_posts(root, info):
        # We can easily optimize query count in the resolve method
        return Post.objects.all()


    def resolve_top_stories(root, info):
        # We can easily optimize query count in the resolve method
        return Post.objects.extra(select={'length':'Length(title)'}).order_by('length')

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


class CommentMutation(LoginRequiredMixin, graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        post_id = graphene.Int(required=True)
        message = graphene.String(required=True)


    # The class attributes define the response of the mutation
    comment = graphene.Field(CommentType)

    @classmethod
    def mutate(cls, root, info, post_id, message):

        if info.context.user.is_authenticated:
            post = Post.objects.get(id=post_id)
            blogger = info.context.user

            comment = Comment.objects.create(post=post, message=message, blogger=blogger)
            comment.save()
            # Notice we return an instance of this mutation
            return CommentMutation(comment=comment)

        raise GraphQLError('You must be logged in to Comment!')



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
    social_auth = graphql_social_auth.SocialAuth.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)