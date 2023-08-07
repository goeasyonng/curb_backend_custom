from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Comment, Recomment
from . import serializers


class CommentDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        responses={
            204: openapi.Response(
                description="Successful Response",
            ),
            403: "Permission Denied",
        },
    )
    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.user != request.user:
            if not request.user.is_coach:
                if not request.user.is_staff:
                    raise PermissionDenied
        comment.delete()
        return Response(status=204)


class TopLikeView(APIView):
    @swagger_auto_schema(
        operation_summary="베스트 댓글 api",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=serializers.CommentSerializer(),
            )
        },
    )
    def get(self, request):
        feed = (
            Comment.objects.annotate(like_count=Count("commentlike"))
            .order_by("-like_count")
            .first()
        )
        serializer = serializers.CommentSerializer(feed, many=True)
        return Response(serializer.data)


class Recomments(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # @swagger_auto_schema(
    #     operation_summary="대댓글 조회",
    #     responses={
    #         200: openapi.Response(
    #             description="Successful Response",
    #             schema=serializers.RecommentSerializer(),
    #         )
    #     },
    # )
    # def get(self, request, comment_pk, recomment_pk):
    #     recomment = get_object_or_404(
    #         Recomment, comment__pk=comment_pk, pk=recomment_pk
    #     )
    #     serializer = serializers.RecommentSerializer(recomment)
    #     return Response(serializer.data)

    # @swagger_auto_schema(
    #     operation_summary="대댓글 삭제",
    #     responses={
    #         200: openapi.Response(
    #             description="Successful Response",
    #             schema=serializers.RecommentSerializer(),
    #         )
    #     },
    # )
    # def delete(self, request, comment_pk, recomment_pk):
    #     recomment = get_object_or_404(
    #         Recomment, comment__pk=comment_pk, pk=recomment_pk
    #     )
    #     if recomment.user == request.user:
    #         recomment.delete()
    #         return Response(status=204)
    #     else:
    #         raise PermissionDenied


class DeleteRecomment(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="대댓글 삭제",
        responses={
            204: openapi.Response(
                description="Successful Response",
            ),
            403: "Permission Denied",
        },
    )
    def delete(self, request, recomment_pk):
        recomment = get_object_or_404(Recomment, pk=recomment_pk)
        if recomment.user != request.user:
            if not request.user.is_coach:
                if not request.user.is_staff:
                    raise PermissionDenied
        recomment.delete()
        return Response(status=204)
