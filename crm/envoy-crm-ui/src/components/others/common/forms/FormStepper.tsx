import React from 'react';

function FormStepper({ templateName, steps, currentTabId }: { templateName?: string; steps: any[]; currentTabId: number }) {
  return (
    <div className="card-body bg-white p-3 rounded-3 mb-3">
      {templateName && (
        <div className="mb-4">
          <div className="fs-5 fw-semibold text-center">{templateName}</div>
        </div>
      )}
      <div className="d-flex justify-content-between align-items-center">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className="d-flex flex-column align-items-center" style={{ flex: 1 }}>
              <div
                className={`rounded-circle d-flex align-items-center justify-content-center ${
                  currentTabId === step.id || steps.findIndex((s) => s.id === currentTabId) > index ? 'bg-primary text-white shadow' : 'border border-2 border-light'
                }`}
                style={{
                  width: '36px',
                  height: '36px',
                  position: 'relative',
                  zIndex: 1,
                }}
              >
                {step.id <= currentTabId ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="11" viewBox="0 0 13 11" fill="none">
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M11.598 0.389671L4.43797 7.29967L2.53797 5.26967C2.18797 4.93967 1.63797 4.91967 1.23797 5.19967C0.847968 5.48967 0.737968 5.99967 0.977968 6.40967L3.22797 10.0697C3.44797 10.4097 3.82797 10.6197 4.25797 10.6197C4.66797 10.6197 5.05797 10.4097 5.27797 10.0697C5.63797 9.59967 12.508 1.40967 12.508 1.40967C13.408 0.489671 12.318 -0.320329 11.598 0.379671V0.389671Z"
                      fill="currentColor"
                    />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="9" height="8" viewBox="0 0 9 8" fill="none">
                    <circle cx="4.5" cy="4" r="4" fill="#D0D5DD" />
                  </svg>
                )}
              </div>
              <div className="text-center mt-2">
                <div className="fw-medium fs-12">{step.title}</div>
              </div>
            </div>

            {index < steps.length - 1 && (
              <div className={`flex-grow-1 mx-2 ${steps.findIndex((s) => s.id === currentTabId) > index ? 'bg-primary' : 'bg-light'}`} style={{ height: '4px', borderRadius: '2px' }} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export default FormStepper;
