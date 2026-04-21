import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState, useEffect } from 'react';

interface EditMappingProps {
  isOpen: boolean;
  rowData: any;
  fields: string[];
  flexFields: { name: string; dataType?: string }[];
  onSave: (row: any) => void;
  onCancel: () => void;
}

function EditMapping({ isOpen, rowData, fields, flexFields, onSave, onCancel }: EditMappingProps) {
  const t = useTrans('label.invoice,otr.common');
  const [formData, setFormData] = useState<any>({});
  const [flexData, setFlexData] = useState<any>({});
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  useEffect(() => {
    setFormData(() => {
      const data: any = {};
      fields.forEach((f) => {
        data[f.toLowerCase().replace(/\s+/g, '_')] = rowData?.[f.toLowerCase().replace(/\s+/g, '_')] || '';
      });
      return data;
    });
    setFlexData(() => {
      const data: any = {};
      flexFields.forEach((f) => {
        data[f.name.toLowerCase().replace(/\s+/g, '_')] = rowData?.flex_fields?.[f.name.toLowerCase().replace(/\s+/g, '_')] || '';
      });
      return data;
    });
  }, [rowData, fields, flexFields]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [name]: value }));
  };
  const onFlexChange = (name: string, value: any) => {
    setFlexData((prev: any) => ({ ...prev, [name]: value }));
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
    <Modal isOpen={isOpen} size="lg" onBackdrop={onCancel}>
      <ModalHeader title={t('edit_mapping_details')} onClose={onCancel} />
      <form onSubmit={handleSubmit} id={`${form.field.store}`}>
        <ModalBody>
          <div className="row">
            {fields.map((f) => (
              <div className="col-12 col-md-6 mb-3" key={f}>
                <Input
                  isRequired
                  label={f}
                  value={formData[f.toLowerCase().replace(/\s+/g, '_')] || ''}
                  onChange={(e) => onFormChange(f.toLowerCase().replace(/\s+/g, '_'), e.target.value)}
                  className="form-control"
                  name={f.toLowerCase().replace(/\s+/g, '_')}
                />
              </div>
            ))}
            {flexFields.map((f) => (
              <div className="col-12 col-md-6 mb-3" key={f.name}>
                <Label label={f.name} isRequired />
                <Input
                  value={flexData[f.name.toLowerCase().replace(/\s+/g, '_')] || ''}
                  onChange={(e) => onFlexChange(f.name.toLowerCase().replace(/\s+/g, '_'), e.target.value)}
                  className="form-control"
                  name={f.name.toLowerCase().replace(/\s+/g, '_')}
                />
              </div>
            ))}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={onCancel} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EditMapping;
