variable "supabase_access_token" {
  type        = string
  sensitive   = true
  description = "Supabase management API access token (dashboard → Account → Access Tokens)"
}

variable "supabase_org_id" {
  type        = string
  description = "Supabase organization ID (dashboard → Settings → General)"
}
