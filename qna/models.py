from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext as _


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)
    category = models.ManyToManyField("Category", blank=True)
    role = models.ManyToManyField("Role", blank=True, related_name="usersrole")

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def display_category(self):
        return ", ".join(category.category for category in self.category.all()[:3])

    def display_user(self):
        return self.user.username

    def __str__(self):
        return self.user.username


class Category(models.Model):

    category = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        ordering = ["category"]

    def __str__(self):
        return self.category


class Role(models.Model):

    role = models.CharField(max_length=120)
    category = models.OneToOneField("Category", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return self.role

    def get_absolute_url(self):
        return reverse("Role_detail", kwargs={"pk": self.pk})


class Question(models.Model):

    STATUS_CHOICES = (
        ("a", "Available"),
        ("f", "Flag"),
        ("o", "Onhold"),
        ("c", "Closed"),
    )

    question = models.CharField(max_length=1000, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default="2",
        related_name="userWhoAskQuestion",
    )
    category = models.ManyToManyField(
        "Category",
        related_name="categoryOfQuestion",
        blank=True,
    )
    vote = models.IntegerField(default=0)
    edit_user = models.ManyToManyField(
        User,
        related_name="userWhoEditQuestion",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="a")

    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.question)
        super(Question, self).save(*args, **kwargs)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse("question", kwargs={"pk": self.pk})

    def display_category(self):
        return ", ".join(category.category for category in self.category.all()[:3])

    def display_edituser(self):
        return ", ".join(edit_user.username for edit_user in self.edit_user.all()[:3])

    display_edituser.short_description = "Edit user"


class Answer(models.Model):

    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    answer = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default="2",
        related_name="userWhoAnswerQuestion",
    )
    vote = models.IntegerField(default=0)
    edit_user = models.ManyToManyField(
        User,
        related_name="userWhoEditAnswer",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        ordering = ["question", "-vote"]

    def __str__(self):
        return self.answer

    def display_edituser(self):
        return ", ".join(edit_user.username for edit_user in self.edit_user.all()[:3])


class QuestionStatusHistory(models.Model):

    question = models.OneToOneField("Question", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default="2",
        related_name="userWhoChangeQuestionStatus",
    )
    reason = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("QuestionStatusHistory")
        verbose_name_plural = _("QuestionStatusHistorys")

    def __str__(self):
        return str(self.question.id) + self.question.status

    def display_status(self):
        return self.question.status


class Qcomment(models.Model):

    qcomment = models.CharField(max_length=600)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default="2",
        related_name="userWhoCommentOnQuestion",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Qcomment")
        verbose_name_plural = _("Qcomments")
        ordering = ["created_at"]

    def __str__(self):
        return self.qcomment


class Acomment(models.Model):

    acomment = models.CharField(max_length=600)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default="2",
        related_name="userWhoCommentonAnswer",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Acomment")
        verbose_name_plural = _("Acomments")

    def __str__(self):
        return self.acomment

    def display_answer_id(self):
        return self.answer.id


class Feedback(models.Model):

    feedback = models.CharField(max_length=1000)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")

    def __str__(self):
        return self.feedback
