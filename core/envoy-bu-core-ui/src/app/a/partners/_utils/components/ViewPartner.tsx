'use client';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { getOnePartner } from '../api-service';
import { initPartner } from '../model';
import ProductsList from './tabs/ProductsList';
import QuotationList from './tabs/QuotationList';
import ContactDetails from './tabs/ContactDetails';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { Button } from '@apptimus-ui/ui-element';
import GoBack from '@/components/others/page-related/GoBack';
import { EditPartner } from './EditPartner';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

function ViewPartner() {
  const t = useTrans('label.partners,otr.common');
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const partnerId = params.partnerId?.toString() || '';
  const [skeleton, setSkeleton] = useState(false);
  const [data, setData] = useState(initPartner);
  const [tab, setTab] = useState('products');
  const [currentEditId, setCurrentEditId] = useState('');
  const [comKey, setComKey] = useState(0);

  useEffect(() => {
    const tab = searchParams.get('t') || 'products';
    toggleTableTab(tab);
  }, [searchParams]);

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('view'),
      backurl: '/a/partners',
    });

    // cleanup on unmount
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb]);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/a/partners/${partnerId}?t=${activeTab}`, { scroll: false });
  };

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePartner(partnerId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setSkeleton(false);
      }
    };

    if (partnerId) {
      setSkeleton(true);
      fetchData();
    }
  }, [partnerId, comKey]);

  return (
    <>
      <GoBack goTo={() => router.push('/a/partners')} title={t('partner')} />
      <div className="panel">
        <div className="row">
          <div className="col-12 col-md-6 col-lg-2 mb-2">
            <ProfileInfo height={100} width={100} imageKey={data?.logo} shape="square" defaultImage="/images/default-profile.png" />
          </div>
          <div className="col-12 col-md-10">
            <div className="row">
              <div className="col-12 col-md-4 mb-4">
                <Description label={t('partner_name')} value={data?.name || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-4">
                <Description label={t('email')} value={data?.email || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-4">
                <Description label={t('contact_number')} value={data?.contact_no || '-'} skeleton={skeleton} />
              </div>
            </div>
            <div className="row">
              <div className="col-12 col-md-4 mb-4">
                <Description label={t('fax_number')} value={data?.fax_no || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-4">
                <Description label={t('address')} value={data?.address || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-4">
                <Description
                  label={t('website')}
                  value={
                    data?.website ? (
                      <a href={data?.website.startsWith('http') ? data?.website : `https://${data?.website}`} target="_blank" rel="noopener noreferrer" className="clickable-text">
                        View website
                      </a>
                    ) : (
                      '-'
                    )
                  }
                  skeleton={skeleton}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="panel">
        <div className="panel-title mb-2">{t('primary_contact')}</div>
        <div className="row">
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('contact_type')} value={data?.contact_details[0]?.is_primary ? 'Primary' : 'Secondary'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('salutation')} value={data?.contact_details[0]?.title || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('contact_person_name')} value={data?.contact_details[0]?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('email')} value={data?.contact_details[0]?.email || '-'} skeleton={skeleton} />
          </div>
        </div>
        <div className="row">
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('contact_number')} value={data?.contact_details[0]?.primary_contact || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('role')} value={data?.contact_details[0]?.role || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('remarks')} value={data?.contact_details[0]?.remarks || '-'} skeleton={skeleton} />
          </div>
        </div>
      </div>
      <div className="panel">
        <div className="panel-title mb-2">{t('bank_account_info')}</div>
        <div className="row">
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('account_holder_name')} value={data?.bank_details[0]?.account_holder_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('bank_name')} value={data?.bank_details[0]?.bank_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('bank_branch')} value={data?.bank_details[0]?.bank_branch || '-'} skeleton={skeleton} />
          </div>
        </div>
        <div className="row">
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('account_number')} value={data?.bank_details[0]?.account_number || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description label={t('isbn_swift_code')} value={data?.bank_details[0]?.iban_swift_code || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-2">
            <Description
              label={t('payment_gateway_url')}
              value={
                data?.bank_details[0]?.payment_gateway_url ? (
                  <a
                    href={data.bank_details[0]?.payment_gateway_url.startsWith('http') ? data.bank_details[0]?.payment_gateway_url : `https://${data.bank_details[0]?.payment_gateway_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="clickable-text"
                  >
                    {data.bank_details[0]?.payment_gateway_url}
                  </a>
                ) : (
                  '-'
                )
              }
              skeleton={skeleton}
            />
          </div>
        </div>

        <div className="d-flex justify-content-end mt-2">
          <Button type="button" className="d-flex align-items-center justify-content-center gap-1" width="sm" onClick={() => setCurrentEditId(data.id)}>
            <Flexicon icon={'edit-05'} variant="line" size={15} />
            <span className="d-none d-sm-inline">{t('edit')}</span>
          </Button>
        </div>
      </div>
      <div className="panel">
        <div className="il-box-tab py-2 my-2">
          <div className={`il-box-tab-item ${tab === 'products' ? 'active' : ''}`} onClick={() => toggleTableTab('products')}>
            {t('products_provided')}
          </div>
          <div className={`il-box-tab-item ${tab === 'contact_details' ? 'active' : ''}`} onClick={() => toggleTableTab('contact_details')}>
            {t('partner_contact_details')}
          </div>
          <div className={`il-box-tab-item ${tab === 'quotations' ? 'active' : ''}`} onClick={() => toggleTableTab('quotations')}>
            {t('received_quotation')}
          </div>
        </div>
        {tab === 'products' && <ProductsList partnerId={partnerId} />}
        {tab === 'quotations' && <QuotationList partnerId={partnerId} />}
        {tab === 'contact_details' && <ContactDetails partnerId={partnerId} setComKey={setComKey} />}
      </div>
      {currentEditId !== '' && (
        <EditPartner
          isOpen={currentEditId !== ''}
          onCancel={() => setCurrentEditId('')}
          afterEdit={() => {
            setComKey((prev) => prev + 1);
          }}
          editId={currentEditId}
        />
      )}
    </>
  );
}

export default ViewPartner;
