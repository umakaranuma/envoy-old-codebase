import React from 'react';
import { Accordion, AccordionItem } from '@apptimus-ui/accordion';
import { useTrans } from '@/helpers/services/lang/langService';
import ErrorList from './ErrorList';
import { Description } from '@/components/others/Description';
function Summary() {
  const t = useTrans('label.invoice,otr.common,be.msg');
  return (
    <div className="panel">
      <div className="fs-15 fw-semibold mb-3">{t('summary')}</div>
      <div className="mb-3">
        <div className="d-flex align-items-center gap-2  justify-content-center">
          <Description label={t('imported_file_summary')} value={'August Policy Payment Details.xlsx'} />
        </div>
        <div className="d-flex flex-row flex-wrap gap-3 justify-content-center py-3">
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('new')} value={'100'} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('updated')} value={'03'} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('ignored')} value={'05'} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('total')} value={'108'} />
          </div>
        </div>
      </div>
      <div>
        <div className="mb-2">
          <Accordion bodyRenderOption="when-active">
            <AccordionItem key={1} title={<div className="fs-14">{t('alert')}</div>}>
              <div className="p-3">
                <ErrorList type={''} />
              </div>
            </AccordionItem>
          </Accordion>
        </div>
        <div className="mb-2">
          <Accordion bodyRenderOption="when-active">
            <AccordionItem key={2} title={<div className="fs-14">{t('duplication')}</div>}>
              <div className="p-3">
                <ErrorList type={''} />
              </div>
            </AccordionItem>
          </Accordion>
        </div>
        <div className="mb-2">
          <Accordion bodyRenderOption="when-active">
            <AccordionItem key={3} title={<div className="fs-14">{t('error')}</div>}>
              <div className="p-3">
                <ErrorList type={''} />
              </div>
            </AccordionItem>
          </Accordion>
        </div>
        <div className="mb-2">
          <Accordion bodyRenderOption="when-active">
            <AccordionItem key={4} title={<div className="fs-14">{t('info')}</div>}>
              <div className="p-3">
                <ErrorList type={''} />
              </div>
            </AccordionItem>
          </Accordion>
        </div>
        <div className="mb-2">
          <Accordion bodyRenderOption="when-active">
            <AccordionItem key={5} title={<div className="fs-14">{t('warning')}</div>}>
              <div className="p-3">
                <ErrorList type={''} />
              </div>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
    </div>
  );
}

export default Summary;
