import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

export async function getFormsElements(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates/${id}`,
      method: 'GET',
    }),
  );
}
