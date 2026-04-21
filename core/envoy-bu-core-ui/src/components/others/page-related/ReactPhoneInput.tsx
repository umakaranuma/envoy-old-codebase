import React, { useState } from 'react';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';

function ReactPhoneInput({
  defaultCountryCode = 'lk',
  className,
  enableAreaCodes = true,
  value,
  countryCodeEditable = false,
  onChange,
}: {
  defaultCountryCode: string;
  value: string;
  enableAreaCodes: boolean;
  className?: string;
  countryCodeEditable?: boolean;
  onChange: (value: string, country: any, e: React.ChangeEvent<HTMLInputElement>, formattedValue: string) => void;
}) {
  const [inputValue, setInputValue] = useState(value);
  return (
    <PhoneInput
      country={defaultCountryCode}
      enableAreaCodes={enableAreaCodes}
      value={inputValue}
      inputStyle={{ height: '40px', width: '100%' }}
      containerStyle={{ height: '40px', width: '100%' }}
      onChange={(value, country: any, e, formattedValue) => {
        setInputValue(value);
        if (value.length <= country.countryCode.length) {
          onChange('', country, e, formattedValue);
        } else {
          onChange(value, country, e, formattedValue);
        }
      }}
      inputClass={className}
      countryCodeEditable={countryCodeEditable}
    />
  );
}

export default ReactPhoneInput;
