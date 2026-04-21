import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { AsyncSelect } from '@apptimus-ui/select';
import React, { useState } from 'react';
import { FlexField } from '@/helpers/services/excelUploadCommonService';

interface CreateFieldProps {
  isOpen: boolean;
  onCancel: () => void;
  onAdd: (field: FlexField) => void;
  excelFields: { label: string; value: string }[];
}

function CreateField({ isOpen, onCancel, onAdd, excelFields }: CreateFieldProps) {
  const t = useTrans('label.invoice,otr.common');
  const [formData, setFormData] = useState<FlexField>({
    name: '',
    dataType: '',
    dataValue: '',
  });
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
    // Clear error when field is updated
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name) newErrors.name = t('field_required');
    if (!formData.dataType) newErrors.dataType = t('field_required');
    if (!formData.dataValue) newErrors.dataValue = t('field_required');
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsFormProcessing(true);
    try {
      onAdd(formData);
      onCancel();
    } catch (error) {
      console.error('Error adding field:', error);
    } finally {
      setIsFormProcessing(false);
    }
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('create_new_entity', { entity: t('field') })} onClose={() => onCancel()} />
      <form onSubmit={handleSubmit} id={`${form.field.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('field_name')}
                value={formData.name}
                onChange={(e) => onFormChange('name', e.target.value)}
                className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                name="name"
              />
              {errors.name && <div className="invalid-feedback">{errors.name}</div>}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('data_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('dataType', value)}
                className={`form-control ${errors.dataType ? 'is-invalid' : ''}`}
                option={{ label: 'label', value: 'value' }}
                isSearchable={true}
                loadOptions={() =>
                  Promise.resolve([
                    { label: 'Text', value: 'text' },
                    { label: 'Number', value: 'number' },
                    { label: 'Date', value: 'date' },
                    { label: 'Boolean', value: 'boolean' },
                    { label: 'Currency', value: 'currency' },
                    { label: 'Percentage', value: 'percentage' },
                  ])
                }
              />
              {errors.dataType && <div className="invalid-feedback">{errors.dataType}</div>}
            </div>
            <div className="col-12 mb-3 custom-select">
              <Label label={t('data_value')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('dataValue', value)}
                className={`form-control ${errors.dataValue ? 'is-invalid' : ''}`}
                option={{ label: 'label', value: 'value' }}
                isSearchable={true}
                loadOptions={() => Promise.resolve(excelFields)}
              />
              {errors.dataValue && <div className="invalid-feedback">{errors.dataValue}</div>}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateField;
