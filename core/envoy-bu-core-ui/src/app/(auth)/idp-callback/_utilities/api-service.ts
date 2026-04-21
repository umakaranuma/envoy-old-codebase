import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

export async function validateInvitation(token: string, invitation: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/verify-invitation`,
    method: 'POST',
    data: { invitation, idp_access_token: token },
  });

  return responseHandling(response);
}

export async function validateToken(token: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/login`,
    method: 'POST',
    data: { idp_access_token: token },
  });

  return responseHandling(response);
}
