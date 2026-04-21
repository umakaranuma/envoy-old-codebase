import ToggleButton from '@/components/others/page-related/ToggleButton';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';

function AutomationSettings() {
  const t = useTrans('otr.common');
  return (
    <div className="mt-2 mt-md-4">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">Notification Settings</div>
        <div className="text-muted mb-2">We may still send you important Workflows Automation about your account outside of your notification settings.</div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">Comments</div>
              <div className="text-muted">These are Workflows Automation for comments on your posts and replies to your comments.</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Push</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Email</div>
              </div>
              <div className="d-flex gap-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>SMS</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">Tags</div>
              <div className="text-muted">These are Workflows Automation for comments on your posts and replies to your comments.</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Push</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Email</div>
              </div>
              <div className="d-flex gap-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>SMS</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">Reminders</div>
              <div className="text-muted">These are Workflows Automation to remind you of updates you might have missed.</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Push</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Email</div>
              </div>
              <div className="d-flex gap-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>SMS</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">More activity about you</div>
              <div className="text-muted">These are Workflows Automation for posts on your profile, likes and other reactions to your posts, and more.</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Push</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>Email</div>
              </div>
              <div className="d-flex gap-2">
                <ToggleButton isToggled={true} setIsToggled={() => {}} />
                <div>SMS</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-3">
        <Button text={t('cancel')} color="light" width="sm" />
        <Button className="d-flex align-items-center gap-1">
          <Flexicon icon="save-01" variant="line" size={18} />
          <span>{t('save_changes')}</span>
        </Button>
      </div>
    </div>
  );
}

export default AutomationSettings;
