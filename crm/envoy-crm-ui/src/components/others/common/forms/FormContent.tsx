import React, { FormEvent, useEffect, useState } from 'react';
import FormStepper from '@/components/others/common/forms/FormStepper';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import ElementType from '@/components/others/common/forms/ElementType';
import { IElements, IForm } from './models';
interface FormContentProps {
  templateData: IForm;
  formData: IElements[];
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  groupElements: any[];
  isFormProcessing: boolean;
  onCancel: Function;
  currentStep: any;
  setCurrentStep: (step: any) => void;
  onFormChange?: (updatedData: IElements[]) => void;
  setFormData: any;
}

const FormContent = ({ templateData, formData, onSubmit, groupElements, isFormProcessing, onCancel, currentStep, setCurrentStep, onFormChange: onFormDataChange, setFormData }: FormContentProps) => {
  const [currentTabIndex, setCurrentTabIndex] = useState(0);
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (formData.length > 0) setLoading(false);
  }, [formData.length]);

  const handleValidation = () => {
    clearError(form.product.store);
    // Initialize error as an empty object with the proper type
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    // Email validation regex pattern
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (templateData.template?.type === 'multi_step_form') {
      const currentStep = templateData.steps[currentTabIndex];
      const currentStepElements = formData.filter((element: any) => element.step_id === currentStep.id);

      currentStepElements.forEach((element: any) => {
        // Check for required fields
        if (element.is_required && !element.value) {
          error[element.id] = [
            {
              error_type: 'required',
              tokens: { _attribute: element.id.toString() },
            },
          ];
        }

        // Additional validation for email fields
        if (element.code === 'EMAIL_INPUT' && element.value && !emailPattern.test(element.value)) {
          error[element.id] = [
            {
              error_type: 'invalid_email',
              tokens: { _attribute: element.id.toString() },
            },
          ];
        }
      });
    } else {
      formData.forEach((element: any) => {
        if (element.is_required && !element.value) {
          error[element.id] = [
            {
              error_type: 'required',
              tokens: { _attribute: element.id.toString() },
            },
          ];
        }

        if (element.code === 'EMAIL_INPUT' && element.value && !emailPattern.test(element.value)) {
          error[element.id] = [
            {
              error_type: 'invalid_email',
              tokens: { _attribute: element.id.toString() },
            },
          ];
        }
      });
    }

    if (Object.keys(error).length > 0) {
      printError(error, form.product.store, tBe);
      return false;
    } else {
      if (templateData.template?.type === 'multi_step_form' && currentTabIndex < templateData.steps.length - 1) {
        const nextIndex = currentTabIndex + 1;
        const nextStep = templateData.steps[nextIndex];
        setCurrentStep(nextStep);
        setCurrentTabIndex(nextIndex);
      }
      return true;
    }
  };
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const isValid = handleValidation();
    if (isValid) {
      onSubmit(e);
    }
  };

  function renderElement(element: IElements, allElements: IElements[], groupElements: any[] | undefined, onFormChange: (elementId: number, value: any) => void, isGroupChild: boolean = false) {
    const children = allElements.filter((child) => child.parent_id === element.id);
    const colClass = isGroupChild ? 'col-12' : `col-12 col-md-${element.column_size || 6}`;

    return (
      <div key={element.id} className={`${colClass} mb-3`}>
        <ElementType
          type={element.code}
          onChange={(value) => onFormChange(element.id, value)}
          options={element.options}
          isRequired={element.is_required !== 0}
          label={element.label}
          value={element.value}
          elementId={element.id.toString()}
        />
        {getGroupLabels(element, groupElements || []).length > 0 && <div className="group-labels">{getGroupLabels(element, groupElements || []).join(', ')}</div>}
        {children.length > 0 && <div className="group-children ps-3 mt-2 border-start">{children.map((child) => renderElement(child, allElements, groupElements, onFormChange, true))}</div>}
      </div>
    );
  }

  function getGroupLabels(element: IElements, groupElements: any[]): string[] {
    if (element.category === 'input_group') {
      const labels = (Array.isArray(groupElements) ? groupElements : []).filter((group: any) => group.group_id === element.id).map((group: any) => group.title);
      return labels;
    }
    return [];
  }

  const SkeletonCard = () => (
    <div className="card shadow-sm mb-4">
      <div className="card-body">
        <Skeleton width="100%" height="2rem" loading={false} />
        <div className="row mt-2">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="col-6 mt-3">
              <Skeleton width="100%" height="2.5rem" loading={false} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const onFormChange = (elementId: number, value: any) => {
    setFormData((prevFormData: any) => {
      const updatedData = prevFormData.map((item: any) => (item.id === elementId ? { ...item, value } : item));

      if (onFormDataChange) {
        onFormDataChange(updatedData);
      }

      return updatedData;
    });
  };

  return loading ? (
    <div>
      <div className="d-flex justify-content-center mb-3">
        <Skeleton width="50%" height="2rem" loading={false} />
      </div>
      <div className="d-flex justify-content-center gap-5 mb-3">
        <Skeleton height="50px" width="50px" className="rounded-pill" loading={false} />
        <Skeleton height="50px" width="50px" className="rounded-pill" loading={false} />
        <Skeleton height="50px" width="50px" className="rounded-pill" loading={false} />
        <Skeleton height="50px" width="50px" className="rounded-pill" loading={false} />
      </div>
      <SkeletonCard />
    </div>
  ) : (
    <form onSubmit={handleSubmit} id={`${form.product.store}`}>
      <div>
        {/* Display Steps if they exist */}
        {templateData.steps && templateData.steps.length > 0 && (
          <div className="mb-4">
            <FormStepper templateName={templateData.template.name} steps={templateData.steps} currentTabId={currentStep.id} />
          </div>
        )}

        {(!templateData?.steps || templateData?.steps?.length === 0) && <div className="my-3 fw-semibold text-center">{templateData?.template?.name}</div>}

        {/* Display Panels and their Elements */}
        {templateData.panels && templateData.panels.length > 0 && (
          <div>
            {templateData.panels.map((panel) => (
              <div
                key={panel.id}
                className={`card shadow-sm mb-4 ${templateData.template?.type === 'multi_step_form' ? `d-${currentStep.id && currentStep.id === panel.step_id ? 'block' : 'none'}` : 'd-block'}`}
              >
                <div className="card-body">
                  <h5 className="fs-14 fw-semibold mb-3">{panel.title || `Panel`}</h5>
                  <div className="row">
                    {formData
                      .filter((element) => element.panel_id === panel.id && element.parent_id === null)
                      .sort((a, b) => a.order_number - b.order_number)
                      .map((element) => renderElement(element, formData, groupElements, onFormChange, false))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Navigation buttons */}
        {templateData.template?.type === 'multi_step_form' ? (
          <div className="d-flex justify-content-end gap-2 mt-3">
            <Button
              color="light"
              className="d-flex align-items-center gap-1"
              disabled={currentTabIndex === 0}
              onClick={() => {
                if (currentTabIndex > 0) {
                  const prevIndex = currentTabIndex - 1;
                  const prevStep = templateData.steps[prevIndex];
                  setCurrentStep(prevStep);
                  setCurrentTabIndex(prevIndex);
                }
              }}
            >
              <Flexicon icon="chevron-left" variant="line" size={18} />
              <span className="d-none d-sm-inline">{t('previous')}</span>
            </Button>
            {currentTabIndex < templateData.steps.length - 1 && (
              <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => handleValidation()}>
                <span className="d-none d-sm-inline">{t('next')}</span>
                <Flexicon icon="chevron-right" variant="line" size={18} />
              </Button>
            )}
            {currentTabIndex === templateData.steps.length - 1 && <Button color="primary" type="submit" text={t('save')} isLoading={isFormProcessing} />}
          </div>
        ) : (
          <div className="d-flex justify-content-end gap-2 mt-3">
            <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onCancel()}>
              <span className="d-none d-sm-inline">{t('cancel')}</span>
            </Button>
            <Button color="primary" type="submit" text={t('save')} isLoading={isFormProcessing} />
          </div>
        )}
      </div>
    </form>
  );
};

export default FormContent;
