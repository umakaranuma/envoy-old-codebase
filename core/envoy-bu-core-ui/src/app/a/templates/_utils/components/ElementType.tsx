import { Label } from '@apptimus-ui/ui-element';
import IconInput from './Elements/IconInput';
import Switch from './Elements/Switch';
import InputField from './Elements/InputField';
import MultiSelects from './Elements/MultiSelects';
import RadioBox from './Elements/RadioBox';
import PhoneInput from 'react-phone-input-2';
import Image from 'next/image';
import OptionScale from './Elements/OptionScale';
import CustomRangeSlider from './Elements/CustomRangeSlider';
import Ranking from './Elements/Ranking';
import StarRatingDisplay from './Elements/StarRatingDisplay';
import CurrencyInput from './Elements/CurrencyInput';
import DevelopmentCard from './Elements/DevelopmentCard';
import SelectInput from './Elements/SelectInput';
import MultiSelectInput from './Elements/MultiSelect';
import PdfViewer from './Elements/PdfViewer';
import FilePreviewer from './Elements/FilePreviewer';
import 'react-phone-input-2/lib/style.css';

const ElementType = ({
  type,
  label,
  isRequired,
  options,
  value,
  elementId,
}: {
  type: string;
  className?: string;
  label?: string;
  isRequired?: boolean;
  options?: any;
  onChange?: (value: any) => void;
  placeholder?: string;
  value?: any;
  elementId?: string;
}) => {
  function optionformater(options: any[]): { id: string; value: string }[] {
    return options.map((opt) => ({
      id: opt.id?.toString() ?? '',
      value: opt.option_value ?? '',
    }));
  }
  switch (type) {
    // Text
    case 'SORT_ANSWER':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="text"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'LONG_ANSWER':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="textarea"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );

    // Display Text
    case 'HEADING':
      return <div className="fw-semibold h5">{value}</div>;
    case 'PARAGRAPH':
      return <>{value}</>;
    case 'BANNER':
      return (
        <div style={{ width: '100%', position: 'relative', aspectRatio: '16/5' }}>
          <Image
            src={value}
            alt="Banner Preview"
            fill
            style={{
              objectFit: 'fill',
              width: '100%',
            }}
            className="rounded"
            priority
          />
        </div>
      );
    case 'LINE_BREAK':
      return <hr className="border border-2 border-light" />;

    // Choices
    case 'DROPDOWN':
      return (
        <SelectInput
          label={label}
          isRequired={isRequired}
          options={optionformater(options)}
          elementId={elementId}
          onChange={(data) => {
            console.log(data);
          }}
        />
      );
    case 'PICTURE_CHOICE':
      return <DevelopmentCard />;
    case 'MULTI_SELECT':
      return (
        <MultiSelectInput
          label={label}
          isRequired={isRequired}
          options={optionformater(options)}
          elementId={elementId}
          onChange={(data) => {
            console.log(data);
          }}
        />
      );
    case 'SWITCH':
      return (
        <Switch
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
          defaultToggled={true}
          onToggle={(value) => {
            console.log(value);
          }}
        />
      );
    case 'MULTI_CHOICE':
      return (
        <MultiSelects
          label={label}
          isRequired={isRequired}
          options={optionformater(options)}
          className={`form-control error-${elementId}`}
          onChange={(data: any) => {
            console.log(data);
          }}
        />
      );
    case 'RADIO_BOX':
      return (
        <RadioBox
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
          options={optionformater(options)}
          onChange={(data: any) => {
            console.log(data);
          }}
        />
      );

    // Date & Time
    case 'DATE_PICKER':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="date"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'TIME_PICKER':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="time"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'DATE_TIME':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="datetime-local"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'DATE_RANGE':
      return label && <Label label={label} isRequired={isRequired} />;
    case 'DATE_RANGE_TO_DATE':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="date"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'DATE_RANGE_FROM_DATE':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="date"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );

    //Rating & Ranking
    case 'RANKING':
      return (
        <Ranking
          onChange={(values, orderObjects) => {
            console.log('Values:', values);
            console.log('Order objects:', orderObjects);
          }}
          options={optionformater(options)}
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
        />
      );
    case 'STAR_RATING':
      return <StarRatingDisplay onChange={(value) => console.log(value)} label={label} isRequired={isRequired} className={`error-${elementId}`} id={elementId} value={value} />;
    case 'SLIDER':
      return <CustomRangeSlider min={0} max={10} step={1} label={label} onChange={(value) => console.log(value)} isRequired={isRequired} className={`error-${elementId}`} />;
    case 'OPTION_SCALE':
      return <OptionScale onChange={(value) => console.log(value)} label={label} isRequired={isRequired} className={`error-${elementId}`} value={value} />;

    //Contact Info
    case 'PHONE_INPUT':
      return (
        <div>
          {label && <Label label={label} isRequired={isRequired} />}
          <PhoneInput
            country={'lk'}
            enableAreaCodes={true}
            value={value || ''}
            inputStyle={{ height: '40px', width: '100%' }}
            containerStyle={{ height: '40px', width: '100%' }}
            onChange={(value) => console.log(value)}
            inputClass={`form-control error-${elementId}`}
            countryCodeEditable={false}
          />
        </div>
      );
    case 'EMAIL_INPUT':
      return (
        <IconInput
          id={elementId}
          icon={'EMAIL'}
          className={`error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="email"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'ADDRESS':
      return (
        <IconInput
          id={elementId}
          icon={'ADDRESS'}
          className={`error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="text"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );

    //Numbers
    case 'NUMBERS':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="number"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'CURRENCY':
      return (
        <CurrencyInput
          label={label}
          isRequired={isRequired}
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          value={value || ''}
        />
      );

    // Miscellaneous
    case 'URL_INPUT':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="url"
          value={value || ''}
          isRequired={isRequired}
          label={label}
          placeholder="http://example.com"
        />
      );
    case 'COLOR_PICKER':
      return (
        <InputField
          className={`error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="color"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'PASSWORD':
      return (
        <IconInput
          className={`error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="password"
          value={value || ''}
          isRequired={isRequired}
          label={label}
          icon={'PASSWORD'}
        />
      );
    case 'FILE_UPLOAD':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            console.log(value);
          }}
          type="file"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'SIGNATURE':
      return <DevelopmentCard />;
    case 'VOICE_RECORDING':
      return <DevelopmentCard />;
    case 'SUBMISSION_PICKER':
      return (
        <FilePreviewer
          onChange={(value: any) => {
            console.log('value from file previewer:', value);
          }}
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
          elementId={elementId}
          fileType={value}
        />
      );
    case 'LOCATION':
      return label && <Label label={label} isRequired={isRequired} />;
    case 'LOCATION_LATITUDE':
      return (
        <InputField
          onChange={(value) => {
            console.log(value);
          }}
          type="text"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'LOCATION_LONGITUDE':
      return (
        <InputField
          onChange={(value) => {
            console.log(value);
          }}
          type="text"
          value={value || ''}
          isRequired={isRequired}
          label={label}
        />
      );
    case 'CAPTCHA':
      return <DevelopmentCard />;
    case 'SUBFORM':
      return <DevelopmentCard />;

    // Navigation & Layout
    case 'SECTION_COLLAPSE':
      return <DevelopmentCard />;
    case 'DIVIDER':
      return (
        <div className="my-3">
          <div className="bg-light w-100 h-100 rounded-3" style={{ minHeight: '65px' }}></div>
        </div>
      );
    case 'PANEL':
      return <DevelopmentCard />;
    case 'HTML':
      return <DevelopmentCard />;

    // Media
    case 'IMAGE_VIEWER':
      return (
        <div style={{ width: '100%', height: '300px', minHeight: '300px', position: 'relative' }}>
          <Image
            src={value}
            alt="Preview"
            fill
            style={{
              objectFit: 'cover',
              width: '100%',
              height: '100%',
            }}
            className="rounded"
          />
        </div>
      );
    case 'VIDEO_VIEWER':
      return (
        <div>
          <div className=" text-center">{label && <Label label={label} />}</div>
          <video width="100%" controls className="rounded">
            <source src={value} />
          </video>
        </div>
      );
    case 'PDF_VIEWER': {
      return <PdfViewer value={value} label={label} />;
    }

    default:
      return <DevelopmentCard label="Something Wrong" />;
  }
};

export default ElementType;
