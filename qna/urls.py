from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.SignUp, name="qna-signup"),
    path("login/", views.Login, name="qna-login"),
    path("logout/", views.Logout, name="qna-logout"),
    path("", views.QuestionListView.as_view(), name="qna-home"),
    path(
        "question/<int:pk>",
        views.QuestionDetailView.as_view(),
        name="question",
    ),
    path(
        "unanswered/",
        views.UnanweredQuestionListView.as_view(),
        name="question-unanswered",
    ),
    path("question/add", views.addquestion, name="question-add"),
    path("question/<int:pk>/edit/", views.questionedit, name="question-edit"),
    path(
        "question/<int:pk>/delete/",
        views.questiondelete,
        name="question-delete",
    ),
    path(
        "question/<int:pk>/addcomment",
        views.addcomment,
        name="question-comment-add",
    ),
    path(
        "question/<int:pk>/questionvotemanager",
        views.questionvotemanager,
        name="question-questionvotemanager",
    ),
    path(
        "question/questionvotelistmanager",
        views.questionvotelistmanager,
        name="question-questionvotelistmanager",
    ),
    path("question/search/", views.QuestionSearch, name="qna-search"),
    path(
        "question/category/<slug:slug>",
        views.QuestionByCategory,
        name="question-categorywise",
    ),
    path(
        "user/category/add/",
        views.categorymanager,
        name="question-categorymanager",
    ),
    path("user/role/add/", views.rolemanager, name="question-rolemanager"),
    path(
        "question/<int:pk>/addanswer",
        views.addanswer,
        name="question-answer-add",
    ),
    path(
        "answer/<int:pk>/edit",
        views.editanswer,
        name="question-answer-edit",
    ),
    path(
        "answer/<int:pk>/delete/",
        views.deleteanswer,
        name="question-answer-delete",
    ),
    path(
        "question/<int:pk>/addanswercomment",
        views.addanswercomment,
        name="question-answer-comment-add",
    ),
    path(
        "question/answervotemanager",
        views.answervotemanager,
        name="question-answervotemanager",
    ),
    path("question/<int:pk>/flag/", views.questionflag, name="question-flag"),
    path("question/<int:pk>/hold/", views.questionhold, name="question-hold"),
    path(
        "question/<int:pk>/close/",
        views.questionclose,
        name="question-close",
    ),
    path("sendfeedback/", views.sendfeedback, name="question-sendfeedback"),
    path(
        "resolvedFeedback/",
        views.resolvedFeedback,
        name="question-feedback-resolved",
    ),
    path("adm/", views.FeedbackListView.as_view(), name="qna-admin-home"),
    path("adm/addcategory/", views.addcategory, name="question-addcategory"),
    path(
        "adm/category/<slug:slug>/edit",
        views.editcategory,
        name="question-editcategory",
    ),
    path(
        "adm/category/<slug:slug>/delete",
        views.deletecategory,
        name="question-deletecategory",
    ),
    path(
        "adm/categories/",
        views.CategoryListView.as_view(),
        name="question-category",
    ),
    path("adm/users/", views.UserListView.as_view(), name="question-user"),
    path(
        "adm/user/<int:pk>/delete",
        views.deleteuser,
        name="question-deleteuser",
    ),
    path(
        "adm/questions/",
        views.AdminQuestionListView.as_view(),
        name="question-question",
    ),
    path(
        "adm/qcomments/",
        views.QcommentListView.as_view(),
        name="question-qcomment",
    ),
    path(
        "adm/acomments/",
        views.AcommentListView.as_view(),
        name="question-acomment",
    ),
    path("user/<int:pk>/", views.UserDetails, name="qna-user"),
    path(
        "qcomment/delete",
        views.deleteqcomment,
        name="question-deleteqcomment",
    ),
    path(
        "acomment/delete",
        views.deleteacomment,
        name="question-deleteacomment",
    ),
]
