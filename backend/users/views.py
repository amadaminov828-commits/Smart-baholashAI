from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer, UserManagementSerializer, CompanySerializer
from .models import User, Company
from vehicles.models import VehicleValuation
from real_estate.models import RealEstateValuation
from rest_framework.views import APIView

class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class UserManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserManagementSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            # Super Admin sees everyone
            return User.objects.all()
        elif user.role == 'admin':
            # Assistant Admin sees only users they created OR their own profile
            from django.db.models import Q
            return User.objects.filter(Q(created_by=user) | Q(id=user.id))
        # Regular users only see themselves
        return User.objects.filter(id=user.id)

    def perform_create(self, serializer):
        # Ensure only admins can create users
        if self.request.user.role not in ['super_admin', 'admin']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Faqat adminlar foydalanuvchi yaratishi mumkin")
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Security check for deletion
        instance = self.get_object()
        if request.user.role == 'admin' and instance.role in ['super_admin', 'admin']:
            return Response({"error": "Yordamchi admin boshqa adminlarni o'chira olmaydi"}, status=status.HTTP_403_FOR_DIRECTORY)
        return super().destroy(request, *args, **kwargs)


class AdminStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['super_admin', 'admin']:
            return Response({"error": "Ruxsat berilmagan"}, status=403)
        
        user = request.user
        if user.role == 'super_admin':
            total_users = User.objects.count()
            v_qs = VehicleValuation.objects.all()
            re_qs = RealEstateValuation.objects.all()
        else:
            # Assistant Admin only sees their own ecosystem
            total_users = User.objects.filter(created_by=user).count()
            v_qs = VehicleValuation.objects.filter(user__created_by=user)
            re_qs = RealEstateValuation.objects.filter(user__created_by=user)
            
        vehicle_reports = v_qs.count()
        real_estate_reports = re_qs.count()
        
        # Count paid/approved valuations
        vehicle_paid = v_qs.filter(status='approved').count()
        real_estate_paid = re_qs.filter(status='approved').count()
        
        return Response({
            'total_users': total_users,
            'total_reports': vehicle_reports + real_estate_reports,
            'total_payments': vehicle_paid + real_estate_paid,
            'vehicle_stats': {
                'total': vehicle_reports,
                'paid': vehicle_paid
            },
            'real_estate_stats': {
                'total': real_estate_reports,
                'paid': real_estate_paid
            }
        })


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Company.objects.filter(id=user.company.id)
        return Company.objects.none()

    def perform_create(self, serializer):
        company = serializer.save()
        self.request.user.company = company
        self.request.user.save()

