from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ("player", "Player"),
        ("admin", "Admin"),
    ]

    user_code = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="player")
    is_active = models.BooleanField(default=True)
    kyc_verified = models.BooleanField(default=False)

    sign_in_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({'KYC' if self.kyc_verified else 'No-KYC'})"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    ticket_number = models.CharField(max_length=100)
    game_name = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    purchased_at = models.DateTimeField(auto_now_add=True)
    draw_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.user.username}"


class Bet(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("won", "Won"),
        ("lost", "Lost"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bets")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="bets")

    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    potential_win = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    placed_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bet {self.id} - {self.user.username} (${self.bet_amount})"
