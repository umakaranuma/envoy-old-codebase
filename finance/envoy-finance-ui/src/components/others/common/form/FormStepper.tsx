import React from 'react';
import { Step } from './template-modal';
import { Flexicon } from '@apptimus-ui/flexicon';

function FormStepper({ templateName, steps, currentTabId }: { templateName: string; steps: Step[]; currentTabId: number }) {
  return (
    <div className="card-body bg-white p-3 rounded-3 mb-3">
      <div className="mb-3">
        <div className="fs-20 fw-semibold text-center">{templateName}</div>
      </div>
      <ul className="d-flex justify-content-center gap-5 list-unstyled mb-0 crm-recent-activity">
        {steps.map((step, index) => (
          <li key={index} className="crm-recent-activity-content">
            <div className="align-items-center">
              <div className="d-flex justify-content-center me-3">
                {step.id <= currentTabId ? (
                  <>
                    <span className={`avatar avatar-xs bg-primary-transparent avatar-rounded`}>
                      <Flexicon icon="check-circle" variant="solid" size={50} />
                    </span>
                  </>
                ) : (
                  <>
                    <span className="avatar claim-avatar claim-transparent claim-avatar-rounded">
                      <i className="bi bi-circle-fill fs-8"></i>
                    </span>
                  </>
                )}
              </div>
              <div className="mt-2">
                <div className="fw-medium mb-1 fs-12">{step.title}</div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FormStepper;
