# Deployment

## Vercel

Vercel's filesystem is ephemeral. Configure an S3-compatible bucket for uploaded media before using the CMS in production:

- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_REGION_NAME` (optional for providers such as R2)
- `AWS_S3_ENDPOINT_URL` (required for R2 or another S3-compatible provider)
- `AWS_S3_CUSTOM_DOMAIN` (optional public CDN/domain)
- `AWS_QUERYSTRING_AUTH=False` when the bucket or CDN is public

Without these variables, development uses local disk and Vercel falls back to `/tmp/media`; those uploads can disappear when the deployment instance is replaced.

The bucket must allow the deployed site to read uploaded files, either through a public media policy or a configured CDN/custom domain. Keep access keys private and never commit `.env` files.
