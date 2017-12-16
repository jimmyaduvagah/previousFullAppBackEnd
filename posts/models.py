import json

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from drf_users.models import PushToken
from ionic_api import request
from ionic_api.objects import IonicPushNotification
from ionic_api.request import PushNotificationRequest
from notifications.models import Notification
from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager
from twz_server_django.notification_types import NOTIFICATION_TYPES
from twz_server_django.settings_private import IONIC_PUSH_GROUP


class PostManagerWithLike(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        qs = super(PostManagerWithLike, self).get_queryset()
        qs = qs.extra(
                select={'my_like': "SELECT id FROM posts_postlike WHERE posts_postlike.post_id = posts_post.id AND posts_postlike.created_by_id = %s"},
                select_params=(user_id, )
            )

        return qs


class Post(CreatedModifiedModel):
    objects_with_my_like = PostManagerWithLike()

    TEXT_TYPE = 1
    LINK_TYPE = 2
    LINK_SMALL_IMAGE_TYPE = 3
    IMAGE_TYPE = 4
    COURSE_TYPE = 5
    ACHIEVEMENT_TYPE = 6
    POST_TYPE_CHOICES = (
        (TEXT_TYPE, 'text'),
        (LINK_TYPE, 'link'),
        (LINK_SMALL_IMAGE_TYPE, 'link-small-image'),
        (IMAGE_TYPE, 'image'),
        (COURSE_TYPE, 'course'),
        (ACHIEVEMENT_TYPE, 'achievement')
    )
    post_type = models.IntegerField(choices=POST_TYPE_CHOICES, default=TEXT_TYPE, blank=False, null=False)

    parent_post = models.ForeignKey('posts.Post', blank=True, null=True)

    text_content = models.TextField(blank=True, null=False)

    # liking other objects to a post.  Can be for things like 'links', photos, courses, etc.
    linked_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    linked_object_id = models.UUIDField(blank=True, null=True)
    linked_content_object = GenericForeignKey('linked_content_type', 'linked_object_id')

    # liking post to other objects.  Can be for having posts associated with any object in the system
    associated_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True, related_name='post_associated_type')
    associated_object_id = models.UUIDField(blank=True, null=True)
    associated_object = GenericForeignKey('associated_type', 'associated_object_id')

    # has_link = models.BooleanField()

    likes_count = models.IntegerField(default=0, null=False, blank=False)
    shares_count = models.IntegerField(default=0, null=False, blank=False)
    comments_count = models.IntegerField(default=0, null=False, blank=False)
    reported = models.IntegerField(default=0, null=False, blank=False)

    number_of_edits = models.IntegerField(default=0, null=False, blank=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return '%s\'s %s at %s' % (self.created_by, self.get_post_type_display(), self.created_on)

    # TODO: Add this to a celery task or something.  Too slow to do on every save.
    def update_comment_count(self, to_save=False):
        changed = False
        new_count = Post.objects.filter(parent_post_id=self.id).count()
        if self.comments_count != new_count:
            changed = True
            self.comments_count = new_count

        if to_save and changed:
            self.save()

        return self.comments_count

    # TODO: Add this to a celery task or something.  Too slow to do on every save.
    def update_like_count(self, to_save=False):
        changed = False
        new_count = PostLike.objects.filter(post_id=self.id).count()

        if self.likes_count != new_count:
            changed = True
            self.likes_count = new_count

        if to_save and changed:
            self.save()

        return self.likes_count

    def increment_social_interaction(self, interaction, to_save=False):
        """
        :param interaction: this should be a string that is the name of the
        interaction field (likes_count, shares_count, comments_count).
        :param to_save: if we should save the object or not, defaults
        to false so it can be used on another method that already calls save.
        :return: returns the updated count.
        """
        count = setattr(self, interaction, getattr(self, interaction)+1)

        if to_save:
            self.save(from_social=True)

        return count

    def decrement_social_interaction(self, interaction, to_save=False):
        """
        :param interaction: this should be a string that is the name of the
        interaction field (likes_count, shares_count, comments_count).
        :param to_save: if we should save the object or not, defaults
        to false so it can be used on another method that already calls save.
        :return: returns the updated count.
        """
        count = setattr(self, interaction, getattr(self, interaction) - 1)

        if to_save:
            self.save(from_social=True)

        return count

    def save(self, *args, **kwargs):
        from_social = kwargs.pop('from_social', False)
        super(Post, self).save(*args, **kwargs)

        if self.parent_post and not from_social:
            self.parent_post.increment_social_interaction('comments_count', to_save=True)


class PostLike(CreatedModifiedModel):
    post = models.ForeignKey('posts.Post', blank=False, null=False, related_name='post_like_post')

    class Meta:
        unique_together = (("post", "created_by"),)

    def __str__(self):
        return '%s\'s like of %s' % (self.created_by, self.post)

    def save(self, *args, **kwargs):
        super(PostLike, self).save(*args, **kwargs)
        self.post.increment_social_interaction('likes_count', to_save=True)

        tokens_for_parent_post_creator_qs = PushToken.objects.filter(user=self.post.created_by,
                                                                     push_group=IONIC_PUSH_GROUP,
                                                                     is_active=True).values_list('token').exclude(user=self.created_by_id)
        tokens_for_parent_post_creator = list()
        for token in tokens_for_parent_post_creator_qs:
            tokens_for_parent_post_creator.append(token[0])

        if self.post.parent_post_id:
            payload = {
                "post_id": str(self.post.parent_post_id),
                "comment_id": str(self.post.id),
                "image": self.created_by.get_profile_image_cache_url(),
                "created_by_id": str(self.created_by_id),
                "type": NOTIFICATION_TYPES.NEW_LIKE
            }
        else:
            payload = {
                "post_id": str(self.post_id),
                "image": self.created_by.get_profile_image_cache_url(),
                "created_by_id": str(self.created_by_id),
                "type": NOTIFICATION_TYPES.NEW_LIKE
            }
        title = "%s likes your post" % self.created_by
        message = "Click here to view it"

        notif = Notification(to_user=self.post.created_by,
                             from_user=self.created_by,
                             created_on=timezone.datetime.now(),
                             title=title,
                             message=message,
                             payload=payload)
        notif.save()
        if len(tokens_for_parent_post_creator) > 0:
            r = PushNotificationRequest()
            r.create({
                "tokens": tokens_for_parent_post_creator,
                "notification": {
                    "message": message,
                    "title": title,
                    "payload": payload,
                    "ios": {
                        "badge": "1",
                        "sound": "default",
                        "priority": 10
                    },
                    "android": {
                        "sound": "default",
                        "priority": "high"
                    }
                },
                "profile": IONIC_PUSH_GROUP
            })

    def delete(self, *args, **kwargs):
        self.post.decrement_social_interaction('likes_count', to_save=True)
        super(PostLike, self).delete(*args, **kwargs)


class PostReport(CreatedModifiedModel):
    post = models.ForeignKey('posts.Post', blank=False, null=False, related_name='post_reported')

    def __str__(self):
        return '%s\'s report of %s' % (self.created_by, self.post)

    def save(self, *args, **kwargs):
        super(PostReport, self).save(*args, **kwargs)
        self.post.increment_social_interaction('reported', to_save=True)

    def delete(self, *args, **kwargs):
        self.post.reported -= 1
        self.post.save()
        super(PostReport, self).delete(*args, **kwargs)
