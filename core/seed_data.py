import random
import string
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from faker import Faker

# Custom imports
from hackathon_ai_dashboard.core.models import User, Ticket, Bet


class Command(BaseCommand):
    help = "Seed the database with test Users, Tickets, and Bets"

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write("Seeding data...")

        # --- Create Users ---
        users = []
        for i in range(500):
            first_name = fake.first_name()
            last_name = fake.last_name()
            user = User.objects.create(
                user_code=f"USR{i+1:04d}",
                username=f"{first_name.lower()}{i+1}",
                email=f"{first_name.lower()}{i+1}@{fake.free_email_domain()}",
                first_name=first_name,
                last_name=last_name,
                role="player",
                kyc_verified=random.choice([True, False, False]),  # more unverified than verified
            )
            users.append(user)
        self.stdout.write(f"Created {len(users)} users")

        # --- Create Tickets ---
        tickets = []
        game_choices = ["Powerball", "MegaMillions", "EuroJackpot", "SuperLotto", "DailyLotto"]
        status_choices = ["active", "expired", "cancelled"]

        for user in users:
            for _ in range(random.randint(5, 12)):  # random number of tickets per user
                ticket = Ticket.objects.create(
                    user=user,
                    ticket_number="TKT" + "".join(random.choices(string.digits, k=8)),
                    game_name=random.choice(game_choices),
                    price=round(random.uniform(1.0, 50.0), 2),  # 1 to 50 USD
                    status=random.choice(status_choices),
                    draw_date=now() - timedelta(days=random.randint(0, 30)) + timedelta(days=random.randint(0, 30)),
                )
                tickets.append(ticket)
        self.stdout.write(f"Created {len(tickets)} tickets")

        # --- Create Bets ---
        bets = []
        bet_status_choices = ["pending", "won", "lost", "void"]

        for ticket in tickets:
            for _ in range(random.randint(1, 5)):  # 1–5 bets per ticket
                created_at = now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
                bet_amount = round(random.uniform(5.0, 500.0), 2)  # 5–500 USD
                potential_win = round(bet_amount * random.uniform(2, 20), 2)  # winnings depend on amount
                status = random.choice(bet_status_choices)
                resolved_at = created_at + timedelta(hours=random.randint(1, 48)) if status != "pending" else None

                bet = Bet.objects.create(
                    user=ticket.user,
                    ticket=ticket,
                    bet_amount=bet_amount,
                    potential_win=potential_win,
                    status=status,
                    resolved_at=resolved_at,
                )
                bets.append(bet)
        self.stdout.write(f"Created {len(bets)} bets")

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully with realistic random data!"))
