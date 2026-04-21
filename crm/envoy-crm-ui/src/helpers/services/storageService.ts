'use server';
import { DeleteObjectCommand, GetObjectCommand, S3Client } from '@aws-sdk/client-s3';
import { createPresignedPost } from '@aws-sdk/s3-presigned-post';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { nanoid } from 'nanoid';

const s3 = new S3Client({
  region: process.env.S3_REGION as string,
  credentials: {
    accessKeyId: process.env.S3_ACCESS_KEY_ID as string,
    secretAccessKey: process.env.S3_SECRET_ACCESS_KEY as string,
  },
});

export async function fileUploader(formData: FormData, folder: string) {
  try {
    const file = formData.get('file') as File;
    if (!file) {
      throw new Error('No file provided');
    }
    const key = `${folder}/${nanoid()}_${file.name}`;

    const { url, fields } = await createPresignedPost(s3, {
      Bucket: process.env.S3_BUCKET_NAME as string,
      Key: key,
      Fields: {
        key: key,
        'Content-Type': file.type,
      },
      Conditions: [
        ['content-length-range', 0, 52428800], // max 50 MB
      ],
    });

    const s3formData = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
      s3formData.append(key, value);
    });

    s3formData.append('file', file);

    const response = await fetch(url, {
      method: 'POST',
      body: s3formData,
    });

    if (!response.ok) {
      throw new Error(`File upload failed with status: ${response.status}`);
    }

    console.log('File upload success', response);
    return key;
  } catch (error) {
    console.error('Error', error);
    throw error;
  }
}

export async function fileReceiver({ key, expiresIn = 3600 }: { key: string; expiresIn?: number }): Promise<string> {
  const command = new GetObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME as string,
    Key: key,
  });

  try {
    const url = await getSignedUrl(s3, command, {
      expiresIn,
    });
    return url;
  } catch (error) {
    console.error('Error generating signed URL:', error);
    throw error;
  }
}

export async function fileRemover(key: string) {
  const command = new DeleteObjectCommand({
    Bucket: process.env.S3_BUCKET_NAME as string,
    Key: key,
  });

  try {
    await s3.send(command);
    console.log(`File deleted successfully: ${key}`);
    return { success: true, message: 'File deleted successfully' };
  } catch (error) {
    console.error('Error deleting file:', error);
    throw error;
  }
}
