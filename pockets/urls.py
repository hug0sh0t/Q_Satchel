from django.urls import path


from pockets.views import (
    pocket_delete_view,
    pocket_detail_view,
    api_pocket_list_view,
    pocket_create_view,
    full_pocket_delete_view,
 
)
# has api/pockets before each endpoint
urlpatterns = [
    path('full/delete', full_pocket_delete_view, name="full pocket del"),
    path('<int:pocket_id>/delete', pocket_delete_view),
    path('<int:pocket_id>', pocket_detail_view),
    path('pocketcreate', pocket_create_view),
    path('', api_pocket_list_view),   


]

