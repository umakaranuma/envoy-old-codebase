type Value = string | string[];

export interface IFilterValue {
  o: string;
  v: Value;
  t: 'T' | 'A';
}

export interface IFilters {
  [key: string]: IFilterValue;
}
