from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name="Текст",
    )
    # pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        null=True,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Введите текст комментария",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации комментария",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации ",
    )

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user.username} / {self.author.username}"
