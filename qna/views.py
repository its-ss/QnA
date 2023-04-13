import random
import string
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Acomment,
    Answer,
    Category,
    Feedback,
    Qcomment,
    Question,
    QuestionStatusHistory,
    Role,
)


def SignUp(request):
    if request.user.is_authenticated:
        return redirect("qna-home")
    else:
        if request.method == "POST":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            confirmpassword = request.POST.get("confirmpassword", "")

            if password != confirmpassword:
                error = "Both passwords are not same"
                return render(request, "qna/signup.html", {"error": error})

            if (
                len(username) > 30
                or len(username) < 4
                or len(
                    password,
                )
                > 30
                or len(password) < 4
            ):
                error = (
                    "Username and password should be min 4 and max 30 character longer."
                )
                return render(request, "qna/signup.html", {"error": error})

            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                )
                login(request, user)
                return redirect("qna-home")
            except IntegrityError:
                error = "Username already exist with same username"
                return render(request, "qna/signup.html", {"error": error})
        else:
            return render(request, "qna/signup.html")


def Login(request):
    if request.user.is_authenticated:
        return redirect("qna-home")
    else:
        if request.method == "POST":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            if (
                len(username) > 30
                or len(username) < 4
                or len(
                    password,
                )
                > 30
                or len(password) < 4
            ):
                error ="Username and password should be min 4 and max 30 character longer."
                return render(request, "qna/login.html", {"error": error})
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.GET.get("next"):
                    next = request.GET.get("next")
                    return redirect(next)
                return redirect("qna-home")

            else:
                error = "Username and password doesnt match"
                return render(request, "qna/login.html", {"error": error})
        else:
            return render(request, "qna/login.html")


def Logout(request):
    logout(request)
    return redirect("qna-home")


def UserDetails(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, "qna/user.html", {"profile_user": user})


class QuestionListView(generic.ListView):
    model = Question
    template_name = "qna/index.html"
    context_object_name = "questions"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trendingcategories"] = getTrendingCategory()
        if self.request.user.is_authenticated:
            ucategories = userscategories(self.request.user)
            context["userscategories"] = ucategories
        else:
            context["userscategories"] = None

        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            questions = Question.objects.none()
            ucategories = userscategories(self.request.user)
            for catquestion in ucategories:
                questions = questions | catquestion.categoryOfQuestion.all()
            questions = questions.distinct()

            questions = sorted(
                questions.exclude(answer__isnull=True).exclude(status="c"),
                key=lambda x: random.random(),
            )

            if questions:
                return questions
            else:
                return sorted(
                    Question.objects.exclude(
                        answer__isnull=True,
                    ).exclude(status="c"),
                    key=lambda x: random.random(),
                )

        else:
            return sorted(
                Question.objects.exclude(
                    answer__isnull=True,
                ).exclude(status="c"),
                key=lambda x: random.random(),
            )


class UnanweredQuestionListView(generic.ListView):
    model = Question
    template_name = "qna/unanswered_question.html"
    context_object_name = "questions"

    def get_queryset(self):
        return sorted(
            Question.objects.exclude(answer__isnull=False).exclude(status="c"),
            key=lambda x: random.random(),
        )


def common_category(usercategories, questioncategories):
    usercategories_set = set(usercategories)
    questioncategories_set = set(questioncategories)
    if len(usercategories_set.intersection(questioncategories_set)) > 0:
        return True
    return False


def getHasRole(user, questionscategories):
    if user.is_staff:
        return True
    userrole = user.profile.role.all()
    userrolecat = []
    for role in userrole.all():
        userrolecat.append(role.category)

    if common_category(userrolecat, questionscategories):
        return True
    else:
        return False


def getTrendingCategory():
    listwithvote = {}
    for c in Category.objects.all():
        qs = c.categoryOfQuestion.all()
        coins = 0
        for q in qs:
            coins += q.vote
            listwithvote[c] = coins
    listwithvote = sorted(
        listwithvote.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    listwithvote = listwithvote[0:5]
    categorylist = []
    for list in listwithvote:
        categorylist.append(list[0])

    return categorylist


def userscategories(user):
    return user.profile.category.all()


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime("%b. %e,  %Y  %l:%M %P")


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = "qna/question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questionscategories = self.object.category.all()
        hasRole = False
        isFlag = True if self.object.status == "f" else False
        isHold = True if self.object.status == "o" else False
        isClose = True if self.object.status == "c" else False
        if isHold or isClose:
            isFlag = True
        if self.request.user.is_authenticated:
            hasRole = getHasRole(self.request.user, questionscategories)
        context["questionscategories"] = questionscategories
        context["hasRole"] = hasRole
        context["isFlag"] = isFlag
        context["isHold"] = isHold
        context["isClose"] = isClose
        return context


@login_required(login_url="/login/")
def addquestion(request):
    if request.method == "POST":
        question = request.POST.get("question", "")
        categories = request.POST.getlist("category", "")

        if len(question) == 0 or len(question) > 1000 or len(question) < 10:
            error = "question should be min 10 and max 1000 character longer."
            return render(
                request,
                "qna/add-question.html",
                {
                    "error": error,
                    "categories": categories,
                },
            )

        def questionExist(question):
            q = Question.objects.filter(question=question)
            if q:
                return True
            else:
                return False

        if questionExist(question):
            error = (
                "Question already exist.Please be more specific or go to that question"
            )
            return render(
                request,
                "qna/add-question.html",
                {
                    "error": error,
                    "categories": categories,
                },
            )

        categorylist = []
        for category in categories:
            categorylist.append(
                Category.objects.filter(category=category).first(),
            )
        if len(categorylist) > 4:
            error = "Max 4 category allowed"
            return render(
                request,
                "qna/add-question.html",
                {
                    "error": error,
                    "categories": categories,
                },
            )

        user = request.user
        question = Question(question=question, user=user)
        question.save()

        for category in categorylist:
            question.category.add(category)

        question.save()
        return redirect("question", pk=question.id)
    else:
        categories = Category.objects.all()
        context = {"categories": categories}
        return render(request, "qna/add-question.html", context=context)


@login_required(login_url="/login/")
def questionedit(request, pk):
    question = Question.objects.get(pk=pk)
    categories = Category.objects.all()
    questionscategories = question.category.all()
    user = request.user
    if question.user == user or getHasRole(user, questionscategories):
        if request.method == "POST":
            updated_question = request.POST.get("question", "")
            updated_categories = request.POST.getlist("category", "")
            previous_question = question
            change = False

            if (
                len(updated_question) == 0
                or len(
                    updated_question,
                )
                > 1000
                or len(updated_question) < 10
            ):
                error = "question should be min 10 and max 1000 character longer."
                return render(
                    request,
                    "qna/edit-question.html",
                    {
                        "error": error,
                        "categories": categories,
                        "questionscategories": questionscategories,
                    },
                )
            if updated_question != previous_question.question:
                change = True

            categorylist = []
            for category in updated_categories:
                categorylist.append(
                    Category.objects.filter(category=category).first(),
                )

            if len(categorylist) > 4:
                error = "Max 4 category allowed"
                return render(
                    request,
                    "qna/edit-question.html",
                    {
                        "error": error,
                        "categories": categories,
                        "questionscategories": questionscategories,
                    },
                )

            new_categories = []
            if questionscategories:
                for category in questionscategories:
                    new_categories.append(category.category)
            if updated_categories:
                updated_categories.sort()
            else:
                updated_categories = []
            if new_categories:
                new_categories.sort()
            else:
                new_categories = []
            if updated_categories != new_categories:
                change = True

            if change:
                previous_question.question = updated_question
                previous_question.category.clear()
                if user not in previous_question.edit_user.all():
                    previous_question.edit_user.add(user)
                previous_question.save()
                for category in categorylist:
                    previous_question.category.add(category)
                previous_question.save()
                return redirect("question", pk=previous_question.id)
            else:
                error = "Previous question and this question is same."
                return render(
                    request,
                    "qna/edit-question.html",
                    {
                        "error": error,
                        "question": question,
                        "categories": categories,
                        "questionscategories": questionscategories,
                    },
                )
        else:
            return render(
                request,
                "qna/edit-question.html",
                {
                    "question": question,
                    "categories": categories,
                    "questionscategories": questionscategories,
                },
            )
    else:
        return redirect("question", pk=question.id)


@login_required(login_url="/login/")
def questiondelete(request, pk):
    question = Question.objects.get(pk=pk)
    user = request.user
    question.delete()
    return redirect('qna-home')


@login_required
@csrf_exempt
def addcomment(request, pk):
    question = Question.objects.get(pk=pk)
    user = request.user
    if request.method == "POST":
        comment = request.POST.get("qcomment", "")
        if len(comment) == 0 or len(comment) > 600:
            data = {"error": "Comment  should not be empty"}
            return JsonResponse(data)
        comment = Qcomment(qcomment=comment, question=question, user=user)
        comment.save()
        username = user.username

        created_at = aslocaltimestr(comment.created_at)
        data = {
            "comment": comment.qcomment,
            "username": username,
            "created_at": created_at,
            "added": True,
        }
        return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def questionvotemanager(request, pk):
    if request.method == "POST":
        request.user
        totalvote = request.POST.get("totalvote", "")
        question = Question.objects.get(pk=pk)
        question.user.profile.coins -= int(question.vote)
        question.vote = int(totalvote)
        question.save()
        question.user.profile.coins += int(question.vote)
        question.user.save()
        data = {"voted": True}
        return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def questionvotelistmanager(request):
    if request.method == "POST":
        request.user
        totalvote = request.POST.get("totalvote", "")
        questionid = request.POST.get("questionid", "")
        question = Question.objects.get(pk=questionid)

        question.vote = totalvote
        question.save()
        data = {"voted": True}
        return JsonResponse(data)
    else:
        return redirect("qna-home")


def QuestionSearch(request):
    questiontosearch = request.POST.get("questionsearch")
    questions = Question.objects.filter(
        Q(question__contains=questiontosearch)
        | Q(answer__answer__contains=questiontosearch),
    )
    return render(
        request,
        "qna/search-question.html",
        {
            "questiontosearch": questiontosearch,
            "questions": questions,
        },
    )


def QuestionByCategory(request, slug):
    category = Category.objects.filter(slug=slug).first()
    questions = category.categoryOfQuestion.all()
    hasRole = True
    isCategoryin = False
    if request.user.is_authenticated:
        ucategory = userscategories(request.user)
        if category in ucategory:
            isCategoryin = True
            hasRole = (
                True if category.role in request.user.profile.role.all() else False
            )
    return render(
        request,
        "qna/category-question.html",
        {
            "questions": questions,
            "category": category,
            "hasRole": hasRole,
            "isCategoryin": isCategoryin,
        },
    )


@login_required
def addanswer(request, pk):
    question = Question.objects.get(pk=pk)
    user = request.user

    allanswersonquestion = question.answer_set.all()

    allanswersusers = []
    for answer in allanswersonquestion:
        allanswersusers.append(answer.user)

    if question.user == user or user in allanswersusers:
        return redirect("question", pk=question.id)

    if question.status == "o" or question.status == "c":
        return redirect("question", pk=question.id)

    if request.method == "POST":
        answer = request.POST.get("answer", "")

        if len(answer) < 10 or len(answer) > 8000:
            error = "Answer cant be 10 character shorter or 8000 character longer"
            return render(
                request,
                "qna/add-answer.html",
                {
                    "error": error,
                    "question": question,
                    "answer": answer,
                },
            )

        answer = Answer(question=question, answer=answer, user=user)
        answer.save()
        return redirect("question", pk=question.id)
    else:
        return render(request, "qna/add-answer.html", {"question": question})


@login_required
def editanswer(request, pk):
    answer = Answer.objects.get(pk=pk)
    user = request.user
    questionscategories = answer.question.category.all()

    if answer.user == user or getHasRole(user, questionscategories):
        if request.method == "POST":
            previous_answer = answer
            change = False
            updated_answer = request.POST.get("answer", "")
            if len(updated_answer) < 10 or len(updated_answer) > 8000:
                error = "Answer cant be 10 character shorter or 8000 character longer"
                return render(
                    request,
                    "qna/edit-answer.html",
                    {
                        "error": error,
                        "answer": answer,
                        "updated_answer": updated_answer,
                    },
                )

            if updated_answer != previous_answer.answer:
                previous_answer.category = updated_answer
                change = True
            if change:
                previous_answer.answer = updated_answer
                previous_answer.save()
                if user not in previous_answer.edit_user.all():
                    previous_answer.edit_user.add(user)
                previous_answer.save()
                return redirect("question", pk=previous_answer.question.id)
            else:
                error = "Previous answer and this answer is same."
                return render(
                    request,
                    "qna/edit-answer.html",
                    {
                        "error": error,
                        "answer": answer,
                    },
                )
        else:
            return render(request, "qna/edit-answer.html", {"answer": answer})
    else:
        return redirect("question", pk=answer.question.id)


@login_required
def deleteanswer(request, pk):
    answer = Answer.objects.get(pk=pk)
    user = request.user
    questionscategories = answer.question.category.all()
    answer.delete()
    return redirect("qna-home")
    # if answer.user == user or getHasRole(user, questionscategories):
    #     if request.method == "POST":
    #         if request.POST.get("yes"):
    #             answer.delete()
    #             return redirect("qna-home")
    #         else:
    #             return redirect("question", pk=answer.question.id)
    #     else:
    #         return render(
    #             request,
    #             "qna/delete-answer.html",
    #             {"answer": answer},
    #         )
    # else:
    #     return redirect("question", pk=answer.question.id)


@login_required
@csrf_exempt
def addanswercomment(request, pk):
    if request.method == "POST":
        comment = request.POST.get("acomment", "")
        answerid = request.POST.get("answerid", "")
        answer = Answer.objects.get(pk=answerid)
        user = request.user
        username = user.username

        if len(comment) == 0 or len(comment) > 600:
            data = {"error": "Comment  should not be empty"}
            return JsonResponse(data)
        comment = Acomment(acomment=comment, answer=answer, user=user)
        comment.save()
        created_at = aslocaltimestr(comment.created_at)
        data = {
            "comment": comment.acomment,
            "username": username,
            "created_at": created_at,
            "added": True,
        }
        return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def questionflag(request, pk):
    question = Question.objects.get(pk=pk)
    if request.method == "POST":
        questionscategories = question.category.all()
        user = request.user
        if question.user == user:
            data = {
                "flag": False,
                "error": "Can't flag or unflag own question",
                "unflag": False,
            }
            return JsonResponse(data)

        if not getHasRole(user, questionscategories):
            data = {"error": "You don't have permission to flag question"}
            return JsonResponse(data)

        if question.status == "a":
            qshistory = QuestionStatusHistory(question=question, user=user)
            question.status = "f"
            qshistory.save()
            question.save()
            data = {"flag": True}
            return JsonResponse(data)
        elif question.status == "f":
            qshistory = QuestionStatusHistory.objects.get(question=question)
            if qshistory.user == user:
                data = {
                    "error": "You can't unflag this question because you flagged this question",
                }
                return JsonResponse(data)
            question.status = "a"
            qshistory.delete()
            question.save()
            data = {"unflag": True}
            return JsonResponse(data)
        elif question.status == "o":
            data = {"error": "Question is on hold"}
            return JsonResponse(data)
        elif question.status == "c":
            data = {"error": "Its Closed"}
            return JsonResponse(data)
        else:
            data = {"error": "Something went wrong"}
            return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def questionhold(request, pk):
    if request.method == "POST":
        question = Question.objects.get(pk=pk)
        questionscategories = question.category.all()

        user = request.user

        if not getHasRole(user, questionscategories):
            data = {
                "flag": False,
                "error": "Can't flag or unflag own question",
                "unflag": False,
            }
            return JsonResponse(data)

        if question.user == user:
            data = {"error": "Can't hold own question"}
            return JsonResponse(data)
        qshistory = QuestionStatusHistory.objects.get(question=question)

        if question.status == "f":
            if qshistory.user == user:
                data = {
                    "error": "You can't put this question on hold because you flagged this question",
                }
                return JsonResponse(data)
            qshistory.user = user
            question.status = "o"
            qshistory.save()
            question.save()
            data = {"onhold": True}
            return JsonResponse(data)
        elif question.status == "o":
            if qshistory.user == user:
                data = {
                    "error": "You can't off hold because you put this on hold",
                }
                return JsonResponse(data)
            question.status = "a"
            qshistory.delete()
            question.save()
            data = {"unflag": True}
            return JsonResponse(data)
        elif question.status == "c":
            data = {"error": "Question is Closed"}
            return JsonResponse(data)
        else:
            data = {"error": "Question has to be first flag"}
            return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def questionclose(request, pk):
    if request.method == "POST":
        question = Question.objects.get(pk=pk)
        questionscategories = question.category.all()
        user = request.user

        if not getHasRole(user, questionscategories):
            data = {
                "flag": False,
                "error": "Can't flag or unflag own question",
                "unflag": False,
            }
            return JsonResponse(data)

        if question.user == user:
            data = {"error": "You can't close or open own question"}
            return JsonResponse(data)

        qshistory = QuestionStatusHistory.objects.get(question=question)

        if question.status == "o" or question.status == "f":
            reason = request.POST.get("reason", "")
            if qshistory.user == user:
                data = {
                    "error": "You can't close this question becuase either you flagged this question or put on hold",
                }
                return JsonResponse(data)

            if len(reason) == 0 or len(reason) > 100 or len(reason) < 10:
                error = "question should be min 10 and max 100 character longer."
                data = {"error": error}
                return JsonResponse(data)

            qshistory.user = user
            qshistory.reason = reason
            question.status = "c"
            qshistory.save()
            question.save()
            data = {"close": True}
            return JsonResponse(data)
        elif question.status == "c":
            if qshistory.user == user:
                data = {
                    "error": "You can't open this question because you closed this question",
                }
                return JsonResponse(data)
            question.status = "a"
            qshistory.delete()
            question.save()
            data = {"unflag": True}
            return JsonResponse(data)
        else:
            data = {"error": "Question has to be first flag"}
            return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def answervotemanager(request):
    if request.method == "POST":
        request.user
        totalvote = request.POST.get("totalvote", "")
        answerid = request.POST.get("answerid", "")
        answer = Answer.objects.get(pk=answerid)
        answer.user.profile.coins -= int(answer.vote)
        answer.vote = int(totalvote)
        answer.save()
        answer.user.profile.coins += int(answer.vote)
        answer.user.save()
        data = {"voted": True}
        return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
def sendfeedback(request):
    if request.method == "POST":
        feedback = request.POST.get("feedback", "")

        if len(feedback) == 0 or len(feedback) > 1000:
            error = "Feedback should be max 3000 character longer."
            return render(request, "qna/send-feedback.html", {"error": error})

        def feedbackExist(feedback):
            q = Feedback.objects.filter(feedback=feedback)
            if q:
                return True
            else:
                return False

        if not feedbackExist(feedback):
            feedback = Feedback(feedback=feedback)
            feedback.save()
        return redirect("qna-home")
    else:
        return render(request, "qna/send-feedback.html")


@method_decorator(
    staff_member_required(login_url="/login"),
    name="dispatch",
)
class FeedbackListView(generic.ListView, LoginRequiredMixin):

    model = Feedback
    template_name = "qna/admin-index.html"
    context_object_name = "feedbacks"

    def get_queryset(self):
        return Feedback.objects.filter(resolved=False)


@staff_member_required(login_url="/login")
@login_required
@csrf_exempt
def resolvedFeedback(request):
    if request.method == "POST":
        id = request.POST.get("id", "")
        feedback = Feedback.objects.get(pk=id)
        feedback.resolved = True
        feedback.save()
        data = {"resolved": True}
        return JsonResponse(data)
    else:
        data = {"error": "Something went wrong"}


@staff_member_required(login_url="/login")
@login_required
def addcategory(request):
    if request.method == "POST":
        category = request.POST.get("category", "")
        role = request.POST.get("role", "")
        if (
            len(category) == 0
            or len(category) > 100
            or len(
                role,
            )
            == 0
            or len(role) > 100
        ):
            error = "Category or role should be max 100 character longer."
            return render(
                request,
                "qna/admin-add-category.html",
                {"error": error},
            )

        def categoryExist(category):
            q = Category.objects.filter(category=category)
            if q:
                return True
            else:
                return False

        if not categoryExist(category):
            category = Category(category=category)
            category.save()
            role = Role(category=category, role=role)
            role.save()
        else:
            error = "Category already exist."
            return render(
                request,
                "qna/admin-add-category.html",
                {"error": error},
            )

        return redirect("qna-admin-home")
    else:
        return render(request, "qna/admin-add-category.html")


@method_decorator(
    staff_member_required(login_url="/login"),
    name="dispatch",
)
class CategoryListView(generic.ListView, LoginRequiredMixin):
    model = Category
    context_object_name = "categories"
    template_name = "qna/admin-category.html"


@staff_member_required(login_url="/login")
@login_required
def editcategory(request, slug):
    category = Category.objects.get(slug=slug)
    if request.method == "POST":
        change = False
        error = ""
        updated_category = request.POST.get("category", "")
        updated_role = request.POST.get("role", "")
        previous_category = category

        if updated_category != previous_category.category:
            previous_category.category = updated_category
            change = True
        if updated_role != previous_category.role.role:
            previous_category.role.role = updated_role
            change = True

        if change:
            previous_category.save()
            previous_category.role.save()
            return redirect("question-category")
        else:
            error = "Previous category/role and this category/role is same."
            return render(
                request,
                "qna/admin-editcategory.html",
                {
                    "error": error,
                    "category": category,
                },
            )
    else:
        return render(
            request,
            "qna/admin-editcategory.html",
            {"category": category},
        )


@staff_member_required(login_url="/login")
@login_required
def deletecategory(request, slug):
    category = Category.objects.get(slug=slug)
    category.role.delete()
    category.delete()
    return redirect("question-category")

@method_decorator(
    staff_member_required(login_url="/login"),
    name="dispatch",
)
class UserListView(generic.ListView, LoginRequiredMixin):

    model = User
    template_name = "qna/admin-users.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().order_by("username")


def randomStringwithDigitsAndSymbols(stringLength=10):
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(password_characters) for i in range(stringLength))


@staff_member_required(login_url="/login")
@login_required
def deleteuser(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    return redirect('question-user')

@method_decorator(
    staff_member_required(login_url="/login"),
    name="dispatch",
)
class AdminQuestionListView(generic.ListView, LoginRequiredMixin):

    model = Question
    template_name = "qna/admin-question.html"
    context_object_name = "questions"

    def get_queryset(self):
        return Question.objects.all().order_by("question")


@method_decorator(
    staff_member_required(login_url="/login"),
    name="dispatch",
)
class QcommentListView(generic.ListView, LoginRequiredMixin):

    model = Qcomment
    template_name = "qna/admin-qcomment.html"
    context_object_name = "comments"

    def get_queryset(self):
        return Qcomment.objects.all().order_by("question")


@method_decorator(
    staff_member_required(login_url="/login"),
    name="dispatch",
)
class AcommentListView(generic.ListView, LoginRequiredMixin):

    model = Acomment
    template_name = "qna/admin-Acomment.html"
    context_object_name = "comments"

    def get_queryset(self):
        return Acomment.objects.all().order_by("question")


@login_required
@csrf_exempt
def deleteqcomment(request):
    if request.method == "POST":
        id = request.POST.get("qcommentid", "")
        qcomment = Qcomment.objects.get(pk=id)
        questionscategories = qcomment.question.category.all()
        user = request.user
        if qcomment.user == user or getHasRole(user, questionscategories):
            qcomment.delete()
            data = {"deleted": True}
            return JsonResponse(data)
        else:
            data = {"error": "You can't perform this action"}
            return JsonResponse(data)

    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def deleteacomment(request):
    if request.method == "POST":
        id = request.POST.get("acommentid", "")
        acomment = Acomment.objects.get(pk=id)
        questionscategories = acomment.answer.question.category.all()
        user = request.user
        if acomment.user == user or getHasRole(user, questionscategories):
            acomment.delete()
            data = {"deleted": True}
            return JsonResponse(data)
        else:
            data = {"error": "You can't perform this action"}
            return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def categorymanager(request):
    if request.method == "POST":
        categoryslug = request.POST.get("categoryslug")
        user = request.user
        if request.user.is_authenticated:
            category = Category.objects.filter(slug=categoryslug).first()
            ucategory = userscategories(request.user)
            if category in ucategory:
                user.profile.category.remove(category)
                data = {"deleted": True}
                return JsonResponse(data)
            else:
                user.profile.category.add(category)
                data = {"added": True}
                return JsonResponse(data)
    else:
        return redirect("qna-home")


@login_required
@csrf_exempt
def rolemanager(request):
    if request.method == "POST":
        categoryslug = request.POST.get("categoryslug")
        user = request.user
        if request.user.is_authenticated:
            category = Category.objects.filter(slug=categoryslug).first()
            urole = request.user.profile.role.all()
            if category.role in urole:
                data = {"added": True}
                return JsonResponse(data)
            else:
                hasSuffecientCoins = False
                isOldEnough = False
                catuserquestion = user.userWhoAskQuestion.filter(
                    category=category,
                )
                usersCoins = 0
                for question in catuserquestion:
                    usersCoins += question.vote
                if usersCoins > 7000:
                    hasSuffecientCoins = True

                if timezone.now() - timedelta(days=30) > user.date_joined:
                    isOldEnough = True

                if hasSuffecientCoins and isOldEnough:
                    user.profile.role.add(category.role)
                    data = {"added": True}
                    return JsonResponse(data)
                else:
                    data = {"insufficient": "Can't get right now"}
                    return JsonResponse(data)
    else:
        return redirect("qna-home")


def response_404_error_handler(request, exception=None):
    return render(request, "qna/page404.html", status=404)


def response_500_error_handler(request, exception=None):
    return render(request, "qna/page500.html", status=404)


def response_404_error_handler(request, exception=None):  # noqa
    return render(request, "qna/page404.html", status=404)


def response_403_error_handler(request, exception=None):
    return render(request, "qna/page404.html", status=403)


def response_400_error_handler(request, exception=None):
    return render(request, "qna/page404.html", status=400)


def csrf_failure(request, reason=""):
    return render(request, "qna/page404.html", status=403)
