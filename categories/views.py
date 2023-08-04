from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework.permissions import IsAuthenticated
from .models import Category
from . import serializers
from django.shortcuts import get_object_or_404
from groups.models import Group
from django.core.cache import cache


class GroupCategories(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="그룹 카테고리 조회",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=serializers.CategorySerializer(),
            )
        },
    )
    def get(self, request, group_pk):
        # import time
        # start = time.time()
        category = cache.get(f"category_of_{group_pk}")
        if category:
            # end = time.time()
            # print("Cached Time")
            # print(end - start)
            return Response(category)
        category = Category.objects.filter(group__pk=group_pk).order_by("created_at")
        serializer = serializers.CategorySerializer(
            category,
            many=True,
        )
        cache.set(f"category_of_{group_pk}", serializer.data)

        # end = time.time()
        # print("Not cached Time")
        # print(end - start)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="그룹 카테고리 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명"),
            },
        ),
        responses={
            200: openapi.Response(description="OK"),
            400: openapi.Response(description="Invalid request data"),
            401: openapi.Response(description="The user is not authenticated"),
        },
    )
    def post(self, request, group_pk):
        serializer = serializers.CategorySerializer(data=request.data)
        if not request.user.is_coach:
            if not request.user.is_staff:
                raise PermissionDenied
        if serializer.is_valid():
            category = serializer.save(group=group_pk)
            serializer = serializers.CategorySerializer(category)
            cache.delete(f"category_of_{group_pk}")
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class GroupCategoryDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="그룹 카테고리 디테일 조회",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=serializers.CategorySerializer(),
            )
        },
    )
    def get(self, request, pk, group_pk):
        category = get_object_or_404(Category, pk=pk, group__pk=group_pk)
        serializer = serializers.CategorySerializer(category)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="그룹 카테고리 수정",
        request_body=serializers.CategorySerializer(),
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=serializers.CategorySerializer(),
            ),
            400: "Bad Request",
        },
    )
    def put(self, request, group_pk, pk):
        group = get_object_or_404(Group, pk=group_pk)
        category = get_object_or_404(Category, pk=pk, group=group)
        serializer = serializers.CategorySerializer(
            category,
            data=request.data,
            partial=True,
        )
        if request.user.group != group:
            if not request.user.is_staff:
                raise PermissionDenied

        if request.user.is_coach == False:
            if not request.user.is_staff:
                raise PermissionDenied

        if serializer.is_valid():
            category = serializer.save(group=group_pk)
            serializer = serializers.CategorySerializer(category)
            cache.delete(f"category_of_{group_pk}")
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="그룹 카테고리 삭제",
        responses={
            204: openapi.Response(
                description="Successful response",
            )
        },
    )
    def delete(self, request, group_pk, pk):
        if not request.user.is_staff:
            if request.user.group.pk != group_pk:
                raise PermissionDenied
        if not request.user.is_coach:
            if not request.user.is_staff:
                raise PermissionDenied

        category = get_object_or_404(Category, pk=pk, group__pk=group_pk)
        if category.name == "전체글" or category.name == "인기글":
            raise ParseError("Can't delete this category")
        category.delete()
        cache.delete(f"category_of_{group_pk}")
        return Response({"result": "delete success"}, status=204)
