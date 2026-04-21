import { Input, Label } from '@apptimus-ui/ui-element';
import React, { useState, useEffect } from 'react';

interface CurrencyInputProps {
  label?: string;
  isRequired?: boolean;
  className?: string;
  value?: { amount: string; currency: string };
  onChange?: (val: { amount: string; currency: string }) => void;
}

const currencyOptions = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
];

const CurrencyInput = ({ label, isRequired, className, value, onChange }: CurrencyInputProps) => {
  const [amount, setAmount] = useState(value?.amount || '');
  const [currency, setCurrency] = useState(value?.currency || 'JPY');

  useEffect(() => {
    if (value) {
      setAmount(value.amount ?? '');
      setCurrency(value.currency ?? 'JPY');
    }
  }, [value]);

  const handleCurrencyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrency(e.target.value);
    onChange?.({ amount, currency: e.target.value });
  };

  const handleAmountChange = (e: any) => {
    setAmount(e.target.value);
    onChange?.({ amount: e.target.value, currency });
  };

  return (
    <div>
      {label && <Label label={label} isRequired={isRequired} />}
      <div className="input-group">
        <span className="input-group-text p-0">
          <select
            value={currency}
            onChange={handleCurrencyChange}
            className="form-select border-0 shadow-none"
            style={{
              padding: '0.375rem 0.75rem',
              backgroundColor: 'transparent',
              appearance: 'none',
              fontSize: '1rem',
            }}
          >
            {currencyOptions.map(({ code, symbol }) => (
              <option key={code} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </span>
        <Input type="number" id="amountInput" className={className} aria-label="Amount" value={amount} onChange={(e) => handleAmountChange(e)} />
      </div>
    </div>
  );
};

export default CurrencyInput;
