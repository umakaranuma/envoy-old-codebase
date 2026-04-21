import { Flexicon } from '@apptimus-ui/flexicon';
import React, { useState } from 'react';
import { EditableText } from './EditableText';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { createPanel, createStep, UpdateStep } from '../api-service';
import { useParams } from 'next/navigation';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import StepDelete from './StepDelete';

function StepSection({
  steps,
  loading,
  setActiveStepId,
  activeStepId,
  setSteps,
  setPanels,
}: {
  steps: any;
  loading: any;
  setActiveStepId: any;
  activeStepId: number | null;
  setSteps: any;
  setPanels: any;
}) {
  const params = useParams();
  const templateId = params.id?.toString() || '';
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isLoading, setIsLoading] = useState(false);
  const [deleteModel, SetDeleteModel] = useState(false);
  const [stepId, setStepId] = useState(0);

  const handleCreateStep = async () => {
    try {
      setIsLoading(true);
      const response = await createStep({ title: 'Untitled Step' }, templateId);

      if (response.is_success) {
        toaster.success(tBe(response.message));
        const responseData = await createPanel({ title: 'Untitled Panel', step_id: response.result.id }, templateId);
        setSteps((prev: any) => [...prev, response.result]);
        setPanels((prev: any) => [...prev, responseData.result]);
      } else {
        toaster.error(tBe(response.message));
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateStep = async (formData: any, templateId: string, stepId: any) => {
    try {
      setIsLoading(true);
      const response = await UpdateStep(formData, templateId, stepId);

      if (response.is_success) {
        toaster.success(tBe(response.message));
        setSteps((prevSteps: any) => prevSteps.map((step: any) => (step.id === stepId ? { ...step, ...formData } : step)));
      } else {
        toaster.error(tBe(response.message));
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {loading ? (
        <div className="d-flex justify-content-center gap-3 mt-3">
          <Skeleton height="50px" width="50px" className="rounded-pill" />
          <Skeleton height="50px" width="50px" className="rounded-pill" />
          <Skeleton height="50px" width="50px" className="rounded-pill" />
          <Skeleton height="50px" width="50px" className="rounded-pill" />
        </div>
      ) : isLoading ? (
        <div className="d-flex justify-content-center gap-3 mt-3">
          <Skeleton height="50px" width="50px" className="rounded-pill" />
          <Skeleton height="50px" width="50px" className="rounded-pill" />
          <Skeleton height="50px" width="50px" className="rounded-pill" />
          <Skeleton height="50px" width="50px" className="rounded-pill" />
        </div>
      ) : (
        steps.length > 0 && (
          <div className="mb-2 mt-3 ">
            <div className="d-flex align-items-center flex-wrap gap-2 justify-content-center">
              {steps.map((step: any, index: number) => (
                <div key={step.id}>
                  <div className="d-flex align-items-center gap-2">
                    <div className="d-flex flex-column align-items-center text-center" style={{ maxWidth: '100px' }}>
                      <div
                        onClick={() => setActiveStepId(step.id)}
                        className={`rounded-circle d-flex align-items-center justify-content-center mb-1 ${
                          activeStepId === step.id || steps.findIndex((s: any) => s.id === activeStepId) > index ? 'bg-primary text-white shadow' : 'border border-2 border-light'
                        }`}
                        style={{ width: '36px', height: '36px', cursor: 'pointer' }}
                      >
                        {steps.findIndex((s: any) => s.id === activeStepId) > index || activeStepId === step.id ? (
                          // Completed step
                          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="11" viewBox="0 0 13 11" fill="none">
                            <path
                              fillRule="evenodd"
                              clipRule="evenodd"
                              d="M11.598 0.389671L4.43797 7.29967L2.53797 5.26967C2.18797 4.93967 1.63797 4.91967 1.23797 5.19967C0.847968 5.48967 0.737968 5.99967 0.977968 6.40967L3.22797 10.0697C3.44797 10.4097 3.82797 10.6197 4.25797 10.6197C4.66797 10.6197 5.05797 10.4097 5.27797 10.0697C5.63797 9.59967 12.508 1.40967 12.508 1.40967C13.408 0.489671 12.318 -0.320329 11.598 0.379671V0.389671Z"
                              fill="currentColor"
                            />
                          </svg>
                        ) : (
                          // Incomplete step
                          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="8" viewBox="0 0 9 8" fill="none">
                            <circle cx="4.5" cy="4" r="4" fill="#D0D5DD" />
                          </svg>
                        )}
                      </div>
                      <small className="text-muted mt-2" style={{ wordBreak: 'break-word', maxWidth: '100%' }}>
                        <EditableText
                          id={step.id}
                          title={step.title}
                          onChange={(title) => {
                            handleUpdateStep({ title: title }, templateId, step.id);
                          }}
                        />
                      </small>
                      {steps.length > 2 && activeStepId === step.id && (
                        <Button
                          onClick={() => {
                            SetDeleteModel(true);
                            setStepId(step.id);
                          }}
                          color="danger"
                          isLoading={isLoading}
                          className="p-1"
                        >
                          <Flexicon icon="trash-03" variant="line" size={16} />
                        </Button>
                      )}
                    </div>

                    {index < steps.length && (
                      <div
                        className={`${steps.findIndex((s: any) => s.id === activeStepId) > index ? 'bg-primary' : 'bg-light'}`}
                        style={{ width: '70px', height: '4px', borderRadius: '2px', flexShrink: 0 }}
                      />
                    )}
                  </div>
                </div>
              ))}

              <div className="d-flex flex-column align-items-center text-center">
                <div
                  onClick={() => handleCreateStep()}
                  className={`rounded-circle d-flex align-items-center justify-content-center mb-1 bg-primary text-white shadow}`}
                  style={{ width: '36px', height: '36px', cursor: 'pointer' }}
                >
                  <Flexicon icon="plus" variant="line" />
                </div>
              </div>
            </div>
          </div>
        )
      )}

      {/* step Delete Modal  */}
      {deleteModel && (
        <StepDelete
          isOpen={deleteModel}
          onCancel={() => {
            SetDeleteModel(false);
          }}
          setSteps={setSteps}
          stepId={stepId}
          templateId={templateId}
          activeStepId={activeStepId}
          setActiveStepId={setActiveStepId}
          afterDelete={() => {
            SetDeleteModel(false);
          }}
        />
      )}
    </>
  );
}

export default StepSection;
