from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.Login, name='login'),  # Ensure this matches your view
    path('logout/', views.Logout, name='logout'),
    path('signup/', views.Signup, name='signup'),
    path('<int:myid>/', views.quiz, name='quiz'),
    path('<int:myid>/data/', views.quiz_data_view, name='quiz-data'),
    path('<int:myid>/save/', views.save_quiz_view, name='quiz-save'),
    path('add_quiz/', views.add_quiz, name='add_quiz'),
    path('add_question/', views.add_question, name='add_question'),
    path('add_options/<int:myid>/', views.add_options, name='add_options'),
    path('results/', views.results, name='results'),
    path('delete_question/<int:myid>/', views.delete_question, name='delete_question'),
    path('delete_results/<int:myid>/', views.delete_result, name='delete_results'),
]