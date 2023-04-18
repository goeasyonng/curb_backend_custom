from django.db import models
from common.models import CommonModel


class Feedlike(CommonModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )
    feed = models.ForeignKey(
        "feeds.Feed",
        on_delete=models.CASCADE,
        related_name="feedlike",
    )
    unique_together = ("user", "feed")


class                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   (CommonModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        "comments.Comment",
        on_delete=models.CASCADE,
        related_name="commentlike",
    )
    unique_together = ("user", "comment")
