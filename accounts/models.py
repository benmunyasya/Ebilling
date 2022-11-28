from django.db import models
class UserNotifications(models.Model):
    
    message = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.message}"
    
    class Meta:
        verbose_name = "Notifications"
        verbose_name_plural = verbose_name