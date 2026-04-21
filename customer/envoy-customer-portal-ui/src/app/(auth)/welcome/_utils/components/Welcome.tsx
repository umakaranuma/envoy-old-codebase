'use client';
import React from 'react';
import desktopLogo from '../../../../../../public/logo/desktop-logo.png';
import welcomeImage from '../../../../../../public/images/welcome.png';
import Image from 'next/image';
import { Button } from '@apptimus-ui/ui-element';

function Welcome({ sp, idp, redirect }: { sp: string; idp: string; redirect: string }) {
  const handleNavigateToLogin = () => {
    const newUrl = `${idp}/login?sp=${sp}&redirect=${encodeURIComponent(`${redirect}/idp-callback`)}`;
    window.location.href = newUrl;
  };

  return (
    <div className="welcome-page">
      <div className="mb-3">
        <Image src={desktopLogo} width={140} alt="logo" className="desktop-logo" />
      </div>
      <div className="row">
        <div className="col-12 col-md-6">
          <div>
            <div className="text-uppercase text-muted">Your One Stop Solution for Insurance Management</div>
            {/* <div className='fw-bold ' style={{ fontSize: '2rem' }}>{t('welcome_to_your')} <span>Vanguard X</span><span className='text-primary'>!</span></div> */}
            <div className="fw-bold heading-text">
              Welcome to <span className="text-primary">Vanguard X</span> <span> self-care portal</span>
            </div>
            {/* <div className="fw-bold heading-text">Self Care Portal!</div> */}
            {/* <div className='fw-bold ' style={{ fontSize: '2rem' }}>{t('selfcare_portal')}</div> */}
            <div className="text-muted mt-2">
              At Vanguard X Insurance, we prioritize your peace of mind. Our customer portal provides you with easy access to your insurance information, making it simple to manage your quotes,
              policies, and claims all in one secure location.
            </div>
          </div>
          <div className="mt-3 p-3 border rounded shadow-sm bg-white" style={{ width: 'fit-content' }}>
            <div className="fw-medium fs-18">Access Your Portal.</div>
            <div className="text-muted">Your Phone Number is securely encrypted to protect your privacy.</div>
            {/* <div className="d-flex flex-row align-items-center gap-1 mt-2">
              <div>
                <S3Avatar imageKey={undefined} width={50} height={50} />
              </div>
              <div>
                <div className="fs-15 fw-medium">Alex Jones</div>
                <div className="fs-13 text-muted">+94 XX XXX 21100</div>
              </div>
            </div> */}
            <div className="mt-3">
              <Button text={'Login'} onClick={handleNavigateToLogin} />
            </div>
          </div>
          <div className="d-flex flex-row flex-wrap gap-2 mt-4 justify-content-between align-items-center p-3 rounded shadow-sm bg-white">
            <div className="d-flex flex-row gap-2 align-items-center">
              <div>
                <svg className="text-primary" width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M11 15V11M11 7H11.01M21 11C21 16.5228 16.5228 21 11 21C5.47715 21 1 16.5228 1 11C1 5.47715 5.47715 1 11 1C16.5228 1 21 5.47715 21 11Z"
                    stroke="#09729A"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div>
                <div className="fw-medium">Need help?</div>
                <div className="text-muted">Speak to an Vanguard X expert using live chat</div>
              </div>
            </div>
            <div>
              <Button text="Contact Agent" variant="outline" />
            </div>
          </div>
        </div>
        <div className="col-12 col-md-6">
          <Image src={welcomeImage} width={832} height={602} alt="welcome-image" className="img-fluid" />
        </div>
      </div>
      <div className="fw-bold heading-text mb-2">How It Works:</div>
      <div className="d-flex flex-row flex-wrap flex-lg-nowrap gap-3">
        {data.map((item, index) => (
          <HowWorkCard step={item.step} title={item.title} description={item.description} key={index} />
        ))}
      </div>
    </div>
  );
}

export default Welcome;

const data = [
  {
    step: 1,
    title: 'Request a Quotation',
    description: 'Start by submitting a request for a quotation for the insurance product that fits your needs.',
  },
  {
    step: 2,
    title: 'Confirm Your Quotation',
    description: 'Review the quotation details and confirm it to proceed with the policy issuance.',
  },
  {
    step: 3,
    title: 'Receive Your Policy',
    description: 'Once the quotation is confirmed, your insurance policy will be issued and made available in your portal.',
  },
  {
    step: 4,
    title: 'Manage Your Policy',
    description: 'Access and manage your policy details, including payments, coverage options, and endorsements.',
  },
  {
    step: 5,
    title: 'Stay Updated',
    description: 'Receive notifications and updates from your insurer or broker to stay informed about your policy status and any upcoming actions.',
  },
];

export const HowWorkCard = ({ step, title, description }: { step: number; title: string; description: string }) => {
  return (
    <div className="card position-relative p-3 border rounded shadow-sm border border-primary w-100">
      <div className="position-absolute fw-medium top-0 end-0 bg-primary text-white rounded-bottom px-3 mx-2 py-1">{step}</div>
      <h6 className="fw-bold mb-2 text-nowrap">{title}</h6>
      <p className="text-muted fs-14 mb-0">{description}</p>
    </div>
  );
};
