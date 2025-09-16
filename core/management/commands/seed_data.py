# lottery/management/commands/seed_data.py
import random
import string
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import User, Ticket, Bet


class Command(BaseCommand):
    help = "Seed the database with test Users, Tickets, and Bets"

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write("Seeding data...")

        # ---- Base date fix ----
        base_date = datetime(2024, 1, 1)  # FIXED STARTING POINT

        # --- Create Users ---
        users = []
        for i in range(500):
            first_name = fake.first_name()
            last_name = fake.last_name()

            created_at = base_date + timedelta(days=random.randint(0, 365))
            updated_at = created_at + timedelta(days=random.randint(0, 30))

            user = User.objects.create(
                user_code=f"USR{i+1:04d}",
                username=f"{first_name.lower()}{i+1}",
                email=f"{first_name.lower()}{i+1}@{fake.free_email_domain()}",
                first_name=first_name,
                last_name=last_name,
                role="player",
                kyc_verified=random.choice([True, False, False]),
                created_at=created_at,
                updated_at=updated_at,
                last_login=updated_at,
                sign_in_ip=fake.ipv4(),
            )
            users.append(user)
        self.stdout.write(f"Created {len(users)} users")

        # --- Create Tickets ---
        tickets = []
        game_choices = ["Powerball", "MegaMillions", "EuroJackpot", "SuperLotto", "DailyLotto"]
        status_choices = ["active", "expired", "cancelled"]

        for user in users:
            for _ in range(random.randint(5, 12)):
                created_at = base_date + timedelta(days=random.randint(0, 365))
                updated_at = created_at + timedelta(days=random.randint(0, 15))
                draw_date = created_at + timedelta(days=random.randint(1, 30))

                ticket = Ticket.objects.create(
                    user=user,
                    ticket_number="TKT" + "".join(random.choices(string.digits, k=8)),
                    game_name=random.choice(game_choices),
                    price=round(random.uniform(1.0, 50.0), 2),
                    status=random.choice(status_choices),
                    draw_date=draw_date,
                    created_at=created_at,
                    updated_at=updated_at,
                    purchased_at=created_at,
                )
                tickets.append(ticket)
        self.stdout.write(f"Created {len(tickets)} tickets")

        # --- Create Bets ---
        bets = []
        bet_status_choices = ["pending", "won", "lost"]

        for ticket in tickets:
            for _ in range(random.randint(1, 5)):
                created_at = base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
                updated_at = created_at + timedelta(hours=random.randint(1, 72))
                bet_amount = round(random.uniform(5.0, 500.0), 2)
                potential_win = round(bet_amount * random.uniform(2, 20), 2)
                status = random.choice(bet_status_choices)
                resolved_at = updated_at if status != "pending" else None

                bet = Bet.objects.create(
                    user=ticket.user,
                    ticket=ticket,
                    bet_amount=bet_amount,
                    potential_win=potential_win,
                    status=status,
                    resolved_at=resolved_at,
                    created_at=created_at,
                    updated_at=updated_at,
                    placed_at=created_at,
                )
                bets.append(bet)
        self.stdout.write(f"Created {len(bets)} bets")

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully with FIXED random dates!"))