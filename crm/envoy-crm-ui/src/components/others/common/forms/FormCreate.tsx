import React, { useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import FormStepper from './FormStepper';
import { IElements, IFormTemplate, Step } from './models';
import ElementType from './ElementType';

function FormCreate({ templateData, onBack, isFormProcessing, onSubmit }: { templateData: IFormTemplate; onBack: Function; isFormProcessing: boolean; onSubmit: Function }) {
  const t = useTrans('otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [currentTab, setCurrentTab] = useState({} as Step);
  const [currentTabIndex, setCurrentTabIndex] = useState(0);
  const [formData, setFormData] = useState([] as IElements[]);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    console.log('hii');
    if (templateData?.elements) {
      setFormData(templateData.elements);
      if (templateData.steps && templateData.steps.length > 0) {
        const defaultTabSlug = templateData.steps[0].title.toLowerCase().replace(/\s+/g, '_');
        const foundIndex = templateData.steps.findIndex((step) => step.title.toLowerCase().replace(/\s+/g, '_') === defaultTabSlug);

        if (foundIndex !== -1) {
          const step = templateData.steps[foundIndex];
          setCurrentTab(step);
          setCurrentTabIndex(foundIndex);
        }
      }
      setSkeleton(false);
    }
  }, [templateData]);

  const onFormChange = (elementId: number, value: any) => {
    setFormData((prevFormData) => prevFormData.map((item) => (item.id === elementId ? { ...item, value } : item)));
  };

  const handleValidation = () => {
    clearError(form.form_template.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    if (templateData.template.type === 'multi_step_form') {
      const currentStep = templateData.steps[currentTabIndex];
      const currentStepElements = formData.filter((element) => element.step_id === currentStep.id);
      currentStepElements.forEach((element) => {
        if (element.is_required && !element.value) {
          error[element.id] = [
            {
              error_type: 'required',
              tokens: {
                _attribute: element.id.toString(),
              },
            },
          ];
        }
      });
    } else {
      formData.forEach((element) => {
        if (element.is_required && !element.value) {
          error[element.id] = [
            {
              error_type: 'required',
              tokens: {
                _attribute: element.id.toString(),
              },
            },
          ];
        }
      });
    }
    console.log('error', Object.keys(error));
    console.log('formData', formData);
    if (Object.keys(error).length > 0) {
      printError(error, form.form_template.store, tBe);
    } else {
      if (templateData.template.type === 'multi_step_form') {
        if (currentTabIndex === templateData.steps.length - 1) {
          const formattedFormData = formData.reduce(
            (acc, curr) => {
              acc[curr.id.toString()] = curr.value;
              return acc;
            },
            {} as Record<string, any>,
          );
          onSubmit(formattedFormData);
        } else {
          const nextIndex = currentTabIndex + 1;
          const nextStep = templateData.steps[nextIndex];
          setCurrentTab(nextStep);
          setCurrentTabIndex(nextIndex);
        }
      } else {
        const formattedFormData = formData.reduce(
          (acc, curr) => {
            acc[curr.id.toString()] = curr.value;
            return acc;
          },
          {} as Record<string, any>,
        );
        onSubmit(formattedFormData);
      }
    }
  };

  return (
    <>
      {skeleton ? (
        <Skeleton className="w-100" height={'400px'} />
      ) : (
        <div>
          {templateData?.steps?.length > 0 && <FormStepper templateName={templateData.template.name} steps={templateData.steps} currentTabId={currentTab.id} />}
          {templateData?.panels?.map((panel) => (
            <div key={panel.id} className={templateData.template?.type === 'multi_step_form' ? `d-${currentTab.id && currentTab.id === panel.step_id ? 'block' : 'none'}` : 'd-block'}>
              <div className="bg-white rounded-3 mb-3">
                <div className="panel-title">{panel.title}</div>
                <div className="row">
                  {formData
                    .filter((element) => element.panel_id === panel.id)
                    .map((element, index) => (
                      <div id={`${form.form_template.store}`} key={index} className={`col-12 col-md-${element.column_size} mb-3`}>
                        <ElementType
                          type={element.code}
                          onChange={(value) => onFormChange(element.id, value)}
                          options={element.options}
                          isRequired={element.is_required !== 0}
                          label={element.label}
                          value={element.value}
                          elementId={element.id.toString()}
                        />
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ))}
          {templateData?.template?.type === 'multi_step_form' ? (
            <div className="d-flex justify-content-start gap-2 mt-3">
              <Button
                color="light"
                className="d-flex align-items-center gap-1"
                onClick={() => {
                  if (currentTabIndex > 0) {
                    const prevIndex = currentTabIndex - 1;
                    const prevStep = templateData.steps[prevIndex];
                    setCurrentTab(prevStep);
                    setCurrentTabIndex(prevIndex);
                  } else {
                    onBack();
                  }
                }}
              >
                <Flexicon icon="chevron-left" variant="line" size={18} />
                <span className="d-none d-sm-inline">{t('back')}</span>
              </Button>

              {currentTabIndex < templateData.steps.length - 1 ? (
                <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleValidation}>
                  <span className="d-none d-sm-inline">{t('next')}</span>
                  <Flexicon icon="chevron-right" variant="line" size={18} />
                </Button>
              ) : (
                <Button color="primary" onClick={handleValidation} text={t('save')} isLoading={isFormProcessing} />
              )}
            </div>
          ) : (
            <div className="d-flex justify-content-start gap-2 mt-3">
              <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
                <Flexicon icon="chevron-left" variant="line" size={18} />
                <span className="d-none d-sm-inline">{t('back')}</span>
              </Button>
              <Button color="primary" onClick={handleValidation} text={t('save')} isLoading={isFormProcessing} />
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default FormCreate;
