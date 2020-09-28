from django.db import models


class ShortLink(models.Model):
    full_link = models.CharField(max_length=250, default='')  # субъективно разумный предел для URL
    short_link = models.CharField(max_length=25, default='')
    created = models.DateTimeField(auto_now_add=True)  # удобное значение для упорядочения

    def __str__(self):
        return "full_link: " + self.full_link + ' | short_link: ' + self.short_link

    class Meta:
        ordering = ['-created']
