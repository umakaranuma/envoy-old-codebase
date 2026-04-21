import { getAppMenu } from '@/helpers/services/serverSideServices';

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const moduleKey = url.searchParams.get('module_key');

    if (!moduleKey) {
      return new Response(JSON.stringify({ error: 'Missing required field: module_key' }), { status: 400 });
    }

    const appMenu = await getAppMenu();

    return new Response(JSON.stringify({ menu: appMenu }), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to retrieve data' }), { status: 500 });
  }
}
