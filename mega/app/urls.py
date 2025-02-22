from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, FavoriteBookViewSet, GenreViewSet, LoginView, RegisterView, LoginPageView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'favorites', FavoriteBookViewSet, basename='favorite')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/register/', RegisterView.as_view(), name='register'),
    path('v1/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/api-auth/', include('rest_framework.urls')),
]
