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

export interface IFilePreviewer {
  id: number;
  name: string;
  size: number;
  type?: string;
  url: string;
}
