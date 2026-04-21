import ElementType from '@/components/others/common/forms/ElementType';
import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState, useEffect } from 'react';
import 'react-phone-input-2/lib/style.css';

interface Field {
  id: number;
  label: string;
  element_id?: number;
  element_code: string;
  element_category?: string;
  step_id?: null;
  panel_id?: number;
  order_number?: number;
  column_size?: number;
  is_required?: number;
  options?: any[];
  value?: null;
  isRequired?: boolean;
}

interface EditMappingProps {
  isOpen: boolean;
  rowData: any;
  fields: Field[];
  onSave: (row: any) => void;
  onCancel: () => void;
}

function EditMapping({ isOpen, rowData, fields, onSave, onCancel }: EditMappingProps) {
  const t = useTrans('label.sales_managements,otr.common');
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [flexData, setFlexData] = useState<Record<string, any>>({});
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  useEffect(() => {
    // Initialize form data with field values from rowData
    const initialFormData: Record<string, any> = {};
    fields.forEach((field) => {
      initialFormData[field.id] = rowData?.[field.id] || '';
    });
    setFormData(initialFormData);

    // Initialize flex field data
    const initialFlexData: Record<string, any> = {};
    setFlexData(initialFlexData);
  }, [rowData, fields]);

  const handleFormChange = (fieldId: number, value: any) => {
    setFormData((prev) => ({ ...prev, [fieldId]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsFormProcessing(true);

    const updatedRow = {
      ...rowData,
      ...formData,
      flex_fields: { ...flexData },
    };

    onSave(updatedRow);
    setIsFormProcessing(false);
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={onCancel} size="xl">
      <ModalHeader title={t('edit_mapping_details')} onClose={onCancel} />
      <form onSubmit={handleSubmit} id={`${form.field.store}`}>
        <ModalBody>
          <div className="row">
            {fields.map((field) => (
              <div key={field.id} className={`${field.column_size} mb-3`}>
                <ElementType
                  type={field.element_code}
                  onChange={(e: any) => {
                    const value = e && e.target ? e.target.value : (e?.value ?? e);
                    handleFormChange(field.id, value);
                  }}
                  options={field.options}
                  isRequired={field.is_required !== 0}
                  label={field.label}
                  value={formData[field.id] || ''}
                  elementId={field.id.toString()}
                />
              </div>
            ))}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={onCancel} />
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EditMapping;
