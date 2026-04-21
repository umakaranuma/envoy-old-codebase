import React, { useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import ElementType from '@/components/others/common/form/ElementType';
import { IClaimTemplate, IElement, Step } from '@/components/others/common/form/template-modal';

function CreatePolicyFormTemplate({
  templateData,
  onBack,
  isFormProcessing,
  onSubmit,
  currentTabIndex,
  setCurrentTabIndex,
  setCurrentTab,
  currentTab,
  breakTabId,
}: {
  templateData: IClaimTemplate;
  onBack: Function;
  isFormProcessing: boolean;
  onSubmit: Function;
  currentTabIndex: number;
  setCurrentTabIndex: Function;
  setCurrentTab: Function;
  currentTab: Step;
  breakTabId: number | null;
}) {
  const t = useTrans('label.my_policy,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState([] as IElement[]);

  useEffect(() => {
    setFormData(templateData.elements || []);
  }, [templateData]);

  // const fetchTemplateData = async () => {
  //   if (templateId) {
  //     const responseData = await getFormsElementsOfPolicy(templateId);
  //     if (responseData?.is_success) {
  //       setTemplateData(responseData.result);
  //       setFormData(responseData.result.elements);
  //       const templateResponseData = responseData.result as IClaimTemplate;
  //       // if (templateResponseData.steps && templateResponseData.steps.length > 0) {
  //       //   const defaultTabSlug = templateResponseData.steps[0].title.toLowerCase().replace(/\s+/g, '_');
  //       //   const foundIndex = templateResponseData.steps.findIndex((step) => step.title.toLowerCase().replace(/\s+/g, '_') === defaultTabSlug);

  //       //   if (foundIndex !== -1) {
  //       //     const step = templateResponseData.steps[foundIndex];
  //       //     setCurrentTab(step);
  //       //     setCurrentTabIndex(foundIndex);
  //       //   }
  //       // }
  //       setSkeleton(false);
  //     }
  //   }
  // };
  const onFormChange = (elementId: number, value: any) => {
    setFormData((prevFormData) => prevFormData.map((item) => (item.id === elementId ? { ...item, value } : item)));
  };

  const handleValidation = () => {
    clearError(form.claim.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    if (templateData.template.type === 'multi_step_form') {
      const currentStep = templateData.steps[currentTabIndex];
      console.log('currentStep', currentStep);

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

    if (Object.keys(error).length > 0) {
      printError(error, form.claim.store, tBe);
    } else {
      if (templateData.template.type === 'multi_step_form') {
        if (breakTabId === currentTab.id) {
          onSubmit(formData);
        } else {
          const nextIndex = currentTabIndex + 1;
          const nextStep = templateData.steps[nextIndex];
          setCurrentTab(nextStep);
          setCurrentTabIndex(nextIndex);
        }
      } else {
        onSubmit(formData);
      }
    }
  };

  return (
    <div>
      <>
        {templateData.panels &&
          templateData.panels.length > 0 &&
          templateData.panels.map((panel, index) => (
            <div key={panel.id} className={templateData.template?.type === 'multi_step_form' ? `d-${currentTab.id && currentTab.id === panel.step_id ? 'block' : 'none'}` : 'd-block'}>
              <div className="card-body bg-white p-3 rounded-3 mb-3" key={index}>
                <div className="fs-13 fw-semibold mb-3">{panel.title}</div>
                {
                  <div className="row">
                    {formData
                      .filter((element) => element.panel_id === panel.id)
                      .map((element, index) => (
                        <div id={`${form.claim.store}`} key={index} className={`col-12 col-md-${element.column_size} mb-3`}>
                          <ElementType
                            type={element.code}
                            onChange={(value) => {
                              onFormChange(element.id, value);
                              console.log('value' + value);
                              console.log('element.id' + element.id);
                            }}
                            options={element.options}
                            isRequired={element.is_required !== 0}
                            label={element.label}
                            value={element.value}
                            elementId={element.id.toString()}
                          />
                        </div>
                      ))}
                  </div>
                }
              </div>
            </div>
          ))}
      </>
      {/* {(templateData.template && templateData.template.type) === 'multi_step_form' ? ( */}
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
          <Button
            color="primary"
            className="d-flex align-items-center gap-1"
            onClick={() => {
              handleValidation();
            }}
          >
            <span className="d-none d-sm-inline">{t('next')}</span>
            <Flexicon icon="chevron-right" variant="line" size={18} />
          </Button>
        ) : (
          <Button color="primary" onClick={handleValidation} text={t('save')} isLoading={isFormProcessing} />
        )}
      </div>
      {/* // ) : (
      //   <div className="d-flex justify-content-start gap-2 mt-3">
      //     <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
      //       <Flexicon icon="chevron-left" variant="line" size={18} />
      //       <span className="d-none d-sm-inline">{t('back')}</span>
      //     </Button>
      //     <Button color="primary" onClick={handleValidation} text={t('save')} isLoading={isFormProcessing} />
      //   </div>
      // )} */}
    </div>
  );
}

export default CreatePolicyFormTemplate;
