from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.paginator import Paginator
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from .models import Feed
from . import serializers
from django.shortcuts import get_object_or_404
from groups.models import Group
from categories.models import Category
from medias.models import Image
from comments.serializers import CommentSerializer
from comments.serializers import RecommentSerializer
from comments.models import Comment
from django.db.models import F, Q
from rest_framework import permissions
from django.core.cache import cache


class IsCoachOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_coach or request.user.is_staff


user_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "pk": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="유저의 식별 pk값",
        ),
        "is_coach": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="코치 여부",
        ),
    },
)
feed_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="The ID of the feed",
        ),
        "user": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The username of the feed's owner",
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The name of the feed's owner"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The email address of the feed's owner",
                ),
                "avatar": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The URL of the feed owner's avatar image, if available",
                ),
                "is_coach": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether the feed's owner is a coach",
                ),
            },
            description="The user who created the feed",
        ),
        "group": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "pk": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="The ID of the group"
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The name of the group"
                ),
                "members_count": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The number of members in the group",
                ),
            },
            description="The group to which the feed belongs",
        ),
        "category": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="The ID of the category"
                ),
                # "group": openapi.Schema(
                #     type=openapi.TYPE_OBJECT,
                #     properties={
                #         "pk": openapi.Schema(
                #             type=openapi.TYPE_INTEGER, description="The ID of the group"
                #         ),
                #         "name": openapi.Schema(
                #             type=openapi.TYPE_STRING,
                #             description="The name of the group",
                #         ),
                #         "members_count": openapi.Schema(
                #             type=openapi.TYPE_INTEGER,
                #             description="The number of members in the group",
                #         ),
                #     },
                #     description="The group to which the category belongs",
                # ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The name of the category"
                ),
            },
            description="The category to which the feed belongs",
        ),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING, description="The description of the feed"
        ),
        "visited": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="The number of times the feed has been visited",
        ),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="The date and time at which the feed was created, in ISO 8601 format",
        ),
        "like_count": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="The number of likes the feed has received",
        ),
        "comments_count": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="The number of comments the feed has received",
        ),
        "highest_like_comments": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="The ID of the comment"
                    ),
                    "user": user_schema,
                    "description": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "created_at": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "commentlikeCount": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                    ),
                    "recomment": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "user": user_schema,
                            "created_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                            ),
                            "description": openapi.Schema(
                                type=openapi.TYPE_STRING,
                            ),
                        },
                    ),
                },
            ),
            description="The comments with the most likes",
        ),
        "is_like": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
        ),
        "thumnail": openapi.Schema(
            type=openapi.TYPE_STRING,
        ),
        "is_like": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
        ),
    },
)


class Feeds(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="피드 전체 조회",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="1 페이지당 24개의 데이터 (default = 1) \n - total_pages : 총 페이지수 \n - now_page : 현재 페이지 \n - count : 총 개수 \n - results : 순서",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_pages": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="The total number of pages",
                        ),
                        "now_page": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="The current page number",
                        ),
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="The total number of objects",
                        ),
                        "results": feed_schema,
                    },
                ),
            )
        },
    )
    def get(self, request):
        feed = (
            Feed.objects.select_related("user", "group")
            .prefetch_related("images", "comment", "feedlike")
            .all()
            .order_by("-created_at")
        )

        # 최신순
        # pagenations
        current_page = request.GET.get("page", 1)
        items_per_page = 24
        paginator = Paginator(feed, items_per_page)
        try:
            page = paginator.page(current_page)
        except:
            page = paginator.page(paginator.num_pages)

        if int(current_page) > int(paginator.num_pages):
            raise ParseError("that page is out of range")

        serializer = serializers.FeedSerializer(
            page,
            many=True,
            context={"request": request},
        )

        data = {
            "total_pages": paginator.num_pages,
            "now_page": page.number,
            "count": paginator.count,
            "results": serializer.data,
        }
        return Response(data)

    @swagger_auto_schema(
        operation_summary="피드 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "category"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="타이틀"),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="내용"
                ),
                "category": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="카테고리 pk"
                ),
                "image": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="이미지 url, image:null -> 이미지 삭제",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="OK", schema=serializers.FeedDetailSerializer
            ),
            400: openapi.Response(description="잘못된 형식의 데이터"),
            401: openapi.Response(description="비 로그인"),
            404: openapi.Response(description="카테고리 pk가 없거나 유효하지 않은 값"),
        },
    )
    def post(self, request):
        serializer = serializers.FeedDetailSerializer(data=request.data)
        if serializer.is_valid():
            category = get_object_or_404(
                Category, group=request.user.group, pk=request.data.get("category")
            )
            feed = serializer.save(
                user=request.user,
                group=request.user.group,
                category=category,
                image=request.data.get("image"),
            )
            serializer = serializers.FeedDetailSerializer()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class FeedDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="피드 조회",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=serializers.FeedDetailSerializer(),
            ),
            403: "요청한 피드가 속한 그룹과 유저의 그룹이 다를 경우",
        },
    )
    def get(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)

        if feed.group != request.user.group:
            if not request.user.is_staff:
                raise PermissionDenied

        Feed.objects.filter(pk=pk).update(visited=F("visited") + 1)

        serializer = serializers.FeedDetailSerializer(
            feed, context={"request": request}
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="피드 수정",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="타이틀"),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="내용"
                ),
                "category": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="카테고리 pk"
                ),
                "image": openapi.Schema(
                    type=openapi.TYPE_STRING, description="이미지 url, 삭제하려면 Image:null"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=serializers.FeedDetailSerializer(),
            ),
            400: "Bad Request",
            403: "PermissionDenied",
            404: "Not Found",
        },
    )
    def put(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        if feed.user != request.user:
            raise PermissionDenied
        serializer = serializers.FeedDetailSerializer(
            feed,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            try:
                feed = serializer.save(
                    image=request.data["image"], category=request.data.get("category")
                )
            except KeyError:
                feed = serializer.save(category=request.data.get("category"))
            serializer = serializers.FeedDetailSerializer(feed)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="피드 삭제",
        responses={
            204: openapi.Response(description="Successful response"),
            403: "PermissionDenied",
        },
    )
    def delete(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        if feed.user != request.user:
            raise PermissionDenied
        feed.delete()
        return Response(status=204)


class GroupFeedCategory(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="그룹 피드 카테고리별 조회",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="1 페이지당 24개의 데이터 \n - num_pages : 총 페이지수 \n - current_page : 현재 페이지 \n - count : 총 개수 \n - results : 순서",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "group_id",
                openapi.IN_QUERY,
                description="그룹의 pk 값",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "category_id",
                openapi.IN_QUERY,
                description="해당 그룹 내 카테고리의 pk 값",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_pages": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="전체 페이지",
                        ),
                        "now_page": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="현재 페이지",
                        ),
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="피드의 갯수",
                        ),
                        "results": feed_schema,
                    },
                ),
            ),
            400: "범위를 벗어난 페이지 요청",
            403: "유저가 속한 그룹이 아닌 데이터를 요청",
            404: "그룹과 카테고리의 pk가 유효하지 않거나, 카테고리의 그룹과 요청한 그룹이 다를 때",
        },
    )
    def get(self, request):
        group_pk = request.GET.get("group_id")
        category_pk = request.GET.get("category_id")
        # group = get_object_or_404(Group, pk=group_pk)
        if not request.user.is_staff:
            if str(request.user.group.pk) != group_pk:
                raise PermissionDenied
        category = get_object_or_404(Category, pk=category_pk)
        if category.name == "전체글":
            feed = (
                Feed.objects.select_related("user", "group")
                .prefetch_related("images", "comment", "feedlike")
                .filter(group__pk=group_pk)
                .order_by("-created_at")
            )
        elif category.name == "인기글":
            feed = (
                Feed.objects.select_related("user", "group")
                .prefetch_related("images", "comment", "feedlike")
                .filter(group__pk=group_pk)
                .annotate(count_like=Count("feedlike"))
                .order_by("-count_like")
            )
        else:
            feed = (
                Feed.objects.select_related("user", "group")
                .prefetch_related("images", "comment", "feedlike")
                .filter(
                    group__pk=group_pk,
                    category=category,
                )
                .order_by("-created_at")
            )
        items_per_page = 12
        current_page = request.GET.get("page", 1)
        paginator = Paginator(feed, items_per_page)
        try:
            page = paginator.page(current_page)
        except:
            page = paginator.page(paginator.num_pages)

        if int(current_page) > int(paginator.num_pages):
            raise ParseError("that page is out of range")

        serializer = serializers.FeedSerializer(
            page,
            many=True,
            context={"request": request},
        )
        data = {
            "total_pages": paginator.num_pages,
            "now_page": page.number,
            "count": paginator.count,
            "results": serializer.data,
        }
        return Response(data)


class TopLikeView(APIView):
    @swagger_auto_schema(
        operation_summary="커뮤니티 피드 전체 조회(좋아요순)",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="1 페이지당 24개의 데이터 \n - num_pages : 총 페이지수 \n - current_page : 현재 페이지 \n - count : 총 개수 \n - results : 순서",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_pages": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="전체 페이지",
                        ),
                        "now_page": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="현재 페이지",
                        ),
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="피드의 갯수",
                        ),
                        "results": feed_schema,
                    },
                ),
            ),
        },
    )
    def get(self, request):
        feed = (
            Feed.objects.annotate(like_count=Count("feedlike"))
            .order_by("-like_count")
            .order_by(-"created_at")
        )
        items_per_page = 24
        current_page = request.GET.get("page", 1)
        paginator = Paginator(feed, items_per_page)
        try:
            page = paginator.page(current_page)
        except:
            page = paginator.page(paginator.num_pages)

        if int(current_page) > int(paginator.num_pages):
            raise ParseError("that page is out of range")

        serializer = serializers.FeedSerializer(
            page,
            many=True,
            context={"request": request},
        )
        data = {
            "total_pages": paginator.num_pages,
            "now_page": page.number,
            "count": paginator.count,
            "results": serializer.data,
        }
        return Response(data)


class FeedComment(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="피드 댓글 조회",
        operation_description="feed 의 id 입력",
        responses={
            201: openapi.Response(
                description="Successful Response",
                schema=CommentSerializer(many=True),
            ),
            403: "그룹이 다른 유저가 요청, 비로그인 유저",
            404: "존재하지 않는 feed pk",
        },
    )
    def get(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        if feed.group != request.user.group:
            if not request.user.is_staff:
                raise PermissionDenied
        comments = feed.comment.select_related("user").prefetch_related(
            "recomment", "commentlike"
        )
        serializer = CommentSerializer(
            comments,
            many=True,
            context={"request": request},
        )
        anonymous_numbers = {}
        for comment in serializer.data:
            if comment.get("feed_writer"):
                comment["anonymous_number"] = "익명(작성자)"
            else:
                user_pk = comment["user"]["pk"]
                if user_pk not in anonymous_numbers:
                    anonymous_numbers[user_pk] = len(anonymous_numbers) + 1
                comment["anonymous_number"] = f"익명{anonymous_numbers[user_pk]}"

            for recomment in comment.get("recomment", []):
                if recomment.get("feed_writer"):
                    recomment["anonymous_number"] = "익명(작성자)"

                else:
                    user_pk = recomment["user"]["pk"]
                    if user_pk not in anonymous_numbers:
                        anonymous_numbers[user_pk] = len(anonymous_numbers) + 1
                    recomment["anonymous_number"] = f"익명{anonymous_numbers[user_pk]}"

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="피드 댓글 등록",
        operation_description="feed 의 id 입력",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["description"],
            properties={
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="댓글 내용"
                )
            },
        ),
        responses={
            201: openapi.Response(
                description="Successful Response", schema=CommentSerializer
            ),
            400: "Description 형식 오류",
            403: "그룹이 다른 유저가 요청, 비로그인 유저",
            404: "존재하지 않는 feed pk",
        },
    )
    def post(self, request, pk):
        feed = get_object_or_404(Feed, pk=pk)
        if feed.group != request.user.group:
            raise PermissionDenied
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(feed=feed, user=request.user)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class FeedRecomment(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="피드 대댓글 등록",
        operation_description="feed 의 id와 comment id 입력",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["description"],
            properties={
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="댓글 내용"
                )
            },
        ),
        responses={
            201: openapi.Response(
                description="Successful Response", schema=CommentSerializer
            ),
            400: "Description 형식 오류",
            403: "그룹이 다른 유저가 요청, 비로그인 유저",
            404: "feed의 id 나 comment 의 id 가 유효하지않을때",
        },
    )
    def post(self, request, pk, comment_pk):
        feed = get_object_or_404(Feed, pk=pk)
        if feed.group != request.user.group:
            raise PermissionDenied
        comment = get_object_or_404(Comment, pk=comment_pk)
        if comment.feed != feed:
            raise PermissionDenied
        serializer = RecommentSerializer(data=request.data)
        if serializer.is_valid():
            recomment = serializer.save(
                user=request.user,
                comment=comment,
            )
            serializer = RecommentSerializer(
                recomment,
                context={"request": request},
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class GroupFeedSearch(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="그룹 피드 연관 검색어 5개",
        manual_parameters=[
            openapi.Parameter(
                "group_id",
                openapi.IN_QUERY,
                description="그룹의 pk 값",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "keyword",
                openapi.IN_QUERY,
                description="검색하는 키워드",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="성공",
                examples={
                    "application/json": {
                        "result": [
                            {"pk": 1, "title": "Feed 1 title"},
                            {"pk": 2, "title": "Feed 2 title"},
                            {"pk": 3, "title": "Feed 3 title"},
                            {"pk": 4, "title": "Feed 4 title"},
                            {"pk": 5, "title": "Feed 5 title"},
                        ]
                    }
                },
            ),
            403: "유저가 속한 그룹이 아닌 데이터를 요청",
        },
    )
    def get(self, request):
        group_id = request.GET.get("group_id")
        keyword = request.GET.get("keyword")
        if keyword:
            feeds = Feed.objects.order_by("-created_at").filter(
                group__pk=group_id, title__icontains=keyword
            )[:5]
            data = {"result": [{"id": feed.pk, "title": feed.title} for feed in feeds]}
            return Response(data)
        else:
            return Response(status=200)


class GroupFeedSearchResult(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="그룹 피드 검색 결과",
        manual_parameters=[
            openapi.Parameter(
                "group_id",
                openapi.IN_QUERY,
                description="그룹의 pk 값",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "keyword",
                openapi.IN_QUERY,
                description="검색하는 키워드",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="페이지 수",
                default=1,
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="성공",
                examples={
                    "application/json": {
                        "result": [
                            [1, "Feed 1 title"],
                            [2, "Feed 2 title"],
                            [3, "Feed 3 title"],
                            [4, "Feed 4 title"],
                            [5, "Feed 5 title"],
                        ]
                    }
                },
            ),
            403: "유저가 속한 그룹이 아닌 데이터를 요청",
        },
    )
    def get(self, request):
        group_id = request.GET.get("group_id")
        keyword = request.GET.get("keyword")
        if keyword:
            feed = (
                Feed.objects.filter(group__pk=group_id)
                .filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
                .order_by("-created_at")
            )
            items_per_page = 12
            current_page = request.GET.get("page", 1)
            paginator = Paginator(feed, items_per_page)
            try:
                page = paginator.page(current_page)
            except:
                page = paginator.page(paginator.num_pages)

            if int(current_page) > int(paginator.num_pages):
                raise ParseError("that page is out of range")

            serializer = serializers.TinyFeedSerializer(
                page,
                many=True,
                context={"request": request},
            )
            data = {
                "total_pages": paginator.num_pages,
                "now_page": page.number,
                "count": paginator.count,
                "results": serializer.data,
            }
            return Response(data)
        else:
            return Response(status=200)
