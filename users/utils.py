from .models import CustomUser


def clean_token(pk):

    CustomUser.objects.filter(pk=pk).update(email_verification_token='Null')
    return
