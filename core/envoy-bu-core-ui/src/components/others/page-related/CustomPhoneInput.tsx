import React, { useState } from 'react';
import PhoneInput, { CountryData } from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';

function CustomPhoneInput({ value, onChange }: { value: string; onChange: (phone: string) => void }) {
  const [, setPhoneData] = useState<CountryData | undefined>(undefined);

  const handleChange = (phone: string, data: CountryData) => {
    setPhoneData(data);

    // Always pass the phone number as is, allowing users to delete country code
    onChange(phone);
  };

  return (
    <div>
      <PhoneInput
        country={'lk'}
        enableAreaCodes={true}
        value={value}
        inputStyle={{ height: '40px', width: '100%' }}
        containerStyle={{ height: '40px', width: '100%' }}
        onChange={(phone, data: CountryData) => handleChange(phone, data)}
        inputClass="form-control error-contact_number"
        countryCodeEditable={true}
        placeholder=""
        specialLabel=""
        autoFormat={false}
      />
    </div>
  );
}

export default CustomPhoneInput;
