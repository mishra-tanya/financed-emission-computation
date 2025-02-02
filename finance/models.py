from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.user.username
    
class ContactMessages(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Company(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="companies")
    company_name = models.CharField(max_length=100)
    sector = models.CharField(max_length=150)
    geography = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} (User ID: {self.user_id.id})"

class AssetClass(models.Model):
    asset_class_name = models.CharField(max_length=200)
    input_fields = models.JSONField() 
    others = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asset Classes {self.asset_class_name}"

class LoanInvestment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loan_investments")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="loan_investments")  
    asset_class = models.CharField(max_length=200)
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan Investment for {self.company.company_name} (User ID: {self.company.user_id.id})"

class EmissionFactor(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emission_factors")
    asset_class = models.CharField(max_length=200)
    emission_factors = models.JSONField()
    data_quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emission factor for {self.company.company_name} (User ID: {self.company.user_id.id})"

