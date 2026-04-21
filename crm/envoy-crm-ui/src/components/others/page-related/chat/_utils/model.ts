export interface IMessage {
  id: number;
  body: string;
  conversation_id: string | null;
  sent_at: string;
  type: string;
  attachments: IAttachment[];
}
export interface IAttachment {
  id: number;
  file_name: string;
  content_type: string;
  size_bytes: number;
  is_image: number;
  file_url: string;
  gmail_attachment_id: string;
  download_url: string;
}

export const initMessage = {
  body: '',
  Documents: [],
  conversation_id: '',
};

export interface IFileData {
  document_name: string;
  document_url: string;
  document_type: string;
  file_key: string;
  extracted_data: ExtractedData;
  quotation_fields: QuotationFields;
}

export interface ExtractedData {
  payment_mode: string;
  policy_issue_date: string;
  start_date: string;
  end_date: string;
  policy_period_from_date: string;
  policy_period_to_date: string;
  product_name: string;
}

export interface QuotationFields {
  insurer_company_name: string;
  insurer_company_id: string;
  received_date: Date;
  expiry_date: Date;
  total_amount: string;
  revised: string;
  uploaded_by: string;
}
