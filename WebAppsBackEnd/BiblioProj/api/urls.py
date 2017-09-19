from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

resource_patterns = [
    url(r'^answers/?$', views.AnswerResource.as_view()),
    url(r'^comments/?$', views.CommentResource.as_view()),
]


edit_patterns = [
    url(r'^answer/?$', views.AnswerEdit.as_view()),
    url(r'^comment/?$', views.CommentEdit.as_view()),
]

edit_patterns = format_suffix_patterns(edit_patterns, allowed=['json', 'html'])

create_delete_get_patterns = [
    url(r'^answer/?$', views.Answers.as_view()),
    url(r'^comment/?$', views.Comments.as_view()),
    url(r'^paper/?$', views.PaperPDF.as_view()),
    url(r'^(?P<paper_id>[0-9]+)/questions/?$', views.PaperQuestions.as_view()),
]

create_delete_get_patterns = format_suffix_patterns(create_delete_get_patterns, allowed=['json', 'html'])

paper_info_patterns = [
    url(r'^paper/?$', views.PaperPDF.as_view()),
    url(r'^questions/?$', views.PaperQuestions.as_view()),
]

register_patterns = [
    url(r'^student/?$', views.RegStudent.as_view()),
    url(r'^staff/?$', views.RegStaff.as_view())
]


urlpatterns = [
    url(r'^available-papers/?', views.AvailablePapers.as_view()),
    url(r'^(?P<course_code>[A-Z][0-9]{3})/(?P<year>[0-9]{4})/', include(paper_info_patterns)),
    url(r'^(?P<id>[0-9]+)/(?P<resource_name>.*)/', include(resource_patterns)),
    url(r'^(?P<id>[0-9]+)/', include(create_delete_get_patterns)),
    url(r'^submit/', include(create_delete_get_patterns)),
    url(r'^update/', include(edit_patterns)),
    url(r'^delete/(?P<pk>[0-9]+)/', include(create_delete_get_patterns)),
    url(r'^upvote/(?P<answer_id>[0-9]+)/?$', views.UpVote.as_view()),
    url(r'^downvote/(?P<answer_id>[0-9]+)/?$', views.DownVote.as_view()),
    url(r'^register/', include(register_patterns)),
    url(r'^auth/?$', views.LogInUser.as_view()),
]
