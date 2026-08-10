from django.urls import path
from . import views

app_name = "wheels"

urlpatterns =[
    path("",views.home_page,name ="home"),
    path('car/<int:id>/',views.car_detail, name='car_detail'),

    path("profile/", views.profile_view, name="profile"),
    path("my-reviews/", views.my_reviews, name="my_reviews"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('car/<int:id>/review/',views.add_review,name='add_review'),
    path('profile/update/',views.update_profile,name='update_profile'),
    path('review/<int:id>/edit/',views.edit_review,name='edit_review'),
    path('review/<int:id>/delete/',views.delete_review,name='delete_review'),
    path('signup/',views.signup_view,name='signup'),

    path("manage-cars/",views.manage_cars,name="manage_cars"),
    path("car/add/",views.add_car,name="add_car"),
    path("car/<int:id>/edit/",views.edit_car,name="edit_car"),
    path("car/<int:id>/delete/",views.delete_car,name="delete_car"),

]
