import { Label } from '@apptimus-ui/ui-element';
import IconInput from './elements/IconInput';
import Switch from './elements/Switch';
import InputField from './elements/InputField';
import MultiSelects from './elements/MultiSelects';
import RadioBox from './elements/RadioBox';
import PhoneInput from 'react-phone-input-2';
import Image from 'next/image';
import OptionScale from './elements/OptionScale';
import CustomRangeSlider from './elements/CustomRangeSlider';
import Ranking from './elements/Ranking';
import StarRatingDisplay from './elements/StarRatingDisplay';
import CurrencyInput from './elements/CurrencyInput';
import DevelopmentCard from './elements/DevelopmentCard';
import SelectInput from './elements/SelectInput';
import MultiSelectInput from './elements/MultiSelect';
import PdfViewer from './elements/PdfViewer';
import FilePreviewer from './elements/FilePreviewer ';
import { fileUploader } from '@/helpers/services/storageService';
import 'react-phone-input-2/lib/style.css';

const ElementType = ({
  type,
  label,
  isRequired,
  options,
  value,
  elementId,
  onChange,
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
  function optionFormatter(options: any[]): { id: string; value: string }[] {
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
          options={optionFormatter(options)}
          elementId={elementId}
          onChange={(data) => {
            onChange && onChange(data.value);
          }}
          defaultValue={value || ''}
        />
      );
    case 'PICTURE_CHOICE':
      return <DevelopmentCard />;
    case 'MULTI_SELECT':
      return (
        <MultiSelectInput
          label={label}
          isRequired={isRequired}
          options={optionFormatter(options)}
          elementId={elementId}
          onChange={(data) => {
            const refinedData = data.map((item: any) => item.value);
            console.log(refinedData);

            onChange && onChange(refinedData.length === 0 ? '' : refinedData);
          }}
          defaultValue={typeof value === 'string' && value.trim() !== '' ? JSON.parse(value.replace(/'/g, '"')) : Array.isArray(value) ? value : []}
        />
      );
    case 'SWITCH':
      return (
        <Switch
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
          defaultToggled={value}
          onToggle={(value) => {
            onChange && onChange(value);
          }}
        />
      );
    case 'MULTI_CHOICE':
      return (
        <MultiSelects
          label={label}
          isRequired={isRequired}
          options={optionFormatter(options)}
          className={`error-${elementId}`}
          onChange={(value: any) => {
            onChange && onChange(value.length === 0 ? '' : value);
          }}
          defaultValue={typeof value === 'string' && value.trim() !== '' ? JSON.parse(value.replace(/'/g, '"')) : Array.isArray(value) ? value : []}
        />
      );
    case 'RADIO_BOX':
      return (
        <RadioBox
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
          options={optionFormatter(options)}
          onChange={(data: any) => {
            onChange && onChange(data.value);
          }}
          selectedValue={value || ''}
        />
      );

    // Date & Time
    case 'DATE_PICKER':
      return (
        <InputField
          className={`form-control error-${elementId}`}
          onChange={(value) => {
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
          options={optionFormatter(options)}
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
        />
      );
    case 'STAR_RATING':
      return <StarRatingDisplay onChange={(value) => onChange && onChange(value)} label={label} isRequired={isRequired} className={`error-${elementId}`} id={elementId} value={value} />;
    case 'SLIDER':
      return <CustomRangeSlider min={0} max={10} step={1} label={label} onChange={(value) => onChange && onChange(value)} isRequired={isRequired} className={`error-${elementId}`} />;
    case 'OPTION_SCALE':
      return <OptionScale onChange={(value) => onChange && onChange(value)} label={label} isRequired={isRequired} className={`error-${elementId}`} value={value || ''} />;

    //Contact Info
    case 'PHONE_INPUT':
      return (
        <div className={`error-${elementId}`}>
          {label && <Label label={label} isRequired={isRequired} />}
          <PhoneInput
            country={'lk'}
            enableAreaCodes={true}
            value={value || ''}
            inputStyle={{ height: '40px', width: '100%' }}
            containerStyle={{ height: '40px', width: '100%' }}
            onChange={(value) => onChange && onChange(value)}
            inputClass="form-control"
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
            onChange && onChange(value);
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
          onChange={async (file: any) => {
            const value = await handleFilePreviewer(file);
            onChange && onChange(value);
          }}
          label={label}
          isRequired={isRequired}
          className={`error-${elementId}`}
          initialUrl={value}
        />
      );
    case 'LOCATION':
      return label && <Label label={label} isRequired={isRequired} />;
    case 'LOCATION_LATITUDE':
      return (
        <InputField
          onChange={(value) => {
            onChange && onChange(value);
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
            onChange && onChange(value);
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
      return <div style={{ minHeight: '50px' }}></div>;
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

const handleFilePreviewer = async (file: File | undefined) => {
  if (!file) {
    return '';
  }

  const data = await handleFileUpload(file);
  const valueArray = [];

  valueArray.push(data?.doc || '');
  valueArray.push(data?.name || '');

  return valueArray;
};

const handleFileUpload = async (file: File) => {
  const formData = new FormData();
  if (!file) {
    return null;
  }
  formData.append('file', file);
  const fileName = file.name;
  const fileExtension = file.name.split('.').pop();
  const key = await fileUploader(formData, 'envoy-test');
  return { doc: key, name: fileName, type: fileExtension };
};
