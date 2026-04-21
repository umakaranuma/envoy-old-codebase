

from envoy_bu_crm_api.sales.models.core_models import RoleAuthority


class AuthService:
    @staticmethod
    def hasAuthority(request, action):
        # user = request.user
        # print("Authenticated User:", user.id)

        # if not user or not user.is_authenticated:
        #     return False

        # if not action or not isinstance(action, dict) or "id" not in action:
        #     return False

        # role_id = getattr(user.role, "id", None)
        # if not role_id:
        #     return False

        # return RoleAuthority.objects.filter(
        #     role_id=role_id,
        #     action_id=action["id"]
        # ).exists()

        return True
