from django.db import models
from common.models import CommonModel
from django.db.models import Count


class Feed(CommonModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    visited = models.PositiveIntegerField(
        editable=False,
        default=0,
    )

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def like_count(self):
        return self.feedlike.count()

    @property
    def comments_count(self):
        return self.comment.count()

    @property
    def highest_like_comments(self):
        return self.comment.annotate(like_count=Count("commentlike")).order_by(
            "-like_count"
        )[:1]

    @property
    def thumbnail(self):
        if self.images.exists():
            return self.images.all()[0].url
        else:
            return None
