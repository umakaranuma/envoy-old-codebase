import { initElementFormData } from '../model';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import 'react-phone-input-2/lib/style.css';
import { Select } from '@apptimus-ui/select';
import { createElement } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fileUploader } from '@/constans/storageService';
import FilePreviewer from './Elements/FilePreviewer';

function ElementCreate({
  isOpen,
  templateId,
  selectedElementCode,
  selectedElementCategory,
  afterSave,
  selectedElementId,
  onCancel,
  activeStepId,
  selectedPanelId,
  setElements,
  groupElement,
}: {
  isOpen: boolean;
  templateId: string;
  selectedElementCode: string;
  selectedElementCategory: string;
  onCancel: () => void;
  afterSave: () => void;
  selectedElementId: number;
  selectedPanelId: number | null;
  activeStepId: number | null;
  setElements: React.Dispatch<React.SetStateAction<any[]>>;
  groupElement: any;
}) {
  const t = useTrans('label.template,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initElementFormData);
  const [options, setOptions] = useState(['']);
  const [isUploading, setIsUploading] = useState(false);
  const [resource, setResource] = useState<File | null>(null);

  const columnSizeOptions = [
    { id: 12, columnSize: '100%' },
    { id: 6, columnSize: '50%' },
    { id: 4, columnSize: '33%' },
    { id: 3, columnSize: '25%' },
  ];

  // const fileType = [
  //   { id: 'All', type: 'All' },
  //   { id: 'Image', type: 'Image' },
  //   { id: 'Video', type: 'Video' },
  //   { id: 'PDF', type: 'PDF' },
  // ];

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const handleAddOption = () => {
    setOptions([...options, '']);
  };

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
    onFormChange(
      'options',
      newOptions.filter((opt) => opt.trim() !== ''),
    );
  };

  const handleRemoveOption = (index: number) => {
    if (options.length > 1) {
      const newOptions = options.filter((_, i) => i !== index);
      setOptions(newOptions);
      onFormChange(
        'options',
        newOptions.filter((opt) => opt.trim() !== ''),
      );
    }
  };

  const handleFileUpload = async () => {
    if (!resource) {
      return null;
    }

    setIsUploading(true);
    try {
      const uploadFormData = new FormData();
      uploadFormData.append('file', resource);
      const key = await fileUploader(uploadFormData, 'envoy-template-form');
      return key;
    } catch (error) {
      console.error('Error uploading file:', error);
      toaster.error('file_upload_failed');
      throw error;
    } finally {
      setIsUploading(false);
    }
  };
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.customres_crud.update);
    setIsFormProcessing(true);
    try {
      if (selectedElementCode === 'IMAGE_VIEWER' || selectedElementCode === 'VIDEO_VIEWER' || selectedElementCode === 'PDF_VIEWER' || (selectedElementCode === 'BANNER' && resource)) {
        const key = await handleFileUpload();
        if (key) {
          const finalValue = process.env.S3CDN + '/' + key;
          onFormChange('value', finalValue);
          const updatedFormData = { ...formData, value: finalValue };
          const responseData = await createElement(updatedFormData, templateId);
          handleResponse(responseData);
        } else {
          toaster.error(tBe('file_upload_failed'));
        }
      } else {
        const responseData = await createElement(formData, templateId);
        const isGrpCategorty = responseData.result.category === 'input_group';

        if (isGrpCategorty) {
          setElements((prev: any) => [...prev, responseData.result]);
          const baseFormData = {
            ...formData,
            parent_id: responseData.result.id,
          };

          const matchingGroups = Array.isArray(groupElement) ? groupElement.filter((group: any) => group.group_id === selectedElementId) : [];

          for (const group of matchingGroups) {
            const updatedFormData = {
              ...baseFormData,
              label: group.title,
              code: group.code,
            };
            const groupResponse = await createElement(updatedFormData, templateId);

            // Add each group result to elements state
            if (groupResponse.is_success) {
              setElements((prev: any) => [...prev, groupResponse.result]);
            }
          }

          setFormData(initElementFormData);
          setOptions(['']);
          setResource(null);
          afterSave();
          return;
        }

        handleResponse(responseData);
      }
    } catch (error) {
      console.error('An error occurred:', error);
      toaster.error(tBe('Something went wrong'));
    } finally {
      setIsFormProcessing(false);
    }
  }

  function handleResponse(responseData: any) {
    if (responseData.status_code === 417) {
      printError(responseData.result, form.customres_crud.update, tBe);
    }

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      setElements((prev: any) => [...prev, responseData.result]);
      setFormData(initElementFormData);
      setOptions(['']);
      setResource(null);
      afterSave();
    }
  }

  useEffect(() => {
    if (isOpen) {
      setFormData({
        ...initElementFormData,
        step_id: activeStepId !== null ? activeStepId.toString() : '',
        panel_id: selectedPanelId !== null ? selectedPanelId.toString() : '',
        element_id: selectedElementId.toString(),
        code: selectedElementCode,
        category: selectedElementCategory,
      });
      setOptions(['']);
      setResource(null);
      onFormChange('column_size', 12);
    }
  }, [isOpen, selectedPanelId, activeStepId, selectedElementId]);

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('add_element')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.contact_crud.store}`}>
        <ModalBody>
          <div className="row">
            {selectedElementCode === 'HEADING' && (
              <div className="col-6 mb-3">
                <Input
                  type="text"
                  label="Heading"
                  isRequired
                  id="text"
                  value={formData.value}
                  rows={4}
                  onChange={(e) => {
                    onFormChange('value', e.target.value);
                  }}
                />
              </div>
            )}

            {selectedElementCode !== 'BANNER' &&
              selectedElementCode !== 'LINE_BREAK' &&
              selectedElementCode !== 'PARAGRAPH' &&
              selectedElementCode !== 'HEADING' &&
              selectedElementCode !== 'DIVIDER' && (
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('label')} value={formData.label} onChange={(e) => onFormChange('label', e.target.value)} className="form-control error-name" name="name" />
                </div>
              )}

            {selectedElementCode !== 'BANNER' && (
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="select-from-existing" label={t('column_size')} />
                <Select
                  onChange={(_, data) => {
                    onFormChange('column_size', data.id);
                    onFormChange('column_size_label', data.columnSize);
                  }}
                  options={columnSizeOptions}
                  option={{
                    label: 'columnSize',
                    value: 'id',
                  }}
                  defaultValue={{ columnSize: formData.column_size_label, id: formData.column_size }}
                />
              </div>
            )}
            {/* 
            {selectedElementCode === 'SUBMISSION_PICKER' && (
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="select-from-existing" label={t('file_type')} />
                <Select
                  onChange={(value) => {
                    onFormChange('value', value);
                  }}
                  options={fileType}
                  option={{
                    label: 'type',
                    value: 'id',
                  }}
                  defaultValue={{ type: formData.value, id: formData.value }}
                />
              </div>
            )} */}

            {/* {selectedElementCode === 'OPTION_SCALE' && (
              <div className="col-12 col-md-6 mb-3">
                <Input label={t('count')} value={formData.value} onChange={(e) => onFormChange('value', e.target.value)} type="number" />
              </div>
            )} */}

            {['DROPDOWN', 'MULTI_SELECT', 'RADIO_BOX', 'MULTI_CHOICE', 'RANKING'].includes(selectedElementCode) && (
              <div className="col-12 mb-3">
                <Label label={t('options')} />
                {options.map((option, index) => (
                  <div key={index} className="d-flex align-items-center gap-2 mb-2">
                    <Input value={option} onChange={(e) => handleOptionChange(index, e.target.value)} className="form-control" placeholder={`${t('option')} ${index + 1}`} />
                    {options.length > 1 && (
                      <Button color="danger" onClick={() => handleRemoveOption(index)} className="p-1">
                        <Flexicon icon="trash-03" variant="line" size={18} />
                      </Button>
                    )}
                  </div>
                ))}
                <div onClick={handleAddOption} className="pointer text-primary mt-3">
                  <Flexicon icon="plus" variant="line" /> {t('add_option')}
                </div>
              </div>
            )}

            {['IMAGE_VIEWER', 'BANNER'].includes(selectedElementCode) && (
              <div className="col-12 mb-3">
                <Label htmlFor="media" label={t('choose_file')} isRequired />
                <FilePreviewer
                  fileType="Image"
                  onChange={(selectedFiles) => {
                    setResource(selectedFiles);
                  }}
                />
                {/* {isUploading && (
                                    <div className="text-center mt-2">
                                        <div className="spinner-border text-primary" role="status">
                                            <span className="visually-hidden">Uploading...</span>
                                        </div>
                                        <p className="text-muted mt-2">Uploading media...</p>
                                    </div>
                                )} */}
              </div>
            )}
            {selectedElementCode === 'VIDEO_VIEWER' && (
              <div className="col-12 mb-3">
                <Label htmlFor="media" label={t('choose_file')} isRequired />
                <FilePreviewer
                  fileType="Video"
                  onChange={(selectedFiles) => {
                    setResource(selectedFiles);
                  }}
                />
                {/* {isUploading && (
                                    <div className="text-center mt-2">
                                        <div className="spinner-border text-primary" role="status">
                                            <span className="visually-hidden">Uploading...</span>
                                        </div>
                                        <p className="text-muted mt-2">Uploading media...</p>
                                    </div>
                                )} */}
              </div>
            )}

            {selectedElementCode === 'PDF_VIEWER' && (
              <div className="col-12 mb-3">
                <Label htmlFor="media" label={t('choose_file')} isRequired />
                <FilePreviewer
                  fileType="PDF"
                  onChange={(selectedFiles) => {
                    setResource(selectedFiles);
                  }}
                />
                {/* {isUploading && (
                                    <div className="text-center mt-2">
                                        <div className="spinner-border text-primary" role="status">
                                            <span className="visually-hidden">Uploading...</span>
                                        </div>
                                        <p className="text-muted mt-2">Uploading media...</p>
                                    </div>
                                )} */}
              </div>
            )}
            {selectedElementCode === 'PARAGRAPH' && (
              <div className="col-12 mb-3">
                <Input
                  type="textarea"
                  label="Paragraph"
                  id="text-area"
                  value={formData.value}
                  rows={4}
                  onChange={(e) => {
                    onFormChange('value', e.target.value);
                  }}
                />
              </div>
            )}

            {selectedElementCode !== 'BANNER' &&
              selectedElementCode !== 'LINE_BREAK' &&
              selectedElementCode !== 'PARAGRAPH' &&
              selectedElementCode !== 'HEADING' &&
              selectedElementCode !== 'PDF_VIEWER' &&
              selectedElementCode !== 'IMAGE_VIEWER' &&
              selectedElementCode !== 'BANNER' &&
              selectedElementCode !== 'VIDEO_VIEWER' &&
              selectedElementCode !== 'DIVIDER' && (
                <div className="mt-2 d-flex align-items-center gap-2">
                  <input type="checkbox" id="isRequiredCheckbox" checked={formData.is_required} onChange={(e) => onFormChange('is_required', e.target.checked)} />
                  <label htmlFor="isRequiredCheckbox" className="fs-14 cursor-pointer">
                    {t('is_required')}
                  </label>
                </div>
              )}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing || isUploading} disabled={isFormProcessing || isUploading} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ElementCreate;
