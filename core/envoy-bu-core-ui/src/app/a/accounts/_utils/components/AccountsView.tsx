'use client';
import { useEffect, useState } from 'react';
import { getAllPrimaryContact, getOneCustomers } from '../api-service';
import { ICustomers } from '../model';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import OtherContacts from '../../other-contacts/OtherContacts';
import { IContacts } from '@/app/a/contacts/_utils/model';
import { IEntity, useFlexField } from '@/components/others/FlexFiled';
import { getOneEntity } from '@/helpers/services/api-service';
import InterestedProducts from './interested-products/InterestedProducts';
import Leads from './leads/Leads';
import Notes from './notes/Notes';
import Policies from './policies/Policies';
import Interactions from './interactions/Interactions';
import GoBack from '@/components/others/page-related/GoBack';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { formatPhoneNumber } from '@/helpers/services/commonService';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { AccountsEdit } from './AccountsEdit';

export const AccountsView = () => {
  const t = useTrans('label.accounts,otr.common,otr.permanent_flex_field');
  const { fields } = useFlexField('CUSTOMER');
  const [data, setData] = useState({} as ICustomers);
  const [skeleton, setSkeleton] = useState(true);
  const [flexSkeleton, setFlexSkeleton] = useState(true);
  const router = useRouter();
  const params = useParams();
  const viewId = params.accountId?.toString() || '';
  const [tab, setTab] = useState('otherContacts');
  const [primaryContactPerson, setPrimaryContactPerson] = useState(null as IContacts | null);
  const [entityData, setEntityData] = useState({} as IEntity);
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [currentEditId, setCurrentEditId] = useState('');

  useEffect(() => {
    setCustomBreadcrumb({
      text: data.code ? data.code : '',
      backurl: '/a/accounts',
    });
    return () => setCustomBreadcrumb(null);
  }, [data]);

  const fetchPrimaryContactPerson = async () => {
    const response = await getAllPrimaryContact({ ids: viewId });
    if (response.is_success && response.result[viewId] && response.result[viewId].length > 0) {
      setPrimaryContactPerson(response.result[viewId][0]);
    } else {
      setPrimaryContactPerson(null);
    }
  };

  useEffect(() => {
    fetchPrimaryContactPerson();
  }, [viewId]);

  useEffect(() => {
    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const fetchData = async () => {
    const responseData = await getOneCustomers(viewId);
    if (responseData?.is_success) {
      setData(responseData.result);
      setSkeleton(false);

      if (responseData.result.entity_id) {
        setFlexSkeleton(true);
        const responseFlex = await getOneEntity(responseData.result.entity_id, 'flex_field_values');

        if (responseFlex?.is_success) {
          setEntityData(responseFlex.result);
        }
      }
      setFlexSkeleton(false);
    }
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    fetchData();
  };

  return (
    <>
      <GoBack goTo={() => router.push('/a/accounts')} title={t('account_view')} skeleton={skeleton} />
      <div className="bg-white custom-card overflow-hidden p-2 px-4 pt-2 rounded-3">
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('account_name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('account_type')} value={data?.type || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('email')} value={data?.primary_contact?.email || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('address')} value={data?.primary_contact?.address || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description
              label={t('website')}
              value={
                data?.primary_contact?.website_url ? (
                  <a
                    href={data.primary_contact.website_url.startsWith('http') ? data.primary_contact.website_url : `https://${data.primary_contact.website_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="clickable-text"
                  >
                    {data.primary_contact.website_url}
                  </a>
                ) : (
                  '-'
                )
              }
              skeleton={skeleton}
            />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('primary_contact_number')} value={formatPhoneNumber(data?.primary_contact?.primary_contact) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('secondary_contact_number')} value={formatPhoneNumber(data?.primary_contact?.secondary_contact as string) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('remarks')} value={data?.remarks || '-'} skeleton={skeleton} />
          </div>
          {fields
            .filter((field) => field.field_code !== 'number_of_employees')
            .map((field) => (
              <div className="col-12 col-md-6 mb-3" key={field.id}>
                <Description
                  label={t(field.field_code)}
                  value={entityData.flex_field_values && entityData.flex_field_values[field.id] ? entityData.flex_field_values[field.id] : flexSkeleton ? '-' : ''}
                  skeleton={flexSkeleton}
                />
              </div>
            ))}
        </div>

        {primaryContactPerson && (
          <div className="row">
            <div className="col-12 mb-3">
              <div className="panel-title">{t('primary_contact_person')}</div>
            </div>
            <div className="col-12 col-md-4 mb-3">
              <ProfileInfo
                height={35}
                width={35}
                imageKey={primaryContactPerson.picture}
                defaultImage="/images/empty-avatar.png"
                title={primaryContactPerson.name}
                subtitle={primaryContactPerson.primary_contact}
              />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('primary_contact_number')} value={formatPhoneNumber(primaryContactPerson?.primary_contact as string) || '-'} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('secondary_contact_number')} value={formatPhoneNumber(String(primaryContactPerson?.secondary_contact || '')) || '-'} />
            </div>
          </div>
        )}
        <div className="d-flex justify-content-end">
          <Button onClick={() => setCurrentEditId(viewId)}>
            <span className="d-flex gap-2">
              <Flexicon icon="pencil-line" variant="line" size={17} />
              <span>{t('edit')}</span>
            </span>
          </Button>
        </div>
      </div>

      <div className="panel mt-2">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${tab === 'otherContacts' ? 'active' : ''}`} onClick={() => setTab('otherContacts')}>
            {t('other_contacts')}
          </div>
          <div className={`il-box-tab-item ${tab === 'interested-products' ? 'active' : ''}`} onClick={() => setTab('interested-products')}>
            {t('interested_products')}
          </div>
          <div className={`il-box-tab-item ${tab === 'leads' ? 'active' : ''}`} onClick={() => setTab('leads')}>
            {t('leads')}
          </div>
          <div className={`il-box-tab-item ${tab === 'policies' ? 'active' : ''}`} onClick={() => setTab('policies')}>
            {t('policies')}
          </div>
          <div className={`il-box-tab-item ${tab === 'interactions' ? 'active' : ''}`} onClick={() => setTab('interactions')}>
            {t('interactions')}
          </div>
          <div className={`il-box-tab-item ${tab === 'notes' ? 'active' : ''}`} onClick={() => setTab('notes')}>
            {t('notes')}
          </div>
        </div>
        <div>
          {tab === 'otherContacts' && <OtherContacts id={viewId} afterSetPrimaryContact={() => fetchPrimaryContactPerson()} afterDelete={() => fetchPrimaryContactPerson()} />}
          {tab === 'interested-products' && <InterestedProducts viewId={viewId} curentTap={tab} />}
          {tab === 'leads' && <Leads viewId={viewId} curentTap={tab} />}
          {tab === 'policies' && <Policies viewId={viewId} curentTap={tab} />}
          {tab === 'interactions' && <Interactions viewId={viewId} curentTap={tab} />}
          {tab === 'notes' && <Notes viewId={viewId} curentTap={tab} />}
        </div>
        {currentEditId !== '' && <AccountsEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      </div>
    </>
  );
};
