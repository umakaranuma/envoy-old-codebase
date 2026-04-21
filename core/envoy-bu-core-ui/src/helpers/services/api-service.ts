import sendRequest from 'apptimus-netlink';
import { responseHandling } from '../handlers/responseHandler';

export async function getOneEntity(id: string, attri: string = '') {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities/${id}?attri=${attri}`,
      method: 'GET',
    }),
  );
}
