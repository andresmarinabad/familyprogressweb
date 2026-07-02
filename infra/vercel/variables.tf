variable "vercel_api_token" {
  type      = string
  sensitive = true
}

variable "github_repo" {
  type = string
}

variable "domain" {
  type = string
}

variable "github_token" {
  type        = string
  sensitive   = true
  description = "GitHub PAT with contents:write scope for uploading images via API"
}

variable "supabase_url" {
  type        = string
  description = "Supabase project URL — from: cd infra/supabase && tofu output supabase_url"
}

variable "supabase_service_role_key" {
  type        = string
  sensitive   = true
  description = "Supabase service role key — from: cd infra/supabase && tofu output -raw service_role_key"
}
