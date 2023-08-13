from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Group
from . import serializers
from django.shortcuts import get_object_or_404
from django.core.cache import cache


class Groups(APIView):
    @swagger_auto_schema(
        operation_summary="그룹 전체 조회",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=serializers.GroupSerializer(),
            )
        },
    )
    def get(self, request):
        group = cache.get("group")
        if group:
            return Response(group)
        group = Group.objects.all()
        serializer = serializers.GroupSerializer(group, many=True)
        cache.set("group", serializer.data)
        return Response(serializer.data)


class GroupDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            raise NotFound

    @swagger_auto_schema(
        operation_summary="그룹 조회",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=serializers.GroupSerializer(),
            )
        },
    )
    def get(self, request, pk):
        group = cache.get(f"group:{pk}")
        if group:
            return Response(group)
        group = self.get_object(pk)
        serializer = serializers.GroupDetailSerializer(group)
        cache.set(f"group:{pk}", serializer.data)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="그룹 이름 수정",
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=serializers.GroupSerializer(),
            ),
            400: "Bad Request",
            404: "Not Found Group",
        },
        request_body=serializers.GroupSerializer(),
    )
    def put(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        if not request.user.group == group:
            if not request.user.is_coach:
                if not request.user.is_staff:
                    raise PermissionDenied
        serializer = serializers.GroupDetailSerializer(
            group,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            group = serializer.save()
            cache.delete("group")
            cache.delete(f"group:{pk}")
            return Response(serializers.GroupDetailSerializer(group).data)
        else:
            return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="그룹 삭제",
        responses={
            204: openapi.Response(
                description="Successful delete",
            ),
            403: "Bad Request",
            403: "Not Found Group",
        },
        request_body=serializers.GroupSerializer(),
    )
    def delete(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        if not request.user.is_coach:
            if request.user.group != group:
                if not request.user.is_staff:
                    raise PermissionDenied
        group.delete()
        cache.delete(f"group:{pk}")
        cache.delete("group")
        return Response("Successful delete", status=204)
