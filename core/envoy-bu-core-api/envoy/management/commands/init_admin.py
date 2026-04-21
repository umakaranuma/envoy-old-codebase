import sys
from django.core.management.base import BaseCommand
from envoy.models import Entity, Role, Action, RoleAuthority, UserInvitation
from envoy.utils import send_invitation_email

class Command(BaseCommand):
    help = "Initialize Entity, Super Admin role, assign permissions, and send invitation"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email', 
            type=str, 
            help="Email to send invitation to",
            required=True
        )

    def handle(self, *args, **options):
        email = options.get('email')
        
        # Ensure the email is provided
        if not email:
            self.stdout.write(self.style.ERROR("Error: Please provide an email using -email"))
            sys.exit(1)

        # Step 1: Create the Entity
        entity, created = Entity.objects.get_or_create(type="System Admin Entity")
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Entity: {entity.type}"))
        else:
            self.stdout.write(self.style.WARNING("Entity already exists."))

        # Step 2: Create the Super Admin Role
        role, created = Role.objects.get_or_create(
            system_role="SYSTEM_ADMIN",
            defaults={
                "name": "Super Admin",
                "description": "",
                "entity_id": entity.id,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Role: {role.name}"))
        else:
            self.stdout.write(self.style.WARNING("Role already exists."))

        # Step 3: Assign Permissions (filtered by can_be_permission=True)
        actions = Action.objects.filter(can_be_permission=True)
        for action in actions:
            RoleAuthority.objects.get_or_create(
                role_id=role.id,  # Pass the primary key of the Role
                action_id=action.id  # Pass the primary key of the Action
            )

        self.stdout.write(self.style.SUCCESS("Assigned all actions to Super Admin Role."))

        # Step 4: Create User Invitation and Send Email
        invitation, created = UserInvitation.objects.get_or_create(
            name="Super Admin",
            email=email,
            role_id=role.id,  # Pass the primary key of the Role
        )
        if created:
            send_invitation_email(invitation, "invitation_email_template.html", "You're Invited!")
            self.stdout.write(self.style.SUCCESS(f"Invitation sent to {email}."))
        else:
            self.stdout.write(self.style.WARNING(f"Invitation already exists for {email}."))