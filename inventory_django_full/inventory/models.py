from django.db import models

class InventoryItem(models.Model):
    part_number = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.part_number
    

from django.contrib.auth.models import User

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Agregar'),
        ('edit', 'Editar'),
        ('delete', 'Eliminar'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity_before = models.IntegerField(null=True, blank=True)
    quantity_after = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.change_type} - {self.item.part_number} ({self.timestamp})"
