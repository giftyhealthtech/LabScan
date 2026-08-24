from .models import User

def create_user(email, password, **extra_fields):
   
    user = User.objects.create_user(email=email, password=password, **extra_fields)
    return user