

from celery import shared_task
import asyncio


@shared_task
async def token_delay(pk):
    from users.models import CustomUser

    print('[+]CELERY START')
    await asyncio.sleep(100)
    CustomUser.objects.filter(pk=pk).update(email_verification_token=None)
    print('[+]CELERY END')
    return