from connections.views_rest import ConnectionViewSet, ConnectionRequestViewSet
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.views import static
from attachments.views import AttachmentViewSet
from cms_locations.views import CountryViewSet, StateViewSet
from course_module_sections.views_rest import CourseModuleSectionViewSet, SectionVideoContainerViewSet, \
    SectionTextViewSet, SectionQuizViewSet, SectionAttachmentViewSet, SectionImageViewSet, SectionGalleryViewSet, \
    SectionAssessmentViewSet, SectionTypesViewSet, SectionSurveyGroupViewSet
from courses.views_rest import CourseViewSet, CourseCategoryViewSet, CourseModuleViewSet, CourseProgressViewSet
from dev_issues.views import DevIssuesViewSet
from drf_users.views import UserViewSet, UserProfileViewSet, UserProfilesViewSet, UsernameTestViewSet, UserRegisterViewSet, UserProfileImageViewSet, GroupViewSet, \
    PeopleViewSet, PushTokenViewSet, UserLogoutViewSet
from drf_users.views_admin import UserAdminViewSet, InvidationCodesViewSet
from drf_users.views_authentication import login_view, obtain_auth_token, token_test
from images.views_rest import ImageViewSet, GalleryImageViewSet, GalleryViewSet, BeardViewSet
from learning_experience_submissions.views import LESubmissionViewSet, LESubmissionRatingViewSet
from nationalities.views import NationalitiesViewSet
from notifications.views import NotificationViewset
from posts.views import PostViewset, CommentViewset, PostLikeViewset, PostCreationViewset, PostReportViewset
from quizzes.views_rest import QuizViewSet, QuizQuestionViewSet, QuizQuestionAnswerViewSet
from reviews.views import ReviewViewSet, ReviewTemplateViewSet
from surveys.views_rest import SurveyViewSet, SurveyResponseViewSet
from tags.views import TagViewset
from towns.views import TownsViewSet
from twz_server_django.settings import HOMEPAGE_URL
from not_found.views import NotFoundViewSet
from password_resets.views import PasswordResetTokenViewSet
from twz_server_django.test import test_callback
from vimeo_api.views import VimeoViewSet, VimeoVideoView
from attachments.views_admin import AttachmentAdminViewSet
from django.views.generic import RedirectView

from institutions.views import InstitutionTypeViewSet, InstitutionViewSet
from institutions.views_admin import InstitutionTypeAdminViewSet, InstitutionAdminViewSet
from user_experience.views import UserProfileExperienceTypeViewSet, UserProfileExperienceViewSet
from user_experience.views_admin import  UserProfileExperienceTypeAdminViewSet, UserProfileExperienceAdminViewSet
from rest_framework_nested import routers

from twz_server_django import settings

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')
router.register(r'user-forgot-password', PasswordResetTokenViewSet, base_name='user-forgot-password')
router.register(r'user-profiles', UserProfilesViewSet, base_name='user-profiles')
router.register(r'user-profile', UserProfileViewSet, base_name='user-profile')
router.register(r'user-profile-image', UserProfileImageViewSet, base_name='user-profile-image')
router.register(r'groups', GroupViewSet, base_name='groups')
router.register(r'countries', CountryViewSet, base_name='countries')
router.register(r'states', StateViewSet, base_name='states')
router.register(r'institution-types', InstitutionTypeViewSet, base_name='institution-types')
router.register(r'institutions', InstitutionViewSet, base_name='institutions')
router.register(r'user-profile-experience-types', UserProfileExperienceTypeViewSet, base_name='user-profile-experience-types')
router.register(r'user-profile-experiences', UserProfileExperienceViewSet, base_name='user-profile-experiences')
router.register(r'username-test', UsernameTestViewSet, base_name='username-test')
router.register(r'push-tokens', PushTokenViewSet, base_name='push-tokens')
router.register(r'auth-register', UserRegisterViewSet, base_name='auth-register')
router.register(r'towns', TownsViewSet, base_name='towns')
router.register(r'nationalities', NationalitiesViewSet, base_name='nationalities')
router.register(r'posts', PostViewset, base_name='posts')
router.register(r'post-creation', PostCreationViewset, base_name='post-creation')
router.register(r'post-reports', PostReportViewset, base_name='post-reports')
router.register(r'likes', PostLikeViewset, base_name='likes')
router.register(r'course-progress', CourseProgressViewSet, base_name='course-progress')
router.register(r'courses', CourseViewSet, base_name='courses')
router.register(r'course-categories', CourseCategoryViewSet, base_name='course-categories')
router.register(r'course-modules', CourseModuleViewSet, base_name='course-modules')
router.register(r'images', ImageViewSet, base_name='images')
router.register(r'galleries', GalleryViewSet, base_name='galleries')
router.register(r'gallery-images', GalleryImageViewSet, base_name='gallery-images')

router.register(r'quizzes', QuizViewSet, base_name='quizzes')
router.register(r'quiz-questions', QuizQuestionViewSet, base_name='quiz-questions')
router.register(r'quiz-question-answers', QuizQuestionAnswerViewSet, base_name='quiz-question-answers')

router.register(r'connections', ConnectionViewSet, base_name='connections')
router.register(r'connection-requests', ConnectionRequestViewSet, base_name='connection-requests')
router.register(r'people', PeopleViewSet, base_name='people')

router.register(r'course-module-sections', CourseModuleSectionViewSet, base_name='course-module-sections')
router.register(r'section-video-containers', SectionVideoContainerViewSet, base_name='section-video-containers')
router.register(r'section-texts', SectionTextViewSet, base_name='section-texts')
router.register(r'section-quizzes', SectionQuizViewSet, base_name='section-quizzes')
router.register(r'section-attachments', SectionAttachmentViewSet, base_name='section-attachment')
router.register(r'section-images', SectionImageViewSet, base_name='section-images')
router.register(r'section-galleries', SectionGalleryViewSet, base_name='section-galleries')
router.register(r'section-assessments', SectionAssessmentViewSet, base_name='section-assessments')
router.register(r'section-types', SectionTypesViewSet, base_name='section-types')
router.register(r'section-survey-group', SectionSurveyGroupViewSet, base_name='section-survey-group')

router.register(r'reviews', ReviewViewSet, base_name='reviews')
router.register(r'review-templates', ReviewTemplateViewSet, base_name='review-templates')

router.register(r'notifications', NotificationViewset, base_name='notifications')
router.register(r'tags', TagViewset, base_name='tags')

router.register(r'beards', BeardViewSet, base_name='beards')

router.register(r'rest-logout', UserLogoutViewSet, base_name='rest-logout')
router.register(r'dev-issues', DevIssuesViewSet, base_name='dev-issues')


router.register(r'surveys', SurveyViewSet, base_name='surveys')
router.register(r'survey-responses', SurveyResponseViewSet, base_name='survey-responses')

router.register(r'le-submissions', LESubmissionViewSet, base_name='le-submissions')
router.register(r'le-submission-ratings', LESubmissionRatingViewSet, base_name='le-submission-ratings')

comments_router = routers.NestedSimpleRouter(router, r'posts', lookup='posts')
comments_router.register(r'comments', CommentViewset, base_name='comments')

# new for v2
router_v2 = DefaultRouter()
# codebase not updated
router_v2.register(r'users', UserViewSet, base_name='v2_users')
router_v2.register(r'username-test', UsernameTestViewSet, base_name='v2_username-test')
router_v2.register(r'auth-register', UserRegisterViewSet, base_name='v2_auth-register')
router_v2.register(r'user-forgot-password', PasswordResetTokenViewSet, base_name='v2_user-forgot-password')
router_v2.register(r'user-profiles', UserProfilesViewSet, base_name='v2_user-profiles')
router_v2.register(r'user-profile', UserProfileViewSet, base_name='v2_user-profile')
router_v2.register(r'user-profile-image', UserProfileImageViewSet, base_name='v2_user-profile-image')


admin_router = DefaultRouter()
admin_router.register(r'users', UserAdminViewSet, base_name="admin-users")
admin_router.register(r'attachments', AttachmentAdminViewSet, base_name="admin-attachments")
admin_router.register(r'institution-types', InstitutionTypeAdminViewSet, base_name="admin-institution-types")
admin_router.register(r'institutions', InstitutionAdminViewSet, base_name="admin-institutions")
admin_router.register(r'user-profile-experience-types', UserProfileExperienceTypeViewSet, base_name="admin-user-profile-experience-types")
admin_router.register(r'user-profile-experiences', UserProfileExperienceViewSet, base_name="admin-user-profile-experiences")
admin_router.register(r'invitation-codes', InvidationCodesViewSet, base_name="invitation-codes")

#codebase updated

# new components
router_v2.register(r'attachments', AttachmentViewSet, base_name='v2_attachments')

admin_router_v2 = DefaultRouter()

not_found_router = DefaultRouter()


urlpatterns = [
    url('^', include('django.contrib.auth.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', RedirectView.as_view(url=HOMEPAGE_URL)),
    url(r'^api/v2/', include(router_v2.urls)),
    url(r'^api/v2/admin/', include(admin_router_v2.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include(comments_router.urls)),
    url(r'^api/v1/admin/', include(admin_router.urls)),
    url(r'^api/v1/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/api-token-auth/', obtain_auth_token),
    url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
    url(r'^api/v1/vimeo/(?P<endpoint>.*)/', VimeoViewSet.as_view({'get': 'list'})),
    url(r'^api/v1/*/', NotFoundViewSet.as_view({'get': 'list'})),
    url(r'^vimeo-video/(?P<vimeo_id>[0-9]+)/$', VimeoVideoView.as_view(), name='vimeo_video'),
    url(r'^auth/login/', login_view),
    url(r'^auth/token-test/', token_test),
    url(r'^mpesa/callback/', test_callback),

]




if settings.DEBUG:
    urlpatterns.append(
        url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT, 'show_indexes':True})
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
