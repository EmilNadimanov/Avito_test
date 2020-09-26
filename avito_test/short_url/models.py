from django.db import models


class ShortLink(models.Model):
    old_link = models.CharField(max_length=150)  # субъективно - разумный предел для длины URL
    new_link = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)  # сохраняем время создания, чтобы удалить по истечении срока Икс

    def __str__(self):
        return self.old_link + '|' + self.new_link

    class Meta:
        ordering = ['-created']


