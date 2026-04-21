import { Metadata } from 'next';
import Welcome from './_utils/components/Welcome';

export const metadata: Metadata = {
  title: 'Welcome',
};

async function Page(props: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const searchParams = await props.searchParams;
  const redirect = searchParams.redirect?.toString() || '';
  const idp = searchParams.idp?.toString() || '';
  const sp = searchParams.sp?.toString() || '';

  return <Welcome redirect={redirect} sp={sp} idp={idp} />;
}

export default Page;
