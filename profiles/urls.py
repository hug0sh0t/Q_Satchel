from django.urls import path
from .views import (
    profile_detail_view,
    analyze_view,
    allocation_view,  
    profile_update_view, 
    profile_detail_api_view,
    updateTheme,
    profile_followers_view,
    profile_following_view,
    connection_ToggleEP,
    # unfollow_ToggleEP
    
)

urlpatterns = [
    path('api/', profile_detail_api_view, name="papi"),
    path('<str:username>/', profile_detail_view),
    path('analyze/charts', analyze_view),
    path('analyze/charts/allocation', allocation_view),

    path('<str:username>/followers/', profile_followers_view),
    path('<str:username>/following/', profile_following_view),
    
    # For the Follow/Unfollow System follows the follwoing , 
    # the the subject being Follow/Unfollowed comes before the member (actor) performing the action
    # in this case, request.user is often the actor
    path('<str:subject>/follow_activation/<str:actor>/', connection_ToggleEP),
    # path('<str:username>/unfollow_activation/<str:username>/', unfollow_ToggleEP),


    path('update_theme', updateTheme, name='papi_update_theme'),
    path('<str:username>/follow_toggle_activation', updateTheme, name='follow_toggle_url'),
    
    path('edit', profile_update_view),
]