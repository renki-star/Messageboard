from django.db import models

class Message(models.Model):
    username = models.CharField(max_length=100)
    text = models.TextField()
    approved = models.BooleanField(default=False)  # Hyväksyntätilanne
    timestamp = models.DateTimeField(auto_now_add=True)  # Automaattinen aikaleima

    def __str__(self):
        return f"{self.username}: {self.text}"
