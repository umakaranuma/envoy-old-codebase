import '../../../public/styles/theme.css';
import '@apptimus-ui/theme/dist/components/styles/ynex/app.css';
import '../../../public/styles/custom.css';

export const metadata = {
  title: 'Vanguard X',
  description: 'Vanguard X - Your Insurance Partner',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
