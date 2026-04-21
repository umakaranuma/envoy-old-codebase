'use client';
import { useEffect, useState } from 'react';
import { Button, Label, Skeleton } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useSearchParams } from 'next/navigation';
import { getOneContacts, getOneEntities, getOneOpportunity } from '../api-service';
import { IEntities, IOpportunity, IFlagResons, IContacts } from '../model';
import { Description } from '@/components/others/Description';
import { useRouter } from 'next/navigation';
import Tasks from './tabs/tasks/Tasks';
import HealthHistory from './tabs/health/HealthHistory';
import RatingBlock from '@/components/others/page-related/RatingBlock';
import OpportunityTypes from './tabs/opportunity-type/OpportunityTypes';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import Notes from './tabs/notes/Notes';
import InterestedProducts from './tabs/interested-products/InterestedProducts';
import OpportunityInteraction from './tabs/op-interaction/OpportunityInteraction';
import { Flexicon } from '@apptimus-ui/flexicon';
import { convertUTCTimeToLocal, formatDate, hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import FlagCreate from './flag/FlagCreate';
import { FlagDelete } from './flag/FlagDelete';
import Quotation from './tabs/quotation/Quotation';
import RecommendationDocumentation from '../../../quotations/_utils/components/view/recommandation-document/RecommendationDocumentation';
import GoBack from '@/components/others/page-related/GoBack';
import Policies from './tabs/policies/Policies';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import ReassignmentList from './tabs/reassignment/ReassignmentList';
import { SalesManagementsEdit } from './SalesManagementsEdit';

export const SalesManagementsView = () => {
  const t = useTrans('label.sales_managements,otr.common');
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [data, setData] = useState({} as IOpportunity);
  const [skeleton, setSkeleton] = useState(true);
  // const [isOpen, setIsOpen] = useState(false);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  // const [currentEditId, setCurrentEditId] = useState(viewId);
  const router = useRouter();
  const [tab, setTab] = useState('tasks');
  const searchParams = useSearchParams();
  const [createFormKey, setCreateFormKey] = useState(0);
  const [tableVers, setTableVers] = useState(0);
  const [flagModel, setFlagModel] = useState(false);
  const [dataEntities, setDataEntities] = useState({} as IEntities);
  const [singleFlagDeleteModel, setSingleFlagDeleteModel] = useState(false);
  const [dataSingleFlag, setDataSingleFlag] = useState({} as IFlagResons);
  const [contactData, setContactData] = useState({} as IContacts);
  const [currentEditId, setCurrentEditId] = useState('');
  const flags = 'flags';

  useEffect(() => {
    setCustomBreadcrumb({
      text: data?.code,
      backurl: '/crm/a/sales-management',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, data]);

  useEffect(() => {
    console.log(contactData);
  }, [contactData]);

  const handleCreateFormOnCancel = () => {
    setFlagModel(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setFlagModel(false);
  };

  const handleAfterDelete = () => {
    setSingleFlagDeleteModel(false);
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  useEffect(() => {
    const fetchData = async () => {
      if (data.entity_id) {
        const responseData = await getOneEntities(flags, data.entity_id.toString());
        setDataEntities(responseData.result);
      }
    };
    fetchData();
  }, [data.entity_id, tableVers]);

  const fetchData = async () => {
    const responseData = await getOneOpportunity(opportunityId);
    if (responseData?.is_success) {
      setData(responseData.result);
      const contactId = responseData?.result?.contact_id || '';
      if (contactId) {
        const response = await getOneContacts(contactId);
        if (response.is_success) {
          setContactData(response.result);
        }
      }
      setSkeleton(false);
    }
  };

  useEffect(() => {
    if (opportunityId) {
      setSkeleton(true);
      fetchData();
    }
  }, [opportunityId, tableVers]);

  useEffect(() => {
    const tab = searchParams.get('t') || 'tasks';
    toggleTableTab(tab);
  }, [searchParams]);

  // const handleAfterUpdate = () => {
  //   setIsOpen(false); // Close modal after update
  //   setCurrentEditId('');
  // };

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/crm/a/sales-management/${opportunityId}?t=${activeTab}&f=${searchParams.get('f') || 'board'}`, { scroll: false });
  };

  const handleSingleFlag = () => {
    setSingleFlagDeleteModel(true);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    fetchData();
  };

  return (
    <>
      <div className="d-flex gap-2">
        <GoBack goTo={() => router.push(`/crm/a/sales-management?act=${searchParams.get('f') || 'board'}`)} title={data.title} skeleton={skeleton} />
        <div className="d-flex align-items-center pb-4 flex-row gap-2">
          <div
            className={`rounded-5 fw-semibold badge ms-3`}
            style={{ background: hexToRgba(data?.stage_color ?? '', 0.1), border: `1px solid ${hexToRgba(data?.stage_color ?? '', 0.4)}`, color: data.stage_color }}
          >
            {data.stage_name}
          </div>
        </div>
        <div className="d-flex gap-3">
          {dataEntities?.flags?.map((data: IFlagResons, i: number) => (
            <div key={i} className="fs-15 fw-medium pointer">
              <div
                className="rounded-5 fw-semibold badge"
                onClick={() => {
                  handleSingleFlag(), setDataSingleFlag(data);
                }}
                style={{
                  background: hexToRgba(data.color, 0.1),
                  border: `1px solid ${hexToRgba(data.color, 0.4)}`,
                  color: data.color,
                }}
              >
                <div className="d-flex align-items-center justify-content-center gap-1" style={{ color: data.color }}>
                  <Flexicon icon="flag-01" variant="solid" size={10} />
                  {data.name}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="pointer" title={t('add_flag')} onClick={() => setFlagModel(true)}>
          <Flexicon icon="alert-circle" variant="line" />
        </div>
      </div>
      <div className="panel">
        <div className="row">
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('code')} value={data?.code || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('account_type')} value={data?.type || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('product_name')} value={data?.product_name || data.product_group_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('channel')} value={data?.channel_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Label label={t('health')} />
            {skeleton ? <Skeleton width={'65%'} height={'24px'} /> : <RatingBlock value={data?.health_value || 0} />}
          </div>
          {/* <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('compaign')} value={data?.campaign_id || '-'} skeleton={skeleton} />
          </div> */}
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('currency')} value={data?.currency_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('last_contact_date')} value={formatDate(data?.last_contacted_date as string) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('remarks')} isTruncate={false} value={data?.remarks || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <div className={`custom-description`}>
              <Label label={t('sales_agent')} />
              {skeleton ? (
                <Skeleton width={'65%'} height={'24px'} />
              ) : (
                <div className="d-flex align-items-center">
                  <S3Avatar imageKey={undefined} width={20} height={20} />
                  <span className="fs-13">{data.sales_agent_name}</span>
                </div>
              )}
            </div>
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            {/* <Description label={t('account_manager')} value={data?.account_manager_name || '-'} skeleton={skeleton} /> */}
            <div className={`custom-description`}>
              <Label label={t('account_manager')} />
              {skeleton ? (
                <Skeleton width={'65%'} height={'24px'} />
              ) : (
                <div className="d-flex align-items-center gap-2">
                  <S3Avatar imageKey={data?.account_manager_picture ?? undefined} width={20} height={20} />
                  <span className="fs-13">{data?.account_manager_name}</span>
                </div>
              )}
            </div>
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <div className={`custom-description`}>
              <Label label={t('created_by')} />
              {skeleton ? (
                <Skeleton width={'65%'} height={'24px'} />
              ) : (
                <div className="d-flex align-items-center">
                  <S3Avatar imageKey={data?.entity?.created_by_profile ?? undefined} width={20} height={20} />
                  <span className="fs-13">{data?.entity?.created_by_name}</span>
                </div>
              )}
            </div>
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('created_date')} value={convertUTCTimeToLocal(data?.entity?.created_at) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <div className={`custom-description`}>
              <Label label={t('last_updated_by')} />
              {skeleton ? (
                <Skeleton width={'65%'} height={'24px'} />
              ) : (
                <div className="d-flex align-items-center gap-2">
                  <S3Avatar imageKey={data?.entity?.updated_by_profile ?? undefined} width={20} height={20} />
                  <span className="fs-13">{data?.entity?.updated_by_name}</span>
                </div>
              )}
            </div>
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('lead_value')} value={thousandSeparator(data?.lead_value ?? '') || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('sale_value')} value={thousandSeparator(data?.sale_value ?? '') || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('country')} value={data?.country_name || '-'} skeleton={skeleton} />
          </div>
        </div>
        {/* <div className="panel-title">{customerData?.name ? t('customer_info') : t('contact_info')}</div> */}
        <div className="row">
          {data?.customer_contact_email ? (
            <>
              <div className="panel-title">{t('customer_info')}</div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('full_name')} value={data?.customer_contact_name} skeleton={skeleton} />
              </div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('email')} value={data?.customer_contact_email} skeleton={skeleton} />
              </div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('contact_number')} value={data?.customer_contact_phone} skeleton={skeleton} />
              </div>
            </>
          ) : contactData.name ? (
            <>
              <div className="panel-title">{t('contact_info')}</div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('full_name')} value={contactData.name || '-'} skeleton={skeleton} />
              </div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('email')} value={contactData.email || '-'} skeleton={skeleton} />
              </div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('contact_number')} value={contactData.primary_contact || '-'} skeleton={skeleton} />
              </div>
            </>
          ) : (
            <>
              <div className="panel-title">{t('contact_info')}</div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('email')} value={data.email || '-'} skeleton={skeleton} />
              </div>
              <div className="col-6 col-md-6 col-lg-4 mb-3">
                <Description label={t('contact_number')} value={data.contact_number || '-'} skeleton={skeleton} />
              </div>
            </>
          )}
          <div className="d-flex justify-content-end">
            <Button onClick={() => setCurrentEditId(opportunityId)}>
              <span className="d-flex gap-2">
                <Flexicon icon="pencil-line" variant="line" size={17} />
                <span>{t('edit')}</span>
              </span>
            </Button>
          </div>
        </div>

        {/* <div className="row">
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('created_by')} value={data?.created_by_id || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('created_date')} value={data?.created_by_id || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('last_updated_by')} value={data?.created_by_id || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('updated_date')} value={data?.created_by_id || '-'} skeleton={skeleton} />
          </div>
        </div> */}
        {/* <div className="d-flex justify-content-end gap-2">
          <Button text={t('edit_leads')}  width="sm" onClick={() => setIsOpen(true)} />
        </div> */}
      </div>

      <div className="panel">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${tab === 'tasks' ? 'active' : ''}`} onClick={() => toggleTableTab('tasks')}>
            {t('tasks')}
          </div>
          <div className={`il-box-tab-item ${tab === 'health' ? 'active' : ''}`} onClick={() => toggleTableTab('health')}>
            {t('health_history')}
          </div>
          <div className={`il-box-tab-item ${tab === 'interested' ? 'active' : ''}`} onClick={() => toggleTableTab('interested')}>
            {t('interested_products')}
          </div>
          <div className={`il-box-tab-item ${tab === 'interactions' ? 'active' : ''}`} onClick={() => toggleTableTab('interactions')}>
            {t('interactions')}
          </div>
          <div className={`il-box-tab-item ${tab === 'notes' ? 'active' : ''}`} onClick={() => toggleTableTab('notes')}>
            {t('notes')}
          </div>
          <div className={`il-box-tab-item ${tab === 'opp-type' ? 'active' : ''}`} onClick={() => toggleTableTab('opp-type')}>
            {t('risk_type')}
          </div>
          <div className={`il-box-tab-item ${tab === 'quotation' ? 'active' : ''}`} onClick={() => toggleTableTab('quotation')}>
            {t('quotation')}
          </div>
          {data.quotation_id && (
            <div className={`il-box-tab-item ${tab === 'recommendation-document' ? 'active' : ''}`} onClick={() => toggleTableTab('recommendation-document')}>
              {t('recommendation_document')}
            </div>
          )}
          <div className={`il-box-tab-item ${tab === 'policies' ? 'active' : ''}`} onClick={() => toggleTableTab('policies')}>
            {t('policies')}
          </div>
          <div className={`il-box-tab-item ${tab === 'reassignment' ? 'active' : ''}`} onClick={() => toggleTableTab('reassignment')}>
            {t('reassignment')}
          </div>
        </div>

        <div>
          {tab === 'tasks' && <Tasks opData={{ id: data.id, title: data.title, code: data.code, stage_name: data.stage_type, stage_color: data.stage_color }} />}
          {tab === 'health' && <HealthHistory setTableVers={setTableVers} />}
          {tab === 'interested' && <InterestedProducts />}
          {tab === 'interactions' && <OpportunityInteraction />}
          {tab === 'notes' && data.entity_id && <Notes entityId={data.entity_id} />}
          {tab === 'opp-type' && <OpportunityTypes customerId={data.customer_id} />}
          {tab === 'quotation' && data.id && (
            <Quotation
              customerId={data.customer_id ? data.customer_id : null}
              quotationRequestId={data.quotation_id ? data.quotation_id.toString() : ''}
              leadId={data.id.toString() || ''}
              afterCreateRequest={() => fetchData()}
              stageId={data.stage_id}
            />
          )}
          {tab === 'policies' && <Policies leadId={opportunityId} customerId={data.customer_id?.toString() || ''} />}
          {tab === 'recommendation-document' && data.quotation_id && <RecommendationDocumentation quotationId={data.quotation_id ? data.quotation_id.toString() : ''} />}
          {tab === 'reassignment' && <ReassignmentList />}
        </div>
      </div>

      {data.entity_id && <FlagCreate key={createFormKey} isOpen={flagModel} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} entityId={data.entity_id.toString()} />}

      {data.entity_id && (
        <FlagDelete isOpen={singleFlagDeleteModel} entityId={data.entity_id.toString()} onCancel={() => setSingleFlagDeleteModel(false)} afterDelete={handleAfterDelete} data={dataSingleFlag} />
      )}
      {currentEditId && <SalesManagementsEdit editId={currentEditId} isOpen={!!currentEditId} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      {/* <OpportunityEdit editId={currentEditId} isOpen={isOpen} onCancel={() => setIsOpen(false)} afterUpdate={handleAfterUpdate} /> */}
    </>
  );
};
