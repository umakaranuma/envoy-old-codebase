import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { fetchAllReportTypes } from '../service';
import { Editor } from '@monaco-editor/react';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getOneReport, updateReport } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { sqlToJson } from '../sqlToJson';
import { InputSkeleton } from '@/components/others/InputSkeleton';

function EditReport({ isOpen, onCancel, afterSave, editId }: { isOpen: boolean; onCancel: () => void; afterSave: () => void; editId: string }) {
  const t = useTrans('label.custom_report,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState({ title: '', description: '', json: '', sql: '', type_id: '', type_name: '' });
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneReport(editId);
      if (responseData?.is_success) {
        setFormData({
          title: responseData.result.title,
          description: responseData.result.description,
          json: responseData.result.json,
          sql: responseData.result.query,
          type_id: responseData.result.type_id_id,
          type_name: responseData.result.type_name,
        });
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  async function onSubmit() {
    clearError(form.custom_report.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateReport({ ...formData, json: formData.json ? JSON.parse(formData.json) : '' }, editId);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.custom_report.update, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const generateJsonFromSql = (sql: string) => {
    let newJson;
    try {
      const generated = sqlToJson(sql);
      newJson = JSON.stringify(generated, null, 2);
    } catch (error: any) {
      const errorMessage = error.message === 'SQL query must start with SELECT' ? 'SQL query must start with a SELECT statement' : 'Invalid SQL query';
      newJson = JSON.stringify({ error: errorMessage }, null, 2);
    }
    if (formData.json !== newJson) {
      onFormChange('json', newJson);
    }
  };

  const canAddSkipColumn = React.useMemo(() => {
    if (!formData.json) return false;
    try {
      const json = JSON.parse(formData.json);
      return typeof json === 'object' && json !== null && Array.isArray(json.fields);
    } catch (e) {
      return false;
    }
  }, [formData.json]);

  const handleAddSkipColumn = () => {
    let json;
    try {
      json = JSON.parse(formData.json || '{}');
    } catch (e) {
      console.error('Invalid JSON, cannot add skip_columns:', e);
      return;
    }

    if (!json.skip_columns || !Array.isArray(json.skip_columns)) {
      json.skip_columns = [{ code: 'column_name', title: 'Column Title' }];
    } else {
      json.skip_columns.push({ code: 'column_name', title: 'Column Title' });
    }
    console.log(JSON.stringify(json, null, 2));
    onFormChange('json', JSON.stringify(json, null, 2));
  };

  return (
    <Modal isOpen={isOpen} size="xl" scrollable>
      <ModalHeader title={t('edit_report')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.custom_report.update}`}>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('name')} isRequired />
            {skeleton ? <InputSkeleton /> : <Input value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />}
          </div>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="form" label={t('report_type')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('type_id', data.id), onFormChange('type_name', data.name);
                }}
                className="form-control error-type_id"
                loadOptions={(searchStr: string, page: number) => fetchAllReportTypes(searchStr, page)}
                option={{
                  value: 'id',
                  label: 'name',
                }}
                defaultValue={{ name: formData.type_name, id: formData.type_id }}
                allowClear
              />
            )}
          </div>
          <div className="col-12 mb-3">
            <Label label={t('description')} />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input
                type="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
              />
            )}
          </div>
          <div className="col-12 mb-3">
            <div className="row g-4">
              <div className="col-12 col-lg-6">
                <Label label={t('sql_query')} isRequired />
                {skeleton ? (
                  <Skeleton width="100%" height="50px" />
                ) : (
                  <span className="error-sql form-control mt-2">
                    <Editor
                      height="60vh"
                      language="sql"
                      value={formData.sql}
                      onChange={(value) => {
                        onFormChange('sql', value);
                        setTimeout(() => {
                          generateJsonFromSql(value ?? '');
                        }, 500);
                      }}
                      options={{
                        fontFamily: 'Lexend Deca',
                        fontSize: 14,
                        placeholder: t('enter_your_sql_select_query_here'),
                      }}
                    />
                  </span>
                )}
              </div>
              <div className="col-12 col-lg-6">
                {formData.json && (
                  <>
                    <div className="d-flex justify-content-between align-items-center">
                      <Label label={t('json')} />
                      <Button size="sm" text="add skip column" onClick={handleAddSkipColumn} disabled={!canAddSkipColumn} />
                    </div>
                    <span className="form-control mt-2">
                      <Editor
                        height="60vh"
                        language="json"
                        value={formData.json}
                        onChange={(value) => onFormChange('json', value ?? '')}
                        options={{
                          fontFamily: 'Lexend Deca',
                          fontSize: 14,
                          minimap: { enabled: false },
                          formatOnPaste: true,
                          formatOnType: true,
                          theme: 'vs-light',
                          scrollbar: { verticalScrollbarSize: 8 },
                        }}
                        //className="mt-2 form-control"
                      />
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EditReport;
