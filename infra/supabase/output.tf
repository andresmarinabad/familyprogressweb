output "project_ref" {
  description = "Supabase project reference ID"
  value       = supabase_project.familyprogressweb.id
}

output "supabase_url" {
  description = "Supabase project URL — set as SUPABASE_URL in Vercel"
  value       = "https://${supabase_project.familyprogressweb.id}.supabase.co"
}

output "anon_key" {
  description = "Supabase anon key — set as SUPABASE_ANON_KEY in Vercel"
  value       = data.supabase_apikeys.familyprogressweb.anon_key
  sensitive   = true
}

output "service_role_key" {
  description = "Supabase service role key — for server-side operations only"
  value       = data.supabase_apikeys.familyprogressweb.service_role_key
  sensitive   = true
}

output "db_password" {
  description = "Generated database password"
  value       = random_password.db_password.result
  sensitive   = true
}
