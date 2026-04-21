import Temp from './_comp/Temp';

async function page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const path = searchParams.path || '';
  const token = searchParams.access_token || '';

  return <Temp {...{ path, token }} />;
}

export default page;
