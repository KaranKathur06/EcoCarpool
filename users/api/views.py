from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from ..models import CustomUser
from .serializers import UserSerializer
from django.db import models

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role', None)
        search = self.request.query_params.get('search', None)
        
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        return queryset.order_by('-registration_date')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.save()
        return Response({'status': 'user verified'})
    
    @action(detail=True, methods=['post'])
    def resend_verification(self, request, pk=None):
        user = self.get_object()
        # Add email verification logic here
        return Response({'status': 'verification email sent'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        drivers = CustomUser.objects.filter(role='driver').count()
        passengers = CustomUser.objects.filter(role='passenger').count()
        verified_users = CustomUser.objects.filter(is_verified=True).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'drivers': drivers,
            'passengers': passengers,
            'verified_users': verified_users
        })