'use client';

import { useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { form } from '@/constans/Form';
import { CHART_TYPES, fetchAllReportFields } from '../../service';
import { createReportChart } from '../../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

type ICreateChartModels = {
  isOpen: boolean;
  onClose: () => void;
  afterSave: () => void;
  reportId: string;
};

function CreateChart({ isOpen, onClose, afterSave, reportId }: ICreateChartModels) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ x_axis: [], y_axis: [], title: '', type: '', is_multi_x: false, is_multi_y: false });
  const t = useTrans('label.custom_report,otr.common');

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  const onSubmit = async (e: any) => {
    e.preventDefault();
    clearError(form.chart.store);
    setIsFormProcessing(true);
    try {
      const responseData = await createReportChart({ ...formData, report_id: reportId, json: { x_axis: formData.x_axis, y_axis: formData.y_axis } });
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.chart.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error: any) {
      console.error(error.message || 'Error saving chart configuration');
    }
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={onClose} size="lg">
      <ModalHeader title={t('create_chart')} onClose={onClose} />
      <form onSubmit={onSubmit} id={`${form.chart.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('name')} />
              <Input value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" isRequired />
            </div>

            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('chart_type')} isRequired />
              <Select
                options={CHART_TYPES}
                option={{ label: 'id', value: 'value' }}
                onChange={(value) => {
                  onFormChange('type', value);
                  const selectedType = CHART_TYPES.find((c) => c.value === value);
                  onFormChange('is_multi_x', selectedType?.axes.x === 'multiple');
                  onFormChange('is_multi_y', selectedType?.axes.y === 'multiple');
                }}
                className="form-control error-type"
                //defaultValue={CHART_TYPES.find((c) => c.value === formData.type)}
              />
            </div>

            {formData.type !== '' && (
              <div className="col-6 mb-3 custom-select">
                <Label label={t('x_axis')} />
                <AsyncSelect
                  key={`x-axis-${formData.type}`}
                  loadOptions={(searchValue, currentPage) => fetchAllReportFields(searchValue, currentPage, reportId)}
                  option={{ label: 'label', value: 'code' }}
                  multiple={formData.is_multi_x}
                  onChange={(_value, data) => {
                    onFormChange('x_axis', formData.is_multi_x ? data : [data]);
                  }}
                  allowClear
                />
              </div>
            )}

            {formData.type !== '' && (
              <div className="col-6 mb-3 custom-select">
                <Label label={t('y_axis')} />
                <AsyncSelect
                  key={`y-axis-${formData.type}`}
                  loadOptions={(searchValue, currentPage) => fetchAllReportFields(searchValue, currentPage, reportId)}
                  option={{ label: 'label', value: 'code' }}
                  multiple={formData.is_multi_y}
                  onChange={(_value, data) => {
                    onFormChange('y_axis', formData.is_multi_y ? data : [data]);
                  }}
                  allowClear
                />
              </div>
            )}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('save')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onClose()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateChart;
