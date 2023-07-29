from rest_framework.test import APITestCase
from .models import Feed
from groups.models import Group
from users.models import User
from categories.models import Category
from comments.models import Comment, Recomment


# 게시글 조회 테스트
class FeedGet(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(is_coach=True, group=self.group)
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
        )

    def test_get_all_feed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "status isn't 200")
        self.assertEqual(len(response.data), 4)


# 게시글 생성 테스트
class FeedPost(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(is_coach=True, group=self.group)
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
        )

    # 유효한 데이터로 POST 요청 보내기
    def test_feed_post_with_valid_data(self):
        data = {"title": "first feed", "category": 1}
        self.client.force_login(self.user)
        response = self.client.post(self.URL, data, format="json")
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    # 유효하지 않은 데이터로 POST 요청 보내기
    def test_category_post_with_invalid_data(self):
        data = {"title": "first feed"}
        self.client.force_login(self.user)
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)

    # 권한이 없는 사용자로 POST 요청 보내기
    def test_category_post_without_permission(self):
        self.client.login(username="testuser", password="testpass")
        data = {"title": "first feed", "category": 1}
        # self.client.force_login(self.user)
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 403)


# 게시글 디테일 조회 테스트
class FeedDetailGet(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(is_coach=True, group=self.group)
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
            group=self.group,
        )

    def test_get_feed(self):
        self.client.force_login(self.user)
        response = self.client.get(f"{self.URL}{self.feed.pk}/")
        self.assertEqual(response.status_code, 200, "status isn't 200")
        self.assertEqual(len(response.data), 14)


# 게시글 디테일 수정 테스트
class FeedDetailPut(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(
            name="OtherUser",
            is_coach=True,
            group=self.group,
            email="user@example.com",
        )
        self.other_user = User.objects.create(
            username="Test User",
            is_coach=True,
            group=self.group,
            email="test@example.com",
        )
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
        )

    # 존재하지 않는 url 접근
    def test_view_feed_detail_not_found_url(self):
        self.client.force_login(self.user)
        response = self.client.get(f"{self.URL}/10", format="json")
        self.assertEqual(response.status_code, 404, "존재하지 않는 url")
        self.client.logout()

    # 비 로그인 유저가 수정
    def test_edit_feed_detail_non_login_user(self):
        response = self.client.put(
            f"{self.URL}{self.feed.pk}/", data={"title": "feed get test"}, format="json"
        )
        self.assertEqual(response.status_code, 403, "비 로그인 수정")

    # 생성한 유저가 아닌 유저가 수정
    def test_edit_feed_detail_not_create_user(self):
        self.client.force_login(self.other_user)
        response = self.client.put(
            f"{self.URL}{self.feed.pk}/", data={"title": "feed get test"}, format="json"
        )
        self.assertEqual(response.status_code, 403, "로그인 (업로드 유저가 아닌 유저) 후 수정")
        self.client.logout()

    # 생성한 유저가 수정
    def test_edit_feed_detail_create_user(self):
        self.client.force_login(self.user)
        response = self.client.put(
            f"{self.URL}{self.feed.pk}/", data={"title": "feed get test"}, format="json"
        )
        self.assertEqual(response.status_code, 200, "로그인 (업로드 유저가) 후 수정")
        self.client.logout()

    # 수정 확인
    def test_edit_feed_detail_create_user_change_value(self):
        self.client.force_login(self.user)
        response = self.client.put(
            f"{self.URL}{self.feed.pk}/", data={"title": "feed get test"}, format="json"
        )
        self.assertEqual(
            Feed.objects.get(pk=self.feed.pk).title,
            "feed get test",
            "수정 여부 확인",
        )
        self.client.logout()


# 게시글 디테일 삭제 테스트
class FeedDetailDelete(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(
            name="OtherUser",
            is_coach=True,
            group=self.group,
            email="user@example.com",
        )
        self.other_user = User.objects.create(
            username="Test User",
            is_coach=True,
            group=self.group,
            email="test@example.com",
        )
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
        )

    # def test_feed_delete(self):
    #     self.client.force_login(self.user)
    #     response = self.client.delete(f"{self.URL}{self.feed.pk}")
    #     self.assertEqual(response.status_code, 200, "status isn't 200")


# 댓글 조회 테스트
class CommentGet(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(
            is_coach=True,
            is_staff=True,
            group=self.group,
        )
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
            group=self.group,
        )
        self.comment = Comment.objects.create(
            feed=self.feed,
            user=self.user,
        )
        self.recomment = Recomment.objects.create(
            user=self.user,
            comment=self.comment,
        )

    def test_get_all_comments(self):
        self.client.force_login(self.user)
        response = self.client.get(f"{self.URL}{self.feed.pk}/comment/")
        self.assertEqual(response.status_code, 200)


# 댓글 생성 테스트
class CommentPost(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(
            is_coach=True,
            is_staff=True,
            group=self.group,
        )
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
            group=self.group,
        )
        self.comment = Comment.objects.create(
            feed=self.feed,
            user=self.user,
        )

    # 유효한 데이터로 POST 요청 보내기
    def test_feed_post_with_valid_data(self):
        self.client.force_login(self.user)
        data = {"description": "test comment"}
        response = self.client.post(
            f"{self.URL}{self.feed.pk}/comment/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)

    # 유효하지 않은 데이터로 POST 요청 보내기
    def test_feed_post_with_invalid_data(self):
        self.client.force_login(self.user)
        data = {"description": ""}
        response = self.client.post(
            f"{self.URL}{self.feed.pk}/comment/", data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    # 권한이 없는 사용자로 POST 요청 보내기
    def test_feed_post_without_permission(self):
        self.client.login(username="testuser", password="testpass")
        data = {"description": "test comment"}
        response = self.client.post(
            f"{self.URL}{self.feed.pk}/comment/", data, format="json"
        )
        self.assertEqual(response.status_code, 403)

    # 익명


# 대댓글 생성 테스트
class ReommentPost(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(
            is_coach=True,
            is_staff=True,
            group=self.group,
        )
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
            group=self.group,
        )
        self.comment = Comment.objects.create(
            feed=self.feed,
            user=self.user,
        )
        self.recomment = Recomment.objects.create(
            user=self.user,
            comment=self.comment,
        )

    # 유효한 데이터로 POST 요청 보내기
    def test_feed_post_with_valid_data(self):
        self.client.force_login(self.user)
        data = {"description": "test recomment"}
        response = self.client.post(
            f"{self.URL}{self.feed.pk}/comment/{self.comment.pk}/recomment/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    # 유효하지 않은 데이터로 POST 요청 보내기
    def test_feed_post_with_invalid_data(self):
        self.client.force_login(self.user)
        data = {"description": ""}
        response = self.client.post(
            f"{self.URL}{self.feed.pk}/comment/{self.comment.pk}/recomment/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    # 권한이 없는 사용자로 POST 요청 보내기
    def test_feed_post_without_permission(self):
        self.client.login(username="testuser", password="testpass")
        data = {"description": "test recomment"}
        response = self.client.post(
            f"{self.URL}{self.feed.pk}/comment/{self.comment.pk}/recomment/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 403)


# 게시글 검색
class GroupFeedSearch(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(
            is_coach=True,
            is_staff=True,
            group=self.group,
        )
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
            group=self.group,
        )

    def test_get_all_search(self):
        # print(111111111)
        self.client.force_login(self.user)
        response = self.client.get(f"{self.URL}group/search/?group_id={self.group.pk}")
        self.assertEqual(response.status_code, 200)


# 게시글 검색 결과
# class GroupCategoryFeedGet(APITestCase):
#     URL = "/api/v1/feeds/"
#     TITLE = "feed get test"

#     def setUp(self):
#         self.group = Group.objects.create(name="oz")
#         self.user = User.objects.create(is_coach=True, group=self.group)
#         self.category = Category.objects.create(group=self.group)
#         self.feed = Feed.objects.create(
#             user=self.user,
#             title=self.TITLE,
#             category=self.category,
#             # group=self.group,
#         )

#     def test_get_all_feed(self):
#         self.client.force_login(self.user)
#         response = self.client.get(
#             f"{self.URL}group/category/?group_id={self.group.pk}&keyword=test",
#         )
#         self.assertEqual(response.status_code, 200, "status isn't 200")
#         self.assertEqual(len(response.data), 4)


# 그룹 카테고리 게시글 조회
class GroupCategoryFeedGet(APITestCase):
    URL = "/api/v1/feeds/"
    TITLE = "feed get test"

    def setUp(self):
        self.group = Group.objects.create(name="oz")
        self.user = User.objects.create(is_coach=True, group=self.group)
        self.category = Category.objects.create(group=self.group)
        self.feed = Feed.objects.create(
            user=self.user,
            title=self.TITLE,
            category=self.category,
            # group=self.group,
        )

    def test_get_category_feed(self):
        self.client.force_login(self.user)
        response = self.client.get(
            f"{self.URL}group/category/?group_id={self.group.pk}&category_id={self.category.pk}",
        )
        self.assertEqual(response.status_code, 200, "status isn't 200")
        self.assertEqual(len(response.data), 4)
