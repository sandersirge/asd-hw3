from django.urls import path

from . import views

app_name = "rides"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<int:ride_id>/", views.ride_detail, name="ride_detail"),
    path("<int:ride_id>/accept/", views.accept_ride, name="accept"),
    path("<int:ride_id>/start/", views.start_ride, name="start"),
    path("<int:ride_id>/complete/", views.complete_ride, name="complete"),
    path("<int:ride_id>/cancel/", views.cancel_ride, name="cancel"),
]
