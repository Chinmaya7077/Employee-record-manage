
from django.db import models


# Create your models here.
class Technology(models.Model):  # Corrected model name to "Technology" (follow PascalCase convention)
    name = models.CharField(max_length=50)  # Added max_length to CharField (required)

    def __str__(self):
        return self.name


class task(models.Model):  # Corrected model name to "Task" (follow PascalCase convention)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mail_id = models.EmailField(max_length=100,unique=True)  # Changed to EmailField for better validation
    technology = models.ManyToManyField(Technology)  # Use ForeignKey for relationships
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name
    
    
    class Meta:
        ordering = ['-id'] 
