'use client';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { initNode } from '../model';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { EditNode } from './EditNode';
import GoBack from '@/components/others/page-related/GoBack';

function ViewNode() {
  const t = useTrans('label.org_nodes,otr.common');
  const router = useRouter();
  //   const searchParams = useSearchParams();
  const [skeleton, _setSkeleton] = useState(false);
  const [data, _setData] = useState(initNode);
  //   const [tab, setTab] = useState('quotations');
  const params = useParams();
  const nodeId = params.nodeId?.toString() || '';
  const [currentEditId, setCurrentEditId] = useState('');

  //   useEffect(() => {
  //     const tab = searchParams.get('t') || 'quotations';
  //     toggleTableTab(tab);
  //   }, [searchParams]);

  //   const toggleTableTab = (activeTab: string) => {
  //     setTab(activeTab);
  //     router.push(`/crm/a/quotations/${quotationId}?t=${activeTab}`);
  //   };

  // useEffect(() => {
  //   const fetchData = async () => {
  //     const responseData = await getOnePartner(partnerId);
  //     if (responseData?.is_success) {
  //       setData(responseData.result);
  //       setSkeleton(false);
  //     }
  //   };

  //   if (partnerId) {
  //     setSkeleton(true);
  //     fetchData();
  //   }
  // }, [partnerId]);
  const handleOnDelete = async (deleteId: string, setLoader: Function) => {
    console.log('Delete ID:', deleteId);
    console.log('setLoader', setLoader);

    // if (!deleteId) {
    //   console.error('Error: Node ID is undefined');
    //   return;
    // }

    // setLoader(true);
    // const responseData = await deleteHierarchies(deleteId);
    // setLoader(false);

    // if (responseData.is_success) {
    //   toaster.success(tBe(responseData.message));
    //   afterNodeCreation();
    // }
  };

  const onClose = () => {};

  return (
    <>
      <GoBack goTo={() => router.push('/a/nodes')} title={t('organizational_node')} />
      <div className="bg-white custom-card overflow-hidden p-3 px-4 rounded-3">
        <div className="row">
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('level_name')} value={data?.level_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('code')} value={data?.code || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('node_name')} value={data?.node_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('branch_name_code')} value={data?.branch_name_code || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('physical_address')} value={data?.physical_address || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('primary_email')} value={data?.primary_email || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('contact_number')} value={data?.contact_number || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('staff')} value={data?.staff || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-3">
            <DeleteConfirmPop
              position="right"
              trigger={
                <Button color="primary" className="d-flex align-items-center gap-1">
                  <Flexicon icon="minus-circle" size={18} />
                  <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('nodes') })}</span>
                </Button>
              }
              deleteId={''}
              {...{ handleOnDelete, onClose }}
            />
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-end gap-2  py-2">
        <Button text={t('edit')} onClick={() => setCurrentEditId(nodeId)} />
        {/* <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} /> */}
      </div>
      {!!currentEditId && <EditNode isOpen={!!currentEditId} onCancel={() => setCurrentEditId('')} afterEdit={() => setCurrentEditId('')} editId={currentEditId} />}
    </>
  );
}

export default ViewNode;
