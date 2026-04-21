import { Button, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import RiskTypeList from './RiskTypeList';
import { deleteRiskInfo, getAllOpportunityTypeConfig, getAllOpportunityTypeFormAttributes } from '../../../../api-service';
import { IElements } from '../../../../model';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import AddInfo from './AddInfo';
import { toaster } from '@/helpers/services/toaster';
import EditRiskInfo from './EditRiskInfo';
import ConfigureForm from './ConfigureForm';

const RiskTypes = ({ selectedTypeId, leadId, customerId }: { selectedTypeId: string; leadId: any; customerId: string }) => {
  const t = useTrans('label.sales_managements,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [currentEditFormId, setCurrentEditFormId] = useState('');
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const [loading, setLoading] = useState(true);
  const [tableElements, setTableElements] = useState<IElements[]>([]);
  const [isConfigured, setIsConfigured] = useState(false);

  const reloadTable = () => {
    setTableVers((prev) => prev + 1);
  };

  useEffect(() => {
    if (selectedTypeId) {
      fetchData();
    }
  }, [selectedTypeId]);

  const fetchData = async () => {
    try {
      const responseData = await getAllOpportunityTypeConfig(selectedTypeId, 'ONBOARDING');
      if (responseData?.is_success) {
        const response = await getAllOpportunityTypeFormAttributes(responseData.result.form_id || '');
        if (responseData.result?.config_id) {
          setIsConfigured(true);
        }
        setTableElements(response?.result || []);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error fetching form attributes:', error);
    }
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteRiskInfo(deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
    }

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      reloadTable();
    }
  };

  const handleOpenConfig = () => {
    setIsCreateOpen(false);
    setTimeout(() => {
      setIsConfigOpen(true);
    }, 100);
  };

  return (
    <div className="mt-2">
      {loading ? (
        <Skeleton height="300px" width="100%" />
      ) : (
        <>
          <div className="align-self-center d-flex justify-content-end">
            <div className="d-flex align-items-center gap-2">
              {/* <Button
                color="light"
                className="d-flex align-items-center gap-1"
                onClick={() => {
                  router.push(`/crm/a/sales-management/${leadId}/${selectedTypeId}/upload-info`);
                }}
              >
                <Flexicon icon="upload-01" variant="line" size={18} />
                <span className="d-none d-sm-inline">{t('upload_info')}</span>
              </Button> */}
              <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
                <Flexicon icon="plus-circle" size={18} />
                <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('info') })}</span>
              </Button>
            </div>
          </div>
          {isConfigured ? (
            <RiskTypeList
              riskTypeId={selectedTypeId}
              tableElements={tableElements}
              tableVers={tableVers}
              leadId={leadId}
              onEdit={(submissionId) => setCurrentEditFormId(submissionId)}
              handleOnDelete={handleOnDelete}
            />
          ) : (
            <div className="panel text-center">
              <div className="text-muted fs-15 fw-semibold my-2">{t('no_form_config')}</div>
              <div className="text-primary clickable-text fs-14" onClick={() => setIsConfigOpen(true)}>
                {t('configure_it_now')}
              </div>
            </div>
          )}
        </>
      )}

      {isCreateOpen && (
        <AddInfo
          isOpen={isCreateOpen}
          onCancel={() => {
            setIsCreateOpen(false);
            reloadTable();
          }}
          afterSave={() => {
            setIsCreateOpen(false);
            reloadTable();
          }}
          opportunityId={leadId}
          typeId={selectedTypeId}
          customerId={customerId?.toString() || ''}
          handleOpenConfig={handleOpenConfig}
        />
      )}

      {currentEditFormId !== '' && (
        <EditRiskInfo
          isOpen={currentEditFormId !== ''}
          onCancel={() => {
            setCurrentEditFormId('');
            reloadTable();
          }}
          afterSave={() => {
            setCurrentEditFormId('');
            reloadTable();
          }}
          riskInfoId={currentEditFormId}
        />
      )}
      {isConfigOpen && (
        <ConfigureForm
          isOpen={isConfigOpen}
          onCancel={() => setIsConfigOpen(false)}
          afterSave={() => {
            setIsConfigOpen(false), fetchData();
          }}
          viewId={selectedTypeId}
        />
      )}
    </div>
  );
};

export default RiskTypes;
